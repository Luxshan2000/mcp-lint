from __future__ import annotations

import json

from mcp_lint.models import (
    Category,
    Grade,
    RuleResult,
    ScoredReport,
    Severity,
    Status,
)
from mcp_lint.report import format_json, format_markdown, format_terminal


def _sample_report() -> ScoredReport:
    return ScoredReport(
        server_name="test-server",
        server_version="1.0.0",
        protocol_version="2024-11-05",
        transport="stdio",
        results=[
            RuleResult(
                rule_id="INIT-001",
                rule_name="Protocol version format",
                category=Category.PROTOCOL,
                severity=Severity.ERROR,
                status=Status.PASS,
                message="protocolVersion '2024-11-05' is valid",
                duration_ms=0.1,
            ),
            RuleResult(
                rule_id="SEC-001",
                rule_name="Dangerous tool names",
                category=Category.SECURITY,
                severity=Severity.WARNING,
                status=Status.FAIL,
                message="1 tool(s) have dangerous names",
                details="'execute_command' (matches: execute)",
                duration_ms=0.05,
            ),
        ],
        score=50.0,
        grade=Grade.F,
        total=2,
        passed=1,
        failed=1,
        warnings=0,
        skipped=0,
        errors=0,
    )


class TestFormatJson:
    def test_valid_json(self):
        report = _sample_report()
        output = format_json(report)
        data = json.loads(output)
        assert data["score"] == 50.0
        assert data["grade"] == "F"
        assert data["server"]["name"] == "test-server"
        assert len(data["results"]) == 2

    def test_summary_counts(self):
        report = _sample_report()
        data = json.loads(format_json(report))
        assert data["summary"]["total"] == 2
        assert data["summary"]["passed"] == 1
        assert data["summary"]["failed"] == 1


class TestFormatMarkdown:
    def test_well_formed(self):
        report = _sample_report()
        output = format_markdown(report)
        assert "# mcp-lint Report:" in output
        assert "| Status |" in output
        assert "## Protocol" in output
        assert "## Security" in output
        assert "## Summary" in output

    def test_contains_score(self):
        report = _sample_report()
        output = format_markdown(report)
        assert "50%" in output
        assert "Grade:** F" in output


class TestFormatTerminal:
    def test_no_exception(self):
        report = _sample_report()
        # Should not raise
        format_terminal(report, verbose=False)

    def test_verbose_no_exception(self):
        report = _sample_report()
        format_terminal(report, verbose=True)
