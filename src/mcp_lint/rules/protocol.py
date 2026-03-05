from __future__ import annotations

import re

from mcp_lint.models import Category, LintContext, RuleResult, Severity
from mcp_lint.rules.base import Rule

KNOWN_CAPABILITY_KEYS = {
    "tools",
    "resources",
    "prompts",
    "logging",
    "experimental",
    "completions",
    "roots",
}


class InitProtocolVersion(Rule):
    id = "INIT-001"
    name = "Protocol version format"
    category = Category.PROTOCOL
    severity = Severity.ERROR
    description = "protocolVersion must be in YYYY-MM-DD format"

    def check(self, context: LintContext) -> RuleResult:
        version = context.protocol_version
        if not version:
            return self.fail_result("No protocolVersion returned by server")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", version):
            return self.pass_result(f"protocolVersion '{version}' is valid")
        return self.fail_result(f"protocolVersion '{version}' is not in YYYY-MM-DD format")


class InitServerInfo(Rule):
    id = "INIT-002"
    name = "Server info completeness"
    category = Category.PROTOCOL
    severity = Severity.ERROR
    description = "serverInfo must include name and version"

    def check(self, context: LintContext) -> RuleResult:
        missing = []
        if not context.server_name:
            missing.append("name")
        if not context.server_version:
            missing.append("version")
        if missing:
            return self.fail_result(f"serverInfo missing: {', '.join(missing)}")
        return self.pass_result(
            f"serverInfo complete: {context.server_name} v{context.server_version}"
        )


class InitCapabilities(Rule):
    id = "INIT-003"
    name = "Capabilities validity"
    category = Category.PROTOCOL
    severity = Severity.ERROR
    description = "capabilities must be a valid object with known keys"

    def check(self, context: LintContext) -> RuleResult:
        caps = context.capabilities
        if not isinstance(caps, dict):
            return self.fail_result("capabilities is not an object")
        unknown = set(caps.keys()) - KNOWN_CAPABILITY_KEYS
        if unknown:
            return self.warn_result(
                f"Unknown capability keys: {', '.join(sorted(unknown))}",
                details="These may be valid extensions but are not part of the core spec",
            )
        return self.pass_result("capabilities object is valid")


class InitCapabilityConsistency(Rule):
    id = "INIT-004"
    name = "Capability consistency"
    category = Category.PROTOCOL
    severity = Severity.WARNING
    description = "Declared capabilities should match actual behavior"

    def check(self, context: LintContext) -> RuleResult:
        issues = []
        caps = context.capabilities

        has_tools_cap = "tools" in caps
        has_tools = len(context.tools) > 0
        if has_tools and not has_tools_cap:
            issues.append("Server serves tools but does not declare tools capability")
        if has_tools_cap and not has_tools and "tools" not in context.errors:
            issues.append("Server declares tools capability but returned no tools")

        has_resources_cap = "resources" in caps
        has_resources = len(context.resources) > 0
        if has_resources and not has_resources_cap:
            issues.append("Server serves resources but does not declare resources capability")

        has_prompts_cap = "prompts" in caps
        has_prompts = len(context.prompts) > 0
        if has_prompts and not has_prompts_cap:
            issues.append("Server serves prompts but does not declare prompts capability")

        if issues:
            return self.fail_result(
                "Capability mismatch detected",
                details="; ".join(issues),
            )
        return self.pass_result("Declared capabilities match actual behavior")


class ToolListValid(Rule):
    id = "TOOL-001"
    name = "tools/list response"
    category = Category.PROTOCOL
    severity = Severity.ERROR
    description = "tools/list must return a valid list response"

    def check(self, context: LintContext) -> RuleResult:
        if "tools" in context.errors:
            return self.fail_result(
                "tools/list failed",
                details=context.errors["tools"],
            )
        if not isinstance(context.tools, list):
            return self.fail_result("tools/list did not return a list")
        return self.pass_result(f"tools/list returned {len(context.tools)} tools")


class UnknownMethodError(Rule):
    id = "ERR-001"
    name = "Unknown method error code"
    category = Category.PROTOCOL
    severity = Severity.WARNING
    description = "Server should return -32601 for unknown methods"

    def check(self, context: LintContext) -> RuleResult:
        err = context.unknown_method_error
        if err is None:
            return self.skip_result("Unknown method test was not performed")
        code = err.get("code")
        if code == -32601:
            return self.pass_result("Server correctly returns -32601 for unknown methods")
        return self.fail_result(
            f"Server returned code {code} instead of -32601 for unknown method",
            details=str(err),
        )
