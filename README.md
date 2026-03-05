<p align="center">
  <h1 align="center">mcp-lint</h1>
  <p align="center">A production-quality linter for MCP (Model Context Protocol) servers</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/mcp-lint/"><img src="https://img.shields.io/pypi/v/mcp-lint?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/mcp-lint/"><img src="https://img.shields.io/pypi/pyversions/mcp-lint?logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/Luxshan2000/mcp-lint/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Luxshan2000/mcp-lint/ci.yml?label=CI&logo=github" alt="CI"></a>
  <a href="https://github.com/Luxshan2000/mcp-lint/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/mcp-lint?color=green" alt="License"></a>
  <a href="https://pypi.org/project/mcp-lint/"><img src="https://img.shields.io/pypi/dm/mcp-lint?color=orange&logo=pypi&logoColor=white" alt="Downloads"></a>
</p>

---

**mcp-lint** connects to any MCP server via stdio or SSE transport, runs **23 deterministic lint rules** across 4 categories, and outputs a scored report with CI/CD-friendly exit codes.

No LLM required. No API keys. Pure static analysis of your MCP server's protocol behavior.

## Features

- **23 lint rules** across 4 categories: Protocol, Schema, Security, Performance
- **Multiple transports** — stdio and SSE support
- **CI/CD ready** — `--fail-under` flag with exit codes (0 = pass, 1 = below threshold, 2 = error)
- **3 output formats** — terminal (Rich), JSON, Markdown
- **Rule filtering** — `--include` / `--exclude` specific rules
- **Zero configuration** — works out of the box with sensible defaults

## Installation

```bash
pip install mcp-lint
```

## Quick Start

```bash
# Lint an MCP server via stdio
mcp-lint "python -m your_mcp_server"

# Lint via SSE
mcp-lint --url http://localhost:8000/sse

# JSON output for CI pipelines
mcp-lint "python -m your_mcp_server" --format json

# Fail CI if score drops below 80%
mcp-lint "python -m your_mcp_server" --fail-under 80

# Verbose output with details
mcp-lint "python -m your_mcp_server" -v
```

## Lint Rules

### Protocol (6 rules)

| Rule | Description | Severity |
|------|-------------|----------|
| `INIT-001` | `protocolVersion` is in YYYY-MM-DD format | Error |
| `INIT-002` | `serverInfo` has name and version | Error |
| `INIT-003` | `capabilities` is a valid object with known keys | Error |
| `INIT-004` | Declared capabilities match actual behavior | Warning |
| `TOOL-001` | `tools/list` returns a valid list response | Error |
| `ERR-001` | Server returns `-32601` for unknown methods | Warning |

### Schema (5 rules)

| Rule | Description | Severity |
|------|-------------|----------|
| `TOOL-002` | Every tool has name, description, and inputSchema | Error |
| `TOOL-003` | Every inputSchema is valid JSON Schema | Error |
| `TOOL-004` | Tool names match `[a-zA-Z0-9_\-.]` (1-128 chars) | Warning |
| `TOOL-005` | Required fields exist in properties | Error |
| `RES-001` | Resources have uri and name | Error |

### Security (8 rules)

| Rule | Description | Severity |
|------|-------------|----------|
| `SEC-001` | Flag tools with dangerous names (execute, eval, shell...) | Warning |
| `SEC-002` | Flag unrestricted file path parameters | Warning |
| `SEC-003` | Flag `additionalProperties: true` or missing | Warning |
| `SEC-004` | Detect prompt injection patterns in descriptions | Error |
| `SEC-005` | Flag tracebacks in tool error responses | Warning |
| `SEC-006` | Flag tools with empty inputSchema | Warning |
| `SEC-007` | Flag unrestricted URL parameters (SSRF risk) | Warning |
| `SEC-008` | Flag parameters without type constraints | Warning |

### Performance (4 rules)

| Rule | Description | Severity |
|------|-------------|----------|
| `PERF-001` | `initialize` completes in under 5s | Warning |
| `PERF-002` | `tools/list` completes in under 2s | Warning |
| `PERF-003` | `resources/list` completes in under 2s | Warning |
| `PERF-004` | `prompts/list` completes in under 2s | Warning |

## CLI Reference

```
Usage: mcp-lint [OPTIONS] [COMMAND]

Arguments:
  COMMAND    MCP server command to run (stdio transport)

Options:
  --url TEXT               MCP server SSE URL
  -f, --format FORMAT      Output: terminal, json, markdown (default: terminal)
  --fail-under FLOAT       Exit 1 if score < threshold (default: 0)
  --timeout FLOAT          Global timeout in seconds (default: 30)
  --include TEXT            Comma-separated rule IDs to include
  --exclude TEXT            Comma-separated rule IDs to exclude
  -v, --verbose            Show detailed output
  -V, --version            Show version and exit
```

## Scoring

Each rule produces a result: **PASS** (1.0), **WARN** (0.5), **FAIL** (0.0), or **SKIP** (excluded from scoring).

The overall score is the weighted average as a percentage, mapped to a letter grade:

| Grade | Score |
|-------|-------|
| A | 90-100% |
| B | 80-89% |
| C | 70-79% |
| D | 60-69% |
| F | < 60% |

## CI/CD Integration

### GitHub Actions

```yaml
- name: Lint MCP Server
  run: |
    pip install mcp-lint
    mcp-lint "python -m my_server" --fail-under 80 --format json
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed (or score >= threshold) |
| `1` | Score below `--fail-under` threshold |
| `2` | Connection error or usage error |

## Development

```bash
git clone https://github.com/Luxshan2000/mcp-lint.git
cd mcp-lint
make dev        # install in editable mode
make test       # run tests
make lint       # run ruff linter
make format     # format code
make check      # lint + format check + tests
```

## License

MIT
