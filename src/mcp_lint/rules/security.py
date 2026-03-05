from __future__ import annotations

import re

from mcp_lint.models import Category, LintContext, RuleResult, Severity
from mcp_lint.rules.base import Rule

DANGEROUS_TOOL_NAMES = {
    "execute",
    "exec",
    "run",
    "eval",
    "shell",
    "bash",
    "cmd",
    "system",
    "subprocess",
    "popen",
    "spawn",
}

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?previous", re.IGNORECASE),
    re.compile(r"<\s*system\s*>", re.IGNORECASE),
    re.compile(r"\bdo\s+not\s+follow\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\b", re.IGNORECASE),
    re.compile(r"\boverride\s+instructions\b", re.IGNORECASE),
]

TRACEBACK_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"File \".*\", line \d+"),
    re.compile(r"^\s+at\s+\S+\s+\(.*:\d+:\d+\)", re.MULTILINE),
    re.compile(r"Exception in thread"),
    re.compile(r"stack trace:", re.IGNORECASE),
]

FILE_PATH_PARAM_NAMES = {
    "path",
    "file",
    "filepath",
    "file_path",
    "filename",
    "directory",
    "dir",
    "folder",
}
URL_PARAM_NAMES = {"url", "uri", "endpoint", "href", "link", "target", "address"}


class DangerousToolNames(Rule):
    id = "SEC-001"
    name = "Dangerous tool names"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools with names suggesting dangerous operations"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            name = tool.get("name", "").lower()
            parts = set(re.split(r"[_\-.]", name))
            matches = parts & DANGEROUS_TOOL_NAMES
            if matches:
                flagged.append(f"'{tool.get('name')}' (matches: {', '.join(sorted(matches))})")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} tool(s) have dangerous names",
                details="; ".join(flagged),
            )
        return self.pass_result("No tools with dangerous names found")


class UnrestrictedFilePaths(Rule):
    id = "SEC-002"
    name = "Unrestricted file path parameters"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools with file path params lacking pattern/enum constraints"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                continue
            for param_name, param_schema in properties.items():
                if param_name.lower() not in FILE_PATH_PARAM_NAMES:
                    continue
                if not isinstance(param_schema, dict):
                    continue
                has_pattern = "pattern" in param_schema
                has_enum = "enum" in param_schema
                if not has_pattern and not has_enum:
                    flagged.append(f"'{tool.get('name')}.{param_name}'")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} file path param(s) lack pattern/enum constraints",
                details="; ".join(flagged),
            )
        return self.pass_result("No unrestricted file path parameters found")


class AdditionalPropertiesOpen(Rule):
    id = "SEC-003"
    name = "Open additionalProperties"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools with additionalProperties: true or missing"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            props = schema.get("properties")
            if not isinstance(props, dict) or not props:
                continue  # empty schemas handled by SEC-006
            ap = schema.get("additionalProperties")
            if ap is True or ap is None:
                state = "true" if ap is True else "missing"
                flagged.append(f"'{tool.get('name')}' (additionalProperties: {state})")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} tool(s) allow additional properties",
                details="; ".join(flagged),
            )
        return self.pass_result("All tools restrict additionalProperties")


class PromptInjectionPatterns(Rule):
    id = "SEC-004"
    name = "Prompt injection patterns"
    category = Category.SECURITY
    severity = Severity.ERROR
    description = "Detect prompt injection patterns in tool/resource descriptions"

    def check(self, context: LintContext) -> RuleResult:
        flagged = []
        for tool in context.tools:
            desc = tool.get("description", "")
            for pattern in INJECTION_PATTERNS:
                if pattern.search(desc):
                    flagged.append(f"Tool '{tool.get('name')}': matches '{pattern.pattern}'")
                    break
        for res in context.resources:
            desc = res.get("description", "")
            for pattern in INJECTION_PATTERNS:
                if pattern.search(desc):
                    flagged.append(f"Resource '{res.get('uri')}': matches '{pattern.pattern}'")
                    break
        if not context.tools and not context.resources:
            return self.skip_result("No tools or resources to check")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} description(s) contain prompt injection patterns",
                details="; ".join(flagged),
            )
        return self.pass_result("No prompt injection patterns detected")


class TracebackInErrors(Rule):
    id = "SEC-005"
    name = "Tracebacks in error responses"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools returning tracebacks in error responses"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tool_call_results:
            return self.skip_result("No tool call results to check")
        flagged = []
        for tool_name, result in context.tool_call_results.items():
            text = str(result)
            for pattern in TRACEBACK_PATTERNS:
                if pattern.search(text):
                    flagged.append(f"Tool '{tool_name}' exposes tracebacks")
                    break
        if flagged:
            return self.fail_result(
                f"{len(flagged)} tool(s) expose tracebacks in errors",
                details="; ".join(flagged),
            )
        return self.pass_result("No tracebacks found in tool error responses")


class EmptyInputSchema(Rule):
    id = "SEC-006"
    name = "Empty inputSchema"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools with empty inputSchema (no properties)"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            props = schema.get("properties")
            if not props or (isinstance(props, dict) and len(props) == 0):
                flagged.append(f"'{tool.get('name')}'")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} tool(s) have empty inputSchema",
                details="; ".join(flagged),
            )
        return self.pass_result("All tools have non-empty inputSchema")


class UnrestrictedUrlParams(Rule):
    id = "SEC-007"
    name = "Unrestricted URL parameters"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools accepting URL params without pattern restriction (SSRF)"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                continue
            for param_name, param_schema in properties.items():
                if param_name.lower() not in URL_PARAM_NAMES:
                    continue
                if not isinstance(param_schema, dict):
                    continue
                has_pattern = "pattern" in param_schema
                has_enum = "enum" in param_schema
                if not has_pattern and not has_enum:
                    flagged.append(f"'{tool.get('name')}.{param_name}'")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} URL param(s) lack pattern/enum constraints (SSRF risk)",
                details="; ".join(flagged),
            )
        return self.pass_result("No unrestricted URL parameters found")


class OverlyPermissiveSchema(Rule):
    id = "SEC-008"
    name = "Overly permissive schemas"
    category = Category.SECURITY
    severity = Severity.WARNING
    description = "Flag tools with schemas lacking type constraints on parameters"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to check")
        flagged = []
        for tool in context.tools:
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                continue
            for param_name, param_schema in properties.items():
                if not isinstance(param_schema, dict):
                    continue
                has_type = any(k in param_schema for k in ("type", "$ref", "anyOf", "oneOf"))
                if not has_type:
                    flagged.append(f"'{tool.get('name')}.{param_name}'")
        if flagged:
            return self.fail_result(
                f"{len(flagged)} param(s) lack type constraints",
                details="; ".join(flagged),
            )
        return self.pass_result("All parameters have type constraints")
