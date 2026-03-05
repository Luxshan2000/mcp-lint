from __future__ import annotations

from mcp_lint.models import LintContext, RuleResult
from mcp_lint.rules import get_rules


def run_rules(
    context: LintContext,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[RuleResult]:
    rules = get_rules(include=include, exclude=exclude)
    results = []
    for rule in rules:
        result = rule.run(context)
        results.append(result)
    return results
