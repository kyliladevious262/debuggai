<p align="center">
  <h1 align="center">DebuggAI</h1>
  <p align="center">The universal verification layer for AI-generated software.</p>
</p>

<p align="center">
  <a href="https://github.com/rish-e/debuggai/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rish-e/debuggai" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
</p>

---

AI-generated code has **1.7x more bugs** than human-written code. DebuggAI catches them — hallucinated APIs, security vulnerabilities, performance anti-patterns, and intent mismatches — before they reach production.

---

## How to Use

There are **two ways** to use DebuggAI. Pick whichever fits your workflow.

### Option A: Inside Claude Code / Cursor (recommended)

Use DebuggAI without leaving your AI coding workflow. Just talk naturally.

**One-time setup:**

```bash
pip install debuggai
debuggai setup
```

Then **restart Claude Code** (or Cursor).

**That's it.** Now just ask Claude:

- *"scan this project for bugs"*
- *"scan src/app.py for security issues"*  
- *"verify this code matches: add user authentication with OAuth"*
- *"check my staged changes before I commit"*

Claude will use DebuggAI's tools automatically. No commands to memorize — just describe what you want.

### Option B: Terminal CLI

Run scans directly from your terminal.

```bash
# Go to any project
cd ~/my-project

# Scan everything
debuggai scan --no-llm

# Scan a specific file
debuggai scan --file src/app.py

# Scan what changed since last commit
debuggai scan --diff HEAD~1

# Scan staged changes (great before committing)
debuggai scan --staged

# Verify code matches what you asked AI to build
debuggai verify --intent "add Google OAuth login"
```

---

## What It Catches

### Hallucinated Imports
AI tools make up packages that don't exist. DebuggAI checks your actual dependency tree.

```
!!! [IMPORT] Hallucinated import: fastapi_magic_router  src/app.py:4
   Module 'fastapi_magic_router' is not installed and not in standard library
   Fix: Verify that 'fastapi_magic_router' exists. Install it or remove the import.
```

### Security Vulnerabilities
15 patterns tuned for AI code — XSS, SQL injection, hardcoded secrets, eval, command injection, and more.

```
!!! [SECURITY] SQL injection vulnerability  src/db.py:17
   SQL query built with string interpolation instead of parameterized queries.
   Fix: Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
```

### Performance Anti-Patterns
O(n²) loops, I/O inside loops, sync blocking calls, N+1 queries.

```
 !! [PERFORMANCE] I/O operation in loop: requests.get  src/sync.py:39
   'requests.get' called inside a loop at line 39. Each iteration performs I/O.
   Fix: Batch I/O operations outside the loop, or use async/concurrent patterns.
```

### LLM-Powered Deep Review
Sends code to Claude for semantic analysis — logic errors, incomplete error handling, architectural drift, dead code. Requires an Anthropic API key.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
debuggai scan --file src/app.py
```

### Intent Verification
Compares what you asked the AI to build vs. what was actually built. Gives you a **Prompt Fidelity Score**.

```bash
debuggai verify --intent "add user auth with Google OAuth" --file src/
```

```
Prompt Fidelity Score: 65/100

[+] OAuth dependency present (google-auth-library found)
[x] No /auth/google route found
[~] Token storage partially implemented (found in localStorage — insecure)
[+] Redirect to login page implemented
```

---

## Why DebuggAI?

Traditional linters weren't designed for AI-generated code. They miss what AI specifically gets wrong:

| Problem | How Often in AI Code | DebuggAI Detection |
|---------|---------------------|-------------------|
| Hallucinated imports (non-existent packages) | Very common | AST + dependency resolution |
| XSS vulnerabilities | 2.74x more likely | Pattern + AST analysis |
| Excessive I/O operations | 8x more frequent | AST loop analysis |
| Hardcoded secrets | 1.88x more likely | Regex + entropy detection |
| Missing error handling | 1.75x more frequent | LLM semantic review |
| Intent mismatches | Universal | Prompt Fidelity scoring |

---

## CLI Reference

### `debuggai setup`

Auto-registers DebuggAI as an MCP server in Claude Code or Cursor. Run once.

```bash
debuggai setup              # Claude Code (default)
debuggai setup --cursor     # Cursor
```

### `debuggai init [directory]`

Initialize DebuggAI for a project. Auto-detects languages and creates `.debuggai.yaml`.

### `debuggai scan`

Scan code for AI-generated bugs.

| Flag | Description |
|------|-------------|
| `--file, -f` | File or directory to scan |
| `--diff, -d` | Git ref to diff against (e.g., `HEAD~1`) |
| `--staged, -s` | Scan staged changes only |
| `--intent, -i` | Intent to verify alongside scan |
| `--no-llm` | Skip LLM analysis (faster, no API key needed) |
| `--format, -o` | Output format: `terminal`, `markdown`, `json` |
| `--strict` | Report all severities including minor and info |

Exit codes: 0 = clean, 1 = major issues, 2 = critical issues.

### `debuggai verify`

Verify code against a natural language intent.

| Flag | Description |
|------|-------------|
| `--intent, -i` | Intent to verify (required) |
| `--file, -f` | File or directory to verify against |
| `--diff, -d` | Git ref to verify against |
| `--format, -o` | Output format: `terminal`, `markdown`, `json` |

### `debuggai config`

Show current DebuggAI configuration.

---

## Configuration

Create a `.debuggai.yaml` in your project root (or run `debuggai init`):

```yaml
project:
  name: "my-project"
  type: "fullstack"

code:
  languages: [python, typescript]
  strictness: medium   # low (critical only) | medium (default) | high (everything)
  ignore:
    - "*.test.*"
    - "node_modules/"
  rules:
    security: true
    performance: true
    ai_patterns: true

reporting:
  format: markdown
  severity_threshold: minor
  output: stdout
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: DebuggAI Scan
  run: |
    pip install debuggai
    debuggai scan --format json --no-llm
  continue-on-error: false
```

### Pre-commit Hook

```bash
debuggai scan --staged --no-llm
```

---

## Supported Languages

| Language | Import Detection | Security Scan | Performance Scan |
|----------|:---:|:---:|:---:|
| Python | Yes | Yes | Yes |
| JavaScript | Yes | Yes | Yes |
| TypeScript | Yes | Yes | Yes |
| Go | Planned | Planned | Planned |
| Rust | Planned | Planned | Planned |
| Java | Planned | Planned | Planned |

## Roadmap

- **v0.1** (current) — Code QA + Intent Verification + CLI + MCP Server
- **v1.0** — Creative Output QA (video/audio), auto-fix suggestions, GitHub PR comments
- **v1.5** — Cloud dashboard, team features, quality gates
- **v2.0** — Autonomous testing agent, self-healing tests, enterprise features

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache 2.0 — see [LICENSE](LICENSE).
