from __future__ import annotations

import time
from abc import ABC, abstractmethod

from mcp_lint.models import Category, LintContext, RuleResult, Severity, Status


class Rule(ABC):
    id: str = ""
    name: str = ""
    category: Category = Category.PROTOCOL
    severity: Severity = Severity.ERROR
    description: str = ""

    def run(self, context: LintContext) -> RuleResult:
        start = time.perf_counter()
        try:
            result = self.check(context)
        except Exception as exc:
            result = RuleResult(
                rule_id=self.id,
                rule_name=self.name,
                category=self.category,
                severity=self.severity,
                status=Status.ERROR,
                message=f"Rule execution error: {exc}",
            )
        elapsed_ms = (time.perf_counter() - start) * 1000
        result.duration_ms = elapsed_ms
        return result

    @abstractmethod
    def check(self, context: LintContext) -> RuleResult: ...

    def pass_result(self, message: str, details: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            category=self.category,
            severity=self.severity,
            status=Status.PASS,
            message=message,
            details=details,
        )

    def fail_result(self, message: str, details: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            category=self.category,
            severity=self.severity,
            status=Status.FAIL,
            message=message,
            details=details,
        )

    def warn_result(self, message: str, details: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            category=self.category,
            severity=self.severity,
            status=Status.WARN,
            message=message,
            details=details,
        )

    def skip_result(self, message: str, details: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            category=self.category,
            severity=self.severity,
            status=Status.SKIP,
            message=message,
            details=details,
        )
