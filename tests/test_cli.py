from __future__ import annotations

import json
from unittest.mock import patch

from typer.testing import CliRunner

from mcp_lint import __version__
from mcp_lint.cli import app
from mcp_lint.models import LintContext

runner = CliRunner()


def _mock_context() -> LintContext:
    return LintContext(
        protocol_version="2024-11-05",
        server_name="mock-server",
        server_version="1.0.0",
        capabilities={"tools": {}},
        tools=[
            {
                "name": "test_tool",
                "description": "A test tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {"q": {"type": "string"}},
                    "required": ["q"],
                    "additionalProperties": False,
                },
            }
        ],
        timings={"initialize": 0.5, "tools_list": 0.3},
        unknown_method_error={"code": -32601, "message": "Method not found"},
    )


def _failing_context() -> LintContext:
    """Context that will fail some rules (score < 100)."""
    return LintContext(
        protocol_version="bad-version",
        server_name="",
        server_version="",
        capabilities={"tools": {}},
        tools=[
            {
                "name": "execute_command",
                "description": "Run a shell command",
                "inputSchema": {
                    "type": "object",
                    "properties": {"cmd": {"type": "string"}},
                    "additionalProperties": True,
                },
            }
        ],
        timings={"initialize": 0.5, "tools_list": 0.3},
    )


def _extract_json(output: str) -> dict:
    """Extract JSON object from output that may contain stderr lines."""
    start = output.index("{")
    # Find matching closing brace
    depth = 0
    for i, c in enumerate(output[start:], start):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(output[start : i + 1])
    raise ValueError("No valid JSON found in output")


class TestVersionFlag:
    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestNoArgs:
    def test_no_args_exits_with_error(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 2


class TestBothTransports:
    def test_both_command_and_url(self):
        result = runner.invoke(app, ["some-cmd", "--url", "http://localhost"])
        assert result.exit_code == 2


class TestLintCommand:
    @patch("mcp_lint.cli.collect_context_stdio")
    def test_stdio_json_output(self, mock_collect):
        mock_collect.return_value = _mock_context()
        result = runner.invoke(app, ["echo test", "--format", "json"])
        assert result.exit_code == 0
        data = _extract_json(result.output)
        assert "score" in data
        assert "grade" in data

    @patch("mcp_lint.cli.collect_context_stdio")
    def test_stdio_markdown_output(self, mock_collect):
        mock_collect.return_value = _mock_context()
        result = runner.invoke(app, ["echo test", "--format", "markdown"])
        assert result.exit_code == 0
        assert "# mcp-lint Report:" in result.output

    @patch("mcp_lint.cli.collect_context_stdio")
    def test_fail_under(self, mock_collect):
        mock_collect.return_value = _failing_context()
        result = runner.invoke(app, ["echo test", "--format", "json", "--fail-under", "90"])
        assert result.exit_code == 1

    @patch("mcp_lint.cli.collect_context_stdio")
    def test_include_rules(self, mock_collect):
        mock_collect.return_value = _mock_context()
        result = runner.invoke(
            app,
            [
                "echo test",
                "--format",
                "json",
                "--include",
                "INIT-001,INIT-002",
            ],
        )
        assert result.exit_code == 0
        data = _extract_json(result.output)
        rule_ids = {r["ruleId"] for r in data["results"]}
        assert rule_ids == {"INIT-001", "INIT-002"}

    @patch("mcp_lint.cli.collect_context_stdio")
    def test_exclude_rules(self, mock_collect):
        mock_collect.return_value = _mock_context()
        result = runner.invoke(
            app,
            [
                "echo test",
                "--format",
                "json",
                "--exclude",
                "INIT-001",
            ],
        )
        assert result.exit_code == 0
        data = _extract_json(result.output)
        rule_ids = {r["ruleId"] for r in data["results"]}
        assert "INIT-001" not in rule_ids

    @patch("mcp_lint.cli.collect_context_stdio")
    def test_connection_failure(self, mock_collect):
        mock_collect.side_effect = ConnectionError("Failed to connect")
        result = runner.invoke(app, ["bad-command"])
        assert result.exit_code == 2
