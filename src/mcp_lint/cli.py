from __future__ import annotations

import asyncio
from enum import Enum
from typing import Optional

import typer
from rich.console import Console

from mcp_lint import __version__
from mcp_lint.client import collect_context_sse, collect_context_stdio
from mcp_lint.report import format_json, format_markdown, format_terminal
from mcp_lint.runner import run_rules
from mcp_lint.scorer import build_report

app = typer.Typer(
    name="mcp-lint",
    help="Lint and validate MCP servers for protocol compliance, security, and performance.",
    add_completion=False,
    no_args_is_help=True,
)

stderr = Console(stderr=True)


class OutputFormat(str, Enum):
    terminal = "terminal"
    json = "json"
    markdown = "markdown"


def version_callback(value: bool) -> None:
    if value:
        print(f"mcp-lint {__version__}")
        raise typer.Exit()


@app.command()
def lint(
    command: Optional[str] = typer.Argument(
        None,
        help="MCP server command to run (stdio transport)",
    ),
    url: Optional[str] = typer.Option(
        None,
        "--url",
        help="MCP server SSE URL",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.terminal,
        "--format",
        "-f",
        help="Output format",
    ),
    fail_under: float = typer.Option(
        0,
        "--fail-under",
        help="Exit with code 1 if score is below this threshold",
    ),
    timeout: float = typer.Option(
        30,
        "--timeout",
        help="Global timeout in seconds",
    ),
    include: Optional[str] = typer.Option(
        None,
        "--include",
        help="Comma-separated rule IDs to include",
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude",
        help="Comma-separated rule IDs to exclude",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Lint an MCP server for protocol compliance, schema, security, and performance."""
    if not command and not url:
        stderr.print("[red]Error:[/red] Provide a command argument or --url option")
        raise typer.Exit(2)

    if command and url:
        stderr.print("[red]Error:[/red] Provide either a command or --url, not both")
        raise typer.Exit(2)

    include_list = [x.strip() for x in include.split(",")] if include else None
    exclude_list = [x.strip() for x in exclude.split(",")] if exclude else None

    # Collect context from server
    stderr.print("[cyan]Connecting to MCP server...[/cyan]")
    try:
        if command:
            context = asyncio.run(collect_context_stdio(command, timeout=timeout))
            transport = "stdio"
        else:
            context = asyncio.run(collect_context_sse(url, timeout=timeout))  # type: ignore[arg-type]
            transport = "sse"
    except Exception as exc:
        stderr.print(f"[red]Connection failed:[/red] {exc}")
        raise typer.Exit(2)

    if "initialize" in context.errors:
        stderr.print(f"[red]Server initialization failed:[/red] {context.errors['initialize']}")
        raise typer.Exit(2)

    stderr.print(
        f"[green]Connected:[/green] {context.server_name} v{context.server_version} "
        f"(protocol {context.protocol_version})"
    )

    # Run rules
    results = run_rules(context, include=include_list, exclude=exclude_list)

    # Build scored report
    report = build_report(context, results, transport)

    # Output
    if format == OutputFormat.terminal:
        format_terminal(report, verbose=verbose)
    elif format == OutputFormat.json:
        print(format_json(report))
    elif format == OutputFormat.markdown:
        print(format_markdown(report))

    # Exit code
    if report.score < fail_under:
        raise typer.Exit(1)


def app_main() -> None:
    app()
