from __future__ import annotations

from mcp_lint.models import LintContext, Status
from mcp_lint.rules.schema import (
    ResourceRequiredFields,
    ToolInputSchemaValid,
    ToolNameFormat,
    ToolRequiredFields,
    ToolRequiredInProperties,
)


class TestToolRequiredFields:
    def test_pass(self, valid_context):
        result = ToolRequiredFields().run(valid_context)
        assert result.status == Status.PASS

    def test_skip_no_tools(self, empty_context):
        result = ToolRequiredFields().run(empty_context)
        assert result.status == Status.SKIP

    def test_fail_missing_description(self):
        ctx = LintContext(tools=[{"name": "test", "inputSchema": {}}])
        result = ToolRequiredFields().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_missing_name(self):
        ctx = LintContext(tools=[{"description": "test", "inputSchema": {}}])
        result = ToolRequiredFields().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_missing_schema(self):
        ctx = LintContext(tools=[{"name": "test", "description": "test"}])
        result = ToolRequiredFields().run(ctx)
        assert result.status == Status.FAIL


class TestToolInputSchemaValid:
    def test_pass(self, valid_context):
        result = ToolInputSchemaValid().run(valid_context)
        assert result.status == Status.PASS

    def test_skip_no_tools(self, empty_context):
        result = ToolInputSchemaValid().run(empty_context)
        assert result.status == Status.SKIP

    def test_fail_invalid_schema(self):
        ctx = LintContext(
            tools=[
                {
                    "name": "test",
                    "description": "test",
                    "inputSchema": {"type": "invalid_type"},
                }
            ]
        )
        result = ToolInputSchemaValid().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_not_object(self):
        ctx = LintContext(
            tools=[
                {
                    "name": "test",
                    "description": "test",
                    "inputSchema": "not_a_dict",
                }
            ]
        )
        result = ToolInputSchemaValid().run(ctx)
        assert result.status == Status.FAIL


class TestToolNameFormat:
    def test_pass(self, valid_context):
        result = ToolNameFormat().run(valid_context)
        assert result.status == Status.PASS

    def test_skip_no_tools(self, empty_context):
        result = ToolNameFormat().run(empty_context)
        assert result.status == Status.SKIP

    def test_fail_spaces(self):
        ctx = LintContext(tools=[{"name": "my tool", "description": "t", "inputSchema": {}}])
        result = ToolNameFormat().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_special_chars(self):
        ctx = LintContext(tools=[{"name": "tool@name!", "description": "t", "inputSchema": {}}])
        result = ToolNameFormat().run(ctx)
        assert result.status == Status.FAIL

    def test_pass_dots_and_dashes(self):
        tool = {"name": "my-tool.v2_test", "description": "t", "inputSchema": {}}
        ctx = LintContext(tools=[tool])
        result = ToolNameFormat().run(ctx)
        assert result.status == Status.PASS


class TestToolRequiredInProperties:
    def test_pass(self, valid_context):
        result = ToolRequiredInProperties().run(valid_context)
        assert result.status == Status.PASS

    def test_skip_no_tools(self, empty_context):
        result = ToolRequiredInProperties().run(empty_context)
        assert result.status == Status.SKIP

    def test_fail_missing_required_in_props(self):
        ctx = LintContext(
            tools=[
                {
                    "name": "test",
                    "description": "test",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"a": {"type": "string"}},
                        "required": ["a", "b"],
                    },
                }
            ]
        )
        result = ToolRequiredInProperties().run(ctx)
        assert result.status == Status.FAIL

    def test_pass_all_required_in_props(self):
        ctx = LintContext(
            tools=[
                {
                    "name": "test",
                    "description": "test",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
                        "required": ["a", "b"],
                    },
                }
            ]
        )
        result = ToolRequiredInProperties().run(ctx)
        assert result.status == Status.PASS


class TestResourceRequiredFields:
    def test_pass(self, valid_context):
        result = ResourceRequiredFields().run(valid_context)
        assert result.status == Status.PASS

    def test_skip_no_resources(self, empty_context):
        result = ResourceRequiredFields().run(empty_context)
        assert result.status == Status.SKIP

    def test_fail_missing_uri(self):
        ctx = LintContext(resources=[{"name": "readme"}])
        result = ResourceRequiredFields().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_missing_name(self):
        ctx = LintContext(resources=[{"uri": "file:///test"}])
        result = ResourceRequiredFields().run(ctx)
        assert result.status == Status.FAIL
