from __future__ import annotations

from mcp_lint.models import Grade, LintContext, RuleResult, ScoredReport, Status

_STATUS_SCORE = {
    Status.PASS: 1.0,
    Status.FAIL: 0.0,
    Status.WARN: 0.5,
    Status.ERROR: 0.0,
}


def calculate_score(results: list[RuleResult]) -> float:
    scored = [r for r in results if r.status != Status.SKIP]
    if not scored:
        return 100.0
    total = sum(_STATUS_SCORE.get(r.status, 0.0) for r in scored)
    return (total / len(scored)) * 100


def calculate_grade(score: float) -> Grade:
    if score >= 90:
        return Grade.A
    if score >= 80:
        return Grade.B
    if score >= 70:
        return Grade.C
    if score >= 60:
        return Grade.D
    return Grade.F


def build_report(
    context: LintContext,
    results: list[RuleResult],
    transport: str,
) -> ScoredReport:
    score = calculate_score(results)
    grade = calculate_grade(score)
    return ScoredReport(
        server_name=context.server_name,
        server_version=context.server_version,
        protocol_version=context.protocol_version,
        transport=transport,
        results=results,
        score=score,
        grade=grade,
        total=len(results),
        passed=sum(1 for r in results if r.status == Status.PASS),
        failed=sum(1 for r in results if r.status == Status.FAIL),
        warnings=sum(1 for r in results if r.status == Status.WARN),
        skipped=sum(1 for r in results if r.status == Status.SKIP),
        errors=sum(1 for r in results if r.status == Status.ERROR),
    )
