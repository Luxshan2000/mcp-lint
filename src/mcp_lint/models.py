from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    PROTOCOL = "Protocol"
    SCHEMA = "Schema"
    SECURITY = "Security"
    PERFORMANCE = "Performance"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Status(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"
    ERROR = "error"


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    category: Category
    severity: Severity
    status: Status
    message: str
    details: str = ""
    duration_ms: float = 0.0


@dataclass
class LintContext:
    init_result: dict = field(default_factory=dict)
    protocol_version: str = ""
    server_name: str = ""
    server_version: str = ""
    capabilities: dict = field(default_factory=dict)
    tools: list[dict] = field(default_factory=list)
    resources: list[dict] = field(default_factory=list)
    prompts: list[dict] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    tool_call_results: dict = field(default_factory=dict)
    unknown_method_error: dict | None = None


@dataclass
class ScoredReport:
    server_name: str = ""
    server_version: str = ""
    protocol_version: str = ""
    transport: str = ""
    results: list[RuleResult] = field(default_factory=list)
    score: float = 0.0
    grade: Grade = Grade.F
    total: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0
    errors: int = 0
