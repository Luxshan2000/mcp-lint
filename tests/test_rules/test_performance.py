from __future__ import annotations

from mcp_lint.models import LintContext, Status
from mcp_lint.rules.performance import (
    InitializeLatency,
    PromptsListLatency,
    ResourcesListLatency,
    ToolsListLatency,
)


class TestInitializeLatency:
    def test_pass(self, valid_context):
        result = InitializeLatency().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_slow(self):
        ctx = LintContext(timings={"initialize": 6.0})
        result = InitializeLatency().run(ctx)
        assert result.status == Status.FAIL

    def test_skip_no_timing(self):
        ctx = LintContext()
        result = InitializeLatency().run(ctx)
        assert result.status == Status.SKIP


class TestToolsListLatency:
    def test_pass(self, valid_context):
        result = ToolsListLatency().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_slow(self):
        ctx = LintContext(timings={"tools_list": 3.0})
        result = ToolsListLatency().run(ctx)
        assert result.status == Status.FAIL

    def test_skip_no_timing(self):
        ctx = LintContext()
        result = ToolsListLatency().run(ctx)
        assert result.status == Status.SKIP


class TestResourcesListLatency:
    def test_pass(self, valid_context):
        result = ResourcesListLatency().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_slow(self):
        ctx = LintContext(
            capabilities={"resources": {}},
            timings={"resources_list": 3.0},
        )
        result = ResourcesListLatency().run(ctx)
        assert result.status == Status.FAIL

    def test_skip_no_capability(self):
        ctx = LintContext(capabilities={}, timings={"resources_list": 0.5})
        result = ResourcesListLatency().run(ctx)
        assert result.status == Status.SKIP

    def test_skip_no_timing(self):
        ctx = LintContext(capabilities={"resources": {}})
        result = ResourcesListLatency().run(ctx)
        assert result.status == Status.SKIP


class TestPromptsListLatency:
    def test_pass(self, valid_context):
        result = PromptsListLatency().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_slow(self):
        ctx = LintContext(
            capabilities={"prompts": {}},
            timings={"prompts_list": 3.0},
        )
        result = PromptsListLatency().run(ctx)
        assert result.status == Status.FAIL

    def test_skip_no_capability(self):
        ctx = LintContext(capabilities={}, timings={"prompts_list": 0.5})
        result = PromptsListLatency().run(ctx)
        assert result.status == Status.SKIP
