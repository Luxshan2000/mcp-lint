from __future__ import annotations

from mcp_lint.rules.base import Rule
from mcp_lint.rules.performance import (
    InitializeLatency,
    PromptsListLatency,
    ResourcesListLatency,
    ToolsListLatency,
)
from mcp_lint.rules.protocol import (
    InitCapabilities,
    InitCapabilityConsistency,
    InitProtocolVersion,
    InitServerInfo,
    ToolListValid,
    UnknownMethodError,
)
from mcp_lint.rules.schema import (
    ResourceRequiredFields,
    ToolInputSchemaValid,
    ToolNameFormat,
    ToolRequiredFields,
    ToolRequiredInProperties,
)
from mcp_lint.rules.security import (
    AdditionalPropertiesOpen,
    DangerousToolNames,
    EmptyInputSchema,
    OverlyPermissiveSchema,
    PromptInjectionPatterns,
    TracebackInErrors,
    UnrestrictedFilePaths,
    UnrestrictedUrlParams,
)

ALL_RULES: list[Rule] = [
    # Protocol
    InitProtocolVersion(),
    InitServerInfo(),
    InitCapabilities(),
    InitCapabilityConsistency(),
    ToolListValid(),
    UnknownMethodError(),
    # Schema
    ToolRequiredFields(),
    ToolInputSchemaValid(),
    ToolNameFormat(),
    ToolRequiredInProperties(),
    ResourceRequiredFields(),
    # Security
    DangerousToolNames(),
    UnrestrictedFilePaths(),
    AdditionalPropertiesOpen(),
    PromptInjectionPatterns(),
    TracebackInErrors(),
    EmptyInputSchema(),
    UnrestrictedUrlParams(),
    OverlyPermissiveSchema(),
    # Performance
    InitializeLatency(),
    ToolsListLatency(),
    ResourcesListLatency(),
    PromptsListLatency(),
]

RULE_MAP: dict[str, Rule] = {rule.id: rule for rule in ALL_RULES}


def get_rules(
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Rule]:
    rules = ALL_RULES
    if include:
        include_set = set(include)
        rules = [r for r in rules if r.id in include_set]
    if exclude:
        exclude_set = set(exclude)
        rules = [r for r in rules if r.id not in exclude_set]
    return rules
