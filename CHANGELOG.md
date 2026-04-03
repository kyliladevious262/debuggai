# Changelog

All notable changes to DebuggAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-03

### Added

- **Auto-Fix Engine**: Generate fix diffs via Claude with confidence scores
  - `debuggai fix` generates fixes, `debuggai fix --apply` applies them
  - `fix_issues` MCP tool + `/fix` slash command
  - Configurable minimum confidence threshold
- **Framework-Aware Context Detection**: Auto-detects tech stack and deployment model
  - Reads package.json, requirements.txt, vercel.json, Dockerfile
  - Detects React, Django, Next.js, Express, Vue, Svelte, FastAPI, Flask
  - Adjusts severity based on context (XSS suppressed for CLI tools, SQL injection downgraded with ORM)
  - Detects deployment model (Vercel, Netlify, Lambda, Docker, Heroku)
- **Dismissal Memory System**: Learn from user feedback
  - `debuggai dismiss <rule-id>` records dismissals
  - Auto-suppresses rules after 3 dismissals of the same pattern
  - SQLite-backed, persists across sessions
  - `dismiss_rule` MCP tool
- **Scan History & Quality Tracking**: Track quality over time
  - Every scan saved to local SQLite database
  - `debuggai history` shows trends with deltas (+3 new, -5 fixed)
  - `show_history` MCP tool + `/history` slash command
  - Issue lifecycle tracking: new, fixed, recurring, dismissed
- **Custom YAML Rule Engine**: Semgrep-style rules
  - Define rules in YAML with regex/pattern matching
  - Auto-loaded from `rules/` (built-in) and `.debuggai/rules/` (project)
  - 8 built-in rules: JWT secrets, bcrypt rounds, debug mode, TODO/FIXME, console.log, commented-out code, unbounded queries
- **Python-native MCP Server**: No npm/Node.js required
  - `debuggai setup` auto-registers in Claude Code / Cursor settings
  - `debuggai-mcp` entry point for direct MCP usage
  - 7 tools: scan_code, verify_intent, fix_issues, show_history, dismiss_rule, get_report, init_project
  - 5 slash commands: /scan, /verify, /fix, /history, /init

### Improved

- **False Positive Reduction**: Major accuracy improvements
  - Auto-skips build artifacts (.vercel/, dist/, build/, node_modules/)
  - Skips minified/bundled files (detected by line length heuristics)
  - Smarter innerHTML detection (only flags variable assignment, not template literals)
  - Smarter secret detection (skips os.getenv, process.env patterns)
  - Smarter SQL injection detection (skips parameterized queries with ? placeholders, column name toggles)
  - Removed print() from I/O-in-loop detection (it's logging, not I/O)
  - Context-aware severity adjustment based on detected framework
- **MCP Server rewritten in Python**: Single `pip install` gets everything, no npm dependency

### Changed

- MCP server moved from TypeScript (`mcp-server/`) to Python (`debuggai/mcp_server.py`)
- `debuggai setup` command replaces manual JSON config editing

## [0.1.0] - 2026-04-03

### Added

- **CLI tool** with `init`, `scan`, `verify`, and `config` commands
- **Code QA Engine** with 4 analyzers:
  - Hallucinated import detector (Python + JavaScript/TypeScript)
  - Security vulnerability scanner (15 patterns: XSS, SQLi, hardcoded secrets, eval, command injection, insecure deserialization, and more)
  - Performance anti-pattern detector (O(n^2) loops, I/O in loops, sync blocking, N+1 queries)
  - LLM-powered semantic review via Claude API
- **Intent Verification Engine**:
  - Captures intent from CLI flags, spec files, and git commit messages
  - Extracts structured assertions from natural language via LLM
  - Scores each assertion against actual code
  - Computes Prompt Fidelity Score (0-100)
- **Report generator** with 3 output formats: terminal (Rich), Markdown, JSON
- **Configuration system** with `.debuggai.yaml` and auto-detection of project languages
- Support for Python, JavaScript, and TypeScript codebases
