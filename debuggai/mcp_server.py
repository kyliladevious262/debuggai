"""DebuggAI MCP Server — Python-native, no npm required.

Run with: debuggai serve
Or point your MCP config to: python -m debuggai.mcp_server
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "DebuggAI",
    version="0.1.0",
    description="The universal verification layer for AI-generated software",
)


# ─── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def scan_code(
    target: str = ".",
    diff: str | None = None,
    staged: bool = False,
    no_llm: bool = False,
    strict: bool = False,
) -> str:
    """Scan code for AI-generated bugs, security issues, and performance problems.

    Args:
        target: File or directory to scan (defaults to current directory)
        diff: Git ref to diff against (e.g., "HEAD~1")
        staged: Scan staged changes only
        no_llm: Skip LLM analysis for faster results
        strict: Report all severities including minor and info
    """
    from debuggai.orchestrator import run_scan
    from debuggai.reports.generator import format_markdown

    if strict:
        os.environ["DEBUGGAI_STRICTNESS"] = "high"

    report = run_scan(
        target=target if target != "." else None,
        diff_ref=diff,
        staged=staged,
        use_llm=not no_llm,
    )

    return format_markdown(report)


@mcp.tool()
def verify_intent(
    intent: str,
    target: str | None = None,
    diff: str | None = None,
) -> str:
    """Verify code matches a natural language intent. Returns Prompt Fidelity Score.

    Args:
        intent: What the code should do (e.g., "add user authentication with OAuth")
        target: File or directory to verify against
        diff: Git ref to verify against
    """
    from debuggai.orchestrator import run_scan
    from debuggai.reports.generator import format_markdown

    report = run_scan(
        target=target,
        diff_ref=diff,
        intent=intent,
        use_llm=True,
    )

    return format_markdown(report)


@mcp.tool()
def get_report(
    target: str | None = None,
    diff: str | None = None,
    no_llm: bool = True,
) -> str:
    """Get a full DebuggAI report in JSON format for programmatic analysis.

    Args:
        target: File or directory to scan
        diff: Git ref to diff against
        no_llm: Skip LLM analysis (default: True for speed)
    """
    from debuggai.orchestrator import run_scan
    from debuggai.reports.generator import format_json

    report = run_scan(
        target=target,
        diff_ref=diff,
        use_llm=not no_llm,
    )

    return format_json(report)


@mcp.tool()
def init_project(directory: str = ".") -> str:
    """Initialize DebuggAI for a project. Auto-detects languages and creates config.

    Args:
        directory: Project directory (defaults to current directory)
    """
    from debuggai.config import generate_default_config, auto_detect_languages

    project_dir = str(Path(directory).resolve())
    config_path = Path(project_dir) / ".debuggai.yaml"

    if config_path.exists():
        return f"Config already exists at {config_path}. Delete it first to reinitialize."

    config_content = generate_default_config(project_dir)
    config_path.write_text(config_content)

    langs = auto_detect_languages(project_dir)
    return (
        f"Initialized DebuggAI in {project_dir}\n"
        f"Config written to: {config_path}\n"
        f"Detected languages: {', '.join(langs) if langs else 'none'}\n"
        f"\nUse /scan to analyze your code."
    )


# ─── Prompts (slash commands) ─────────────────────────────────────────────────


@mcp.prompt()
def scan(target: str = ".", strict: bool = False) -> str:
    """Scan the current project for AI-generated code bugs, security issues, and performance problems."""
    parts = [f"Run the scan_code tool on target=\"{target}\""]
    if strict:
        parts.append(" with strict=True")
    parts.append(
        ". After getting results, present the findings clearly — "
        "group by severity, highlight critical issues first, and include fix suggestions."
    )
    return "".join(parts)


@mcp.prompt()
def verify(intent: str, target: str = ".") -> str:
    """Verify that code matches what you asked the AI to build. Returns a Prompt Fidelity Score."""
    return (
        f'Run the verify_intent tool with intent="{intent}" and target="{target}". '
        "Present the Prompt Fidelity Score prominently, then show each assertion with its "
        "pass/fail status. For failed assertions, explain what's missing and suggest fixes."
    )


@mcp.prompt()
def init(directory: str = ".") -> str:
    """Initialize DebuggAI for a project. Auto-detects languages and creates config."""
    return (
        f'Run the init_project tool with directory="{directory}". '
        "Show the user what was detected and configured."
    )


# ─── Entry point ──────────────────────────────────────────────────────────────


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
