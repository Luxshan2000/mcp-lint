from __future__ import annotations

import asyncio
import shlex
import time
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from mcp_lint.models import LintContext


async def collect_context_stdio(
    command: str,
    timeout: float = 30.0,
) -> LintContext:
    parts = shlex.split(command)
    server_params = StdioServerParameters(
        command=parts[0],
        args=parts[1:] if len(parts) > 1 else [],
    )

    async with AsyncExitStack() as stack:
        transport = await stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = transport
        return await _do_collection(stack, read_stream, write_stream, timeout)


async def collect_context_sse(
    url: str,
    timeout: float = 30.0,
) -> LintContext:
    async with AsyncExitStack() as stack:
        transport = await stack.enter_async_context(sse_client(url))
        read_stream, write_stream = transport
        return await _do_collection(stack, read_stream, write_stream, timeout)


async def _do_collection(
    stack: AsyncExitStack,
    read_stream,
    write_stream,
    timeout: float,
) -> LintContext:
    ctx = LintContext()

    async def _collect() -> None:
        session = await stack.enter_async_context(ClientSession(read_stream, write_stream))

        # Initialize
        t0 = time.perf_counter()
        try:
            init_result = await session.initialize()
            ctx.timings["initialize"] = time.perf_counter() - t0

            result_dict = init_result.model_dump(by_alias=True)
            ctx.init_result = result_dict
            ctx.protocol_version = result_dict.get("protocolVersion", "")
            server_info = result_dict.get("serverInfo", {})
            ctx.server_name = server_info.get("name", "")
            ctx.server_version = server_info.get("version", "")
            ctx.capabilities = result_dict.get("capabilities", {})
        except Exception as exc:
            ctx.timings["initialize"] = time.perf_counter() - t0
            ctx.errors["initialize"] = str(exc)
            return

        # List tools (always)
        t0 = time.perf_counter()
        try:
            tools_result = await session.list_tools()
            ctx.timings["tools_list"] = time.perf_counter() - t0
            ctx.tools = [t.model_dump(by_alias=True) for t in tools_result.tools]
        except Exception as exc:
            ctx.timings["tools_list"] = time.perf_counter() - t0
            ctx.errors["tools"] = str(exc)

        # List resources (if capability declared)
        if "resources" in ctx.capabilities:
            t0 = time.perf_counter()
            try:
                resources_result = await session.list_resources()
                ctx.timings["resources_list"] = time.perf_counter() - t0
                ctx.resources = [r.model_dump(by_alias=True) for r in resources_result.resources]
            except Exception as exc:
                ctx.timings["resources_list"] = time.perf_counter() - t0
                ctx.errors["resources"] = str(exc)

        # List prompts (if capability declared)
        if "prompts" in ctx.capabilities:
            t0 = time.perf_counter()
            try:
                prompts_result = await session.list_prompts()
                ctx.timings["prompts_list"] = time.perf_counter() - t0
                ctx.prompts = [p.model_dump(by_alias=True) for p in prompts_result.prompts]
            except Exception as exc:
                ctx.timings["prompts_list"] = time.perf_counter() - t0
                ctx.errors["prompts"] = str(exc)

        # Test unknown method (for ERR-001)
        try:
            await session.send_request("nonexistent/method", {})
            ctx.unknown_method_error = {"code": None, "message": "No error returned"}
        except Exception as exc:
            error_code = getattr(exc, "code", None)
            error_msg = str(exc)
            ctx.unknown_method_error = {"code": error_code, "message": error_msg}

        # Test tool error responses (for SEC-005) — first 5 tools
        for tool in ctx.tools[:5]:
            tool_name = tool.get("name", "")
            if not tool_name:
                continue
            try:
                result = await session.call_tool(tool_name, arguments={})
                ctx.tool_call_results[tool_name] = result.model_dump(by_alias=True)
            except Exception as exc:
                ctx.tool_call_results[tool_name] = {"error": str(exc)}

    try:
        await asyncio.wait_for(_collect(), timeout=timeout)
    except asyncio.TimeoutError:
        ctx.errors["timeout"] = f"Collection timed out after {timeout}s"

    return ctx
