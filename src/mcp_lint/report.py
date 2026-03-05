from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mcp_lint.models import Category, Grade, ScoredReport, Status

_STATUS_COLORS = {
    Status.PASS: "green",
    Status.FAIL: "red",
    Status.WARN: "yellow",
    Status.SKIP: "dim",
    Status.ERROR: "red",
}

_STATUS_SYMBOLS = {
    Status.PASS: "[green]PASS[/green]",
    Status.FAIL: "[red]FAIL[/red]",
    Status.WARN: "[yellow]WARN[/yellow]",
    Status.SKIP: "[dim]SKIP[/dim]",
    Status.ERROR: "[red]ERR [/red]",
}

_GRADE_COLORS = {
    Grade.A: "green",
    Grade.B: "blue",
    Grade.C: "yellow",
    Grade.D: "red",
    Grade.F: "bold red",
}


def format_terminal(report: ScoredReport, verbose: bool = False) -> None:
    console = Console(stderr=True)

    # Header
    title = f"mcp-lint report: {report.server_name}"
    if report.server_version:
        title += f" v{report.server_version}"
    console.print()
    console.print(Panel(title, style="bold cyan"))

    # Results by category
    for category in Category:
        cat_results = [r for r in report.results if r.category == category]
        if not cat_results:
            continue

        table = Table(title=category.value, show_lines=False, padding=(0, 1))
        table.add_column("Status", width=6, no_wrap=True)
        table.add_column("Rule", width=10, no_wrap=True)
        table.add_column("Name", width=30)
        table.add_column("Message", ratio=1)

        for r in cat_results:
            status_text = _STATUS_SYMBOLS.get(r.status, str(r.status))
            msg = r.message
            if verbose and r.details:
                msg += f"\n  [dim]{r.details}[/dim]"
            table.add_row(status_text, r.rule_id, r.rule_name, msg)

        console.print(table)
        console.print()

    # Summary
    grade_color = _GRADE_COLORS.get(report.grade, "white")
    summary = Text()
    summary.append("Score: ", style="bold")
    summary.append(f"{report.score:.0f}%", style=grade_color)
    summary.append("  Grade: ", style="bold")
    summary.append(report.grade.value, style=f"bold {grade_color}")
    summary.append(f"\n{report.passed} passed", style="green")
    summary.append(f"  {report.failed} failed", style="red")
    summary.append(f"  {report.warnings} warnings", style="yellow")
    summary.append(f"  {report.skipped} skipped", style="dim")
    if report.errors:
        summary.append(f"  {report.errors} errors", style="red")
    console.print(Panel(summary, title="Summary"))
    console.print()


def format_json(report: ScoredReport) -> str:
    data = {
        "server": {
            "name": report.server_name,
            "version": report.server_version,
            "protocolVersion": report.protocol_version,
        },
        "transport": report.transport,
        "score": round(report.score, 1),
        "grade": report.grade.value,
        "summary": {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "warnings": report.warnings,
            "skipped": report.skipped,
            "errors": report.errors,
        },
        "results": [
            {
                "ruleId": r.rule_id,
                "ruleName": r.rule_name,
                "category": r.category.value,
                "severity": r.severity.value,
                "status": r.status.value,
                "message": r.message,
                "details": r.details,
                "durationMs": round(r.duration_ms, 2),
            }
            for r in report.results
        ],
    }
    return json.dumps(data, indent=2)


def format_markdown(report: ScoredReport) -> str:
    lines: list[str] = []
    title = f"# mcp-lint Report: {report.server_name}"
    if report.server_version:
        title += f" v{report.server_version}"
    lines.append(title)
    lines.append("")
    lines.append(f"**Score:** {report.score:.0f}% | **Grade:** {report.grade.value}")
    lines.append(f"**Protocol Version:** {report.protocol_version}")
    lines.append(f"**Transport:** {report.transport}")
    lines.append("")

    for category in Category:
        cat_results = [r for r in report.results if r.category == category]
        if not cat_results:
            continue
        lines.append(f"## {category.value}")
        lines.append("")
        lines.append("| Status | Rule | Name | Message |")
        lines.append("|--------|------|------|---------|")
        for r in cat_results:
            status = r.status.value.upper()
            msg = r.message.replace("|", "\\|")
            lines.append(f"| {status} | {r.rule_id} | {r.rule_name} | {msg} |")
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total:** {report.total}")
    lines.append(f"- **Passed:** {report.passed}")
    lines.append(f"- **Failed:** {report.failed}")
    lines.append(f"- **Warnings:** {report.warnings}")
    lines.append(f"- **Skipped:** {report.skipped}")
    if report.errors:
        lines.append(f"- **Errors:** {report.errors}")
    lines.append("")
    return "\n".join(lines)
