from __future__ import annotations

from mcp_lint.models import LintContext, Status
from mcp_lint.rules.protocol import (
    InitCapabilities,
    InitCapabilityConsistency,
    InitProtocolVersion,
    InitServerInfo,
    ToolListValid,
    UnknownMethodError,
)


class TestInitProtocolVersion:
    def test_pass_valid_format(self, valid_context):
        result = InitProtocolVersion().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_invalid_format(self):
        ctx = LintContext(protocol_version="1.0.0")
        result = InitProtocolVersion().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_empty(self):
        ctx = LintContext(protocol_version="")
        result = InitProtocolVersion().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_partial_date(self):
        ctx = LintContext(protocol_version="2024-11")
        result = InitProtocolVersion().run(ctx)
        assert result.status == Status.FAIL


class TestInitServerInfo:
    def test_pass_complete(self, valid_context):
        result = InitServerInfo().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_missing_name(self):
        ctx = LintContext(server_name="", server_version="1.0.0")
        result = InitServerInfo().run(ctx)
        assert result.status == Status.FAIL
        assert "name" in result.message

    def test_fail_missing_version(self):
        ctx = LintContext(server_name="test", server_version="")
        result = InitServerInfo().run(ctx)
        assert result.status == Status.FAIL
        assert "version" in result.message

    def test_fail_missing_both(self):
        ctx = LintContext()
        result = InitServerInfo().run(ctx)
        assert result.status == Status.FAIL


class TestInitCapabilities:
    def test_pass_known_keys(self, valid_context):
        result = InitCapabilities().run(valid_context)
        assert result.status == Status.PASS

    def test_pass_empty(self):
        ctx = LintContext(capabilities={})
        result = InitCapabilities().run(ctx)
        assert result.status == Status.PASS

    def test_warn_unknown_keys(self):
        ctx = LintContext(capabilities={"tools": {}, "custom_thing": {}})
        result = InitCapabilities().run(ctx)
        assert result.status == Status.WARN

    def test_fail_not_dict(self):
        ctx = LintContext(capabilities="invalid")  # type: ignore[arg-type]
        result = InitCapabilities().run(ctx)
        assert result.status == Status.FAIL


class TestInitCapabilityConsistency:
    def test_pass_consistent(self, valid_context):
        result = InitCapabilityConsistency().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_tools_without_capability(self):
        ctx = LintContext(
            capabilities={},
            tools=[{"name": "test", "description": "t", "inputSchema": {}}],
        )
        result = InitCapabilityConsistency().run(ctx)
        assert result.status == Status.FAIL

    def test_fail_capability_without_tools(self):
        ctx = LintContext(capabilities={"tools": {}}, tools=[])
        result = InitCapabilityConsistency().run(ctx)
        assert result.status == Status.FAIL

    def test_pass_empty(self, empty_context):
        result = InitCapabilityConsistency().run(empty_context)
        assert result.status == Status.PASS


class TestToolListValid:
    def test_pass(self, valid_context):
        result = ToolListValid().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_error(self):
        ctx = LintContext(errors={"tools": "Connection refused"})
        result = ToolListValid().run(ctx)
        assert result.status == Status.FAIL

    def test_pass_empty_list(self):
        ctx = LintContext(tools=[])
        result = ToolListValid().run(ctx)
        assert result.status == Status.PASS


class TestUnknownMethodError:
    def test_pass_correct_code(self, valid_context):
        result = UnknownMethodError().run(valid_context)
        assert result.status == Status.PASS

    def test_fail_wrong_code(self):
        ctx = LintContext(unknown_method_error={"code": -32600, "message": "Invalid"})
        result = UnknownMethodError().run(ctx)
        assert result.status == Status.FAIL

    def test_skip_not_tested(self):
        ctx = LintContext()
        result = UnknownMethodError().run(ctx)
        assert result.status == Status.SKIP
