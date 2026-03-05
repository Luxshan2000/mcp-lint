from __future__ import annotations

import re

from jsonschema import Draft7Validator

from mcp_lint.models import Category, LintContext, RuleResult, Severity
from mcp_lint.rules.base import Rule

TOOL_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-.]{1,128}$")


class ToolRequiredFields(Rule):
    id = "TOOL-002"
    name = "Tool required fields"
    category = Category.SCHEMA
    severity = Severity.ERROR
    description = "Every tool must have name, description, and inputSchema"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to validate")
        issues = []
        for tool in context.tools:
            name = tool.get("name", "<unnamed>")
            missing = []
            if not tool.get("name"):
                missing.append("name")
            if not tool.get("description"):
                missing.append("description")
            if "inputSchema" not in tool:
                missing.append("inputSchema")
            if missing:
                issues.append(f"Tool '{name}' missing: {', '.join(missing)}")
        if issues:
            return self.fail_result(
                f"{len(issues)} tool(s) have missing required fields",
                details="; ".join(issues),
            )
        return self.pass_result("All tools have required fields")


class ToolInputSchemaValid(Rule):
    id = "TOOL-003"
    name = "Tool inputSchema validity"
    category = Category.SCHEMA
    severity = Severity.ERROR
    description = "Every inputSchema must be valid JSON Schema"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to validate")
        issues = []
        for tool in context.tools:
            name = tool.get("name", "<unnamed>")
            schema = tool.get("inputSchema")
            if schema is None:
                continue  # caught by TOOL-002
            if not isinstance(schema, dict):
                issues.append(f"Tool '{name}': inputSchema is not an object")
                continue
            try:
                Draft7Validator.check_schema(schema)
            except Exception as exc:
                issues.append(f"Tool '{name}': {exc}")
        if issues:
            return self.fail_result(
                f"{len(issues)} tool(s) have invalid inputSchema",
                details="; ".join(issues),
            )
        return self.pass_result("All tool inputSchemas are valid JSON Schema")


class ToolNameFormat(Rule):
    id = "TOOL-004"
    name = "Tool name format"
    category = Category.SCHEMA
    severity = Severity.WARNING
    description = "Tool names must be 1-128 chars, [a-zA-Z0-9_\\-.]"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to validate")
        issues = []
        for tool in context.tools:
            name = tool.get("name", "")
            if not name:
                continue  # caught by TOOL-002
            if not TOOL_NAME_PATTERN.match(name):
                issues.append(f"Tool name '{name}' does not match allowed pattern")
        if issues:
            return self.fail_result(
                f"{len(issues)} tool(s) have invalid names",
                details="; ".join(issues),
            )
        return self.pass_result("All tool names are valid")


class ToolRequiredInProperties(Rule):
    id = "TOOL-005"
    name = "Required fields in properties"
    category = Category.SCHEMA
    severity = Severity.ERROR
    description = "Required array fields must exist in properties"

    def check(self, context: LintContext) -> RuleResult:
        if not context.tools:
            return self.skip_result("No tools to validate")
        issues = []
        for tool in context.tools:
            name = tool.get("name", "<unnamed>")
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict):
                continue
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            if not isinstance(required, list) or not isinstance(properties, dict):
                continue
            missing = [r for r in required if r not in properties]
            if missing:
                issues.append(
                    f"Tool '{name}': required fields not in properties: {', '.join(missing)}"
                )
        if issues:
            return self.fail_result(
                f"{len(issues)} tool(s) have required fields missing from properties",
                details="; ".join(issues),
            )
        return self.pass_result("All required fields exist in properties")


class ResourceRequiredFields(Rule):
    id = "RES-001"
    name = "Resource required fields"
    category = Category.SCHEMA
    severity = Severity.ERROR
    description = "Resources must have uri and name"

    def check(self, context: LintContext) -> RuleResult:
        if not context.resources:
            return self.skip_result("No resources to validate")
        issues = []
        for res in context.resources:
            missing = []
            if not res.get("uri"):
                missing.append("uri")
            if not res.get("name"):
                missing.append("name")
            if missing:
                uri = res.get("uri", "<no-uri>")
                issues.append(f"Resource '{uri}' missing: {', '.join(missing)}")
        if issues:
            return self.fail_result(
                f"{len(issues)} resource(s) have missing required fields",
                details="; ".join(issues),
            )
        return self.pass_result("All resources have required fields")
