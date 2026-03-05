from __future__ import annotations

from mcp_lint.models import Category, LintContext, RuleResult, Severity
from mcp_lint.rules.base import Rule


class InitializeLatency(Rule):
    id = "PERF-001"
    name = "Initialize latency"
    category = Category.PERFORMANCE
    severity = Severity.WARNING
    description = "initialize should complete in under 5 seconds"

    def check(self, context: LintContext) -> RuleResult:
        t = context.timings.get("initialize")
        if t is None:
            return self.skip_result("Initialize timing not available")
        if t > 5.0:
            return self.fail_result(f"initialize took {t:.2f}s (threshold: 5.0s)")
        return self.pass_result(f"initialize completed in {t:.2f}s")


class ToolsListLatency(Rule):
    id = "PERF-002"
    name = "tools/list latency"
    category = Category.PERFORMANCE
    severity = Severity.WARNING
    description = "tools/list should complete in under 2 seconds"

    def check(self, context: LintContext) -> RuleResult:
        t = context.timings.get("tools_list")
        if t is None:
            return self.skip_result("tools/list timing not available")
        if t > 2.0:
            return self.fail_result(f"tools/list took {t:.2f}s (threshold: 2.0s)")
        return self.pass_result(f"tools/list completed in {t:.2f}s")


class ResourcesListLatency(Rule):
    id = "PERF-003"
    name = "resources/list latency"
    category = Category.PERFORMANCE
    severity = Severity.WARNING
    description = "resources/list should complete in under 2 seconds"

    def check(self, context: LintContext) -> RuleResult:
        if "resources" not in context.capabilities:
            return self.skip_result("Server does not declare resources capability")
        t = context.timings.get("resources_list")
        if t is None:
            return self.skip_result("resources/list timing not available")
        if t > 2.0:
            return self.fail_result(f"resources/list took {t:.2f}s (threshold: 2.0s)")
        return self.pass_result(f"resources/list completed in {t:.2f}s")


class PromptsListLatency(Rule):
    id = "PERF-004"
    name = "prompts/list latency"
    category = Category.PERFORMANCE
    severity = Severity.WARNING
    description = "prompts/list should complete in under 2 seconds"

    def check(self, context: LintContext) -> RuleResult:
        if "prompts" not in context.capabilities:
            return self.skip_result("Server does not declare prompts capability")
        t = context.timings.get("prompts_list")
        if t is None:
            return self.skip_result("prompts/list timing not available")
        if t > 2.0:
            return self.fail_result(f"prompts/list took {t:.2f}s (threshold: 2.0s)")
        return self.pass_result(f"prompts/list completed in {t:.2f}s")
