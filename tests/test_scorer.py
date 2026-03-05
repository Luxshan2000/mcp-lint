from __future__ import annotations

from mcp_lint.models import (
    Category,
    Grade,
    LintContext,
    RuleResult,
    Severity,
    Status,
)
from mcp_lint.scorer import build_report, calculate_grade, calculate_score


def _make_result(status: Status) -> RuleResult:
    return RuleResult(
        rule_id="TEST-001",
        rule_name="Test rule",
        category=Category.PROTOCOL,
        severity=Severity.ERROR,
        status=status,
        message="test",
    )


class TestCalculateScore:
    def test_all_pass(self):
        results = [_make_result(Status.PASS)] * 5
        assert calculate_score(results) == 100.0

    def test_all_fail(self):
        results = [_make_result(Status.FAIL)] * 5
        assert calculate_score(results) == 0.0

    def test_mixed(self):
        results = [_make_result(Status.PASS), _make_result(Status.FAIL)]
        assert calculate_score(results) == 50.0

    def test_with_warn(self):
        results = [_make_result(Status.PASS), _make_result(Status.WARN)]
        assert calculate_score(results) == 75.0

    def test_skip_excluded(self):
        results = [
            _make_result(Status.PASS),
            _make_result(Status.SKIP),
        ]
        assert calculate_score(results) == 100.0

    def test_all_skip(self):
        results = [_make_result(Status.SKIP)] * 3
        assert calculate_score(results) == 100.0

    def test_empty(self):
        assert calculate_score([]) == 100.0

    def test_error_counts_as_zero(self):
        results = [_make_result(Status.PASS), _make_result(Status.ERROR)]
        assert calculate_score(results) == 50.0


class TestCalculateGrade:
    def test_a(self):
        assert calculate_grade(95) == Grade.A
        assert calculate_grade(90) == Grade.A

    def test_b(self):
        assert calculate_grade(85) == Grade.B
        assert calculate_grade(80) == Grade.B

    def test_c(self):
        assert calculate_grade(75) == Grade.C
        assert calculate_grade(70) == Grade.C

    def test_d(self):
        assert calculate_grade(65) == Grade.D
        assert calculate_grade(60) == Grade.D

    def test_f(self):
        assert calculate_grade(59) == Grade.F
        assert calculate_grade(0) == Grade.F


class TestBuildReport:
    def test_counts(self):
        results = [
            _make_result(Status.PASS),
            _make_result(Status.PASS),
            _make_result(Status.FAIL),
            _make_result(Status.WARN),
            _make_result(Status.SKIP),
            _make_result(Status.ERROR),
        ]
        ctx = LintContext(
            server_name="test",
            server_version="1.0",
            protocol_version="2024-11-05",
        )
        report = build_report(ctx, results, "stdio")
        assert report.total == 6
        assert report.passed == 2
        assert report.failed == 1
        assert report.warnings == 1
        assert report.skipped == 1
        assert report.errors == 1
        assert report.server_name == "test"
        assert report.transport == "stdio"
