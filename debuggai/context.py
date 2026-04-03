"""Framework and deployment context detection.

Auto-detects tech stack, frameworks, and deployment model from project files.
Used to adjust rule severity and suppress false positives.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ProjectContext:
    """Detected context about the project being scanned."""

    # Deployment
    deployment: Optional[str] = None  # vercel, railway, docker, netlify, aws-lambda, static, unknown
    is_serverless: bool = False
    has_edge_runtime: bool = False

    # App type
    is_web_app: bool = False
    is_cli: bool = False
    is_library: bool = False
    is_api: bool = False

    # Frameworks
    frameworks: list[str] = field(default_factory=list)  # django, flask, express, next, react, etc.

    # Protections — frameworks that auto-sanitize
    has_orm: bool = False           # Django ORM, SQLAlchemy, Prisma — auto-parameterize SQL
    has_template_escaping: bool = False  # Django templates, Jinja2, React JSX — auto-escape HTML
    has_csrf_protection: bool = False
    has_cors_configured: bool = False

    # Languages detected
    languages: list[str] = field(default_factory=list)

    # Config files found
    config_files: list[str] = field(default_factory=list)


def detect_context(project_dir: str) -> ProjectContext:
    """Auto-detect project context from config files and structure."""
    root = Path(project_dir)
    ctx = ProjectContext()

    # Check for config files
    _detect_deployment(root, ctx)
    _detect_frameworks(root, ctx)
    _detect_app_type(root, ctx)
    _detect_protections(ctx)

    return ctx


def _detect_deployment(root: Path, ctx: ProjectContext) -> None:
    """Detect deployment model."""
    if (root / "vercel.json").exists() or (root / ".vercel").exists():
        ctx.deployment = "vercel"
        ctx.is_serverless = True
        ctx.config_files.append("vercel.json")

    elif (root / "netlify.toml").exists():
        ctx.deployment = "netlify"
        ctx.is_serverless = True
        ctx.config_files.append("netlify.toml")

    elif (root / "railway.json").exists() or (root / "railway.toml").exists():
        ctx.deployment = "railway"
        ctx.config_files.append("railway.json")

    elif (root / "serverless.yml").exists() or (root / "serverless.yaml").exists():
        ctx.deployment = "aws-lambda"
        ctx.is_serverless = True
        ctx.config_files.append("serverless.yml")

    elif (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists():
        ctx.deployment = "docker"
        ctx.config_files.append("Dockerfile")

    elif (root / "Procfile").exists():
        ctx.deployment = "heroku"
        ctx.config_files.append("Procfile")

    # Check for edge runtime
    if ctx.deployment == "vercel":
        # Check vercel.json for edge functions
        vj = root / "vercel.json"
        if vj.exists():
            try:
                data = json.loads(vj.read_text())
                if any("edge" in str(r).lower() for r in data.get("functions", {}).values()):
                    ctx.has_edge_runtime = True
            except (json.JSONDecodeError, AttributeError):
                pass


def _detect_frameworks(root: Path, ctx: ProjectContext) -> None:
    """Detect frameworks from package.json, requirements.txt, etc."""
    # Python frameworks
    for req_file in ["requirements.txt", "Pipfile", "pyproject.toml"]:
        path = root / req_file
        if path.exists():
            content = path.read_text().lower()
            if "django" in content:
                ctx.frameworks.append("django")
                ctx.has_orm = True
                ctx.has_template_escaping = True
                ctx.has_csrf_protection = True
            if "flask" in content:
                ctx.frameworks.append("flask")
            if "fastapi" in content:
                ctx.frameworks.append("fastapi")
            if "sqlalchemy" in content:
                ctx.has_orm = True
            if "prisma" in content:
                ctx.has_orm = True

    # JS/TS frameworks
    pkg_json = root / "package.json"
    if pkg_json.exists():
        ctx.config_files.append("package.json")
        try:
            pkg = json.loads(pkg_json.read_text())
            all_deps = {}
            for key in ["dependencies", "devDependencies"]:
                all_deps.update(pkg.get(key, {}))

            dep_names = set(all_deps.keys())

            if "next" in dep_names:
                ctx.frameworks.append("next")
                ctx.has_template_escaping = True  # JSX auto-escapes
            if "react" in dep_names or "react-dom" in dep_names:
                ctx.frameworks.append("react")
                ctx.has_template_escaping = True  # JSX auto-escapes
            if "vue" in dep_names:
                ctx.frameworks.append("vue")
                ctx.has_template_escaping = True
            if "svelte" in dep_names:
                ctx.frameworks.append("svelte")
                ctx.has_template_escaping = True
            if "express" in dep_names:
                ctx.frameworks.append("express")
            if "fastify" in dep_names:
                ctx.frameworks.append("fastify")
            if "prisma" in dep_names or "@prisma/client" in dep_names:
                ctx.has_orm = True
            if "sequelize" in dep_names:
                ctx.has_orm = True
            if "drizzle-orm" in dep_names:
                ctx.has_orm = True
            if "cors" in dep_names:
                ctx.has_cors_configured = True
            if "helmet" in dep_names:
                ctx.has_csrf_protection = True
            if "csurf" in dep_names:
                ctx.has_csrf_protection = True

        except json.JSONDecodeError:
            pass


def _detect_app_type(root: Path, ctx: ProjectContext) -> None:
    """Detect whether this is a web app, CLI, library, or API."""
    if any(f in ctx.frameworks for f in ["react", "next", "vue", "svelte"]):
        ctx.is_web_app = True
    if any(f in ctx.frameworks for f in ["express", "fastify", "fastapi", "flask", "django"]):
        ctx.is_api = True
        ctx.is_web_app = True

    # Check for CLI indicators
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            if "bin" in pkg:
                ctx.is_cli = True
        except json.JSONDecodeError:
            pass

    setup_cfg = root / "setup.cfg"
    pyproject = root / "pyproject.toml"
    for f in [setup_cfg, pyproject]:
        if f.exists():
            content = f.read_text()
            if "[project.scripts]" in content or "console_scripts" in content:
                ctx.is_cli = True

    # If no web indicators found, check for index.html
    if not ctx.is_web_app:
        for html_loc in ["index.html", "public/index.html", "src/index.html"]:
            if (root / html_loc).exists():
                ctx.is_web_app = True
                break


def _detect_protections(ctx: ProjectContext) -> None:
    """Set protection flags based on detected frameworks."""
    # React/Vue/Svelte auto-escape HTML in templates
    if any(f in ctx.frameworks for f in ["react", "next", "vue", "svelte"]):
        ctx.has_template_escaping = True

    # Django has CSRF by default
    if "django" in ctx.frameworks:
        ctx.has_csrf_protection = True


def should_adjust_severity(ctx: ProjectContext, rule_id: str, category: str) -> Optional[str]:
    """Return adjusted severity or None to keep original.

    Returns:
        None = keep original severity
        "suppress" = suppress entirely (false positive given context)
        "info" / "minor" / "major" / "critical" = new severity
    """
    # XSS in CLI tools is not exploitable
    if rule_id in ("xss-innerhtml", "xss-react-dangerous") and ctx.is_cli and not ctx.is_web_app:
        return "suppress"

    # dangerouslySetInnerHTML in React — user knows what they're doing (React auto-escapes by default)
    if rule_id == "xss-react-dangerous" and "react" in ctx.frameworks:
        return "minor"  # downgrade from major — React devs are aware

    # SQL injection with ORM — parameterized by default
    if rule_id == "sql-injection" and ctx.has_orm:
        return "minor"  # downgrade — ORM handles parameterization

    # CORS wildcard is only critical for APIs with auth
    if rule_id == "cors-wildcard" and not ctx.is_api:
        return "info"  # static sites don't care about CORS

    # localStorage is fine for non-sensitive apps
    if rule_id == "localstorage-sensitive" and ctx.is_cli:
        return "suppress"

    return None
