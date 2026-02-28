"""
Weekly Quality Analysis — Simplified

Authenticates to Azure Key Vault, scans the repo, calls Azure OpenAI,
and outputs a markdown report for use as a GitHub issue body.

Usage:
    python run_analysis.py --repo-path /path/to/repo --mode both
    python run_analysis.py --repo-path /path/to/repo --mode upgrade --output report.md
"""

import argparse
import io
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import OpenAI


# ---------------------------------------------------------------------------
# Azure Auth
# ---------------------------------------------------------------------------

def get_client() -> OpenAI:
    """Get OpenAI client via Key Vault or direct env vars."""
    kv_url = os.environ.get("KEY_VAULT_ENDPOINT")
    if kv_url:
        client_id = os.environ.get("AZURE_CLIENT_ID")
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")

        if client_id and tenant_id and client_secret:
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        else:
            credential = DefaultAzureCredential()

        kv = SecretClient(vault_url=kv_url, credential=credential)
        api_key = kv.get_secret("AZURE-OPENAI-API-KEY").value
        endpoint = kv.get_secret("AZURE-OPENAI-CHAT-ENDPOINT").value
        return OpenAI(api_key=api_key, base_url=f"{endpoint.rstrip('/')}/openai/v1/")

    if os.environ.get("AZURE_OPENAI_API_KEY"):
        api_key = os.environ["AZURE_OPENAI_API_KEY"]
        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        return OpenAI(api_key=api_key, base_url=f"{endpoint.rstrip('/')}/openai/v1/")

    print("Error: Set KEY_VAULT_ENDPOINT or AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Repo Scanner
# ---------------------------------------------------------------------------

DEPENDENCY_FILES = [
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
    "Pipfile", "package.json", "Cargo.toml", "go.mod", "Gemfile",
]

CONTEXT_FILES = ["README.md", "CLAUDE.md", ".python-version", ".node-version"]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "_quality-action", ".quality-reports"}


def scan_repo(repo_path: Path) -> str:
    """Scan repo and return a text summary for the LLM prompt."""
    sections = []

    # Dependency files (root + 1 level deep)
    dep_files = {}
    for fname in DEPENDENCY_FILES:
        fpath = repo_path / fname
        if fpath.exists():
            dep_files[fname] = fpath.read_text(encoding="utf-8", errors="replace")[:8000]
    for subdir in repo_path.iterdir():
        if subdir.is_dir() and subdir.name not in SKIP_DIRS and not subdir.name.startswith("."):
            for fname in DEPENDENCY_FILES:
                fpath = subdir / fname
                if fpath.exists():
                    dep_files[f"{subdir.name}/{fname}"] = fpath.read_text(encoding="utf-8", errors="replace")[:8000]

    if dep_files:
        sections.append("## Dependency Files\n")
        for fname, content in dep_files.items():
            sections.append(f"### {fname}\n```\n{content}\n```\n")

    # Context files
    for fname in CONTEXT_FILES:
        fpath = repo_path / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8", errors="replace")[:4000]
            sections.append(f"## {fname}\n```\n{content}\n```\n")

    # Directory structure (top 2 levels)
    sections.append("## Directory Structure\n```")
    for entry in sorted(repo_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
        if entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue
        if entry.is_dir():
            sections.append(f"{entry.name}/")
            try:
                for child in sorted(entry.iterdir(), key=lambda e: e.name)[:15]:
                    sections.append(f"  {child.name}")
            except PermissionError:
                pass
        else:
            sections.append(entry.name)
    sections.append("```\n")

    # Sample source files (first 10, first 80 lines each)
    source_exts = {".py", ".js", ".ts", ".go", ".rs"}
    count = 0
    source_section = ["## Source Files (sample)\n"]
    for p in sorted(repo_path.rglob("*")):
        if count >= 10:
            break
        if p.is_file() and p.suffix in source_exts and not any(s in str(p) for s in SKIP_DIRS):
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[:80]
                rel = str(p.relative_to(repo_path))
                source_section.append(f"### {rel}\n```\n{chr(10).join(lines)}\n```\n")
                count += 1
            except Exception:
                pass
    if count > 0:
        sections.extend(source_section)

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

UPGRADE_PROMPT = """You are a dependency upgrade advisor. Analyze this project's dependencies and produce a **markdown report** (not JSON).

For each outdated or risky dependency, include:
- Package name, current version, recommended version
- Why it matters (security, deprecation, new features)
- Effort and risk level (low/medium/high)

Organize findings by priority:
1. **Do Now** — security vulnerabilities, deprecated/EOL packages
2. **Plan Soon** — major versions behind, useful new features available
3. **Monitor** — minor versions behind, low impact
4. **Accept** — intentionally pinned or no meaningful upgrade

End with a brief summary count. Be concise — skip packages that are already current."""

STRATEGIC_PROMPT = """You are a strategic technical advisor. Analyze this project's codebase and suggest improvements.

Focus on:
- Anti-patterns and code quality issues (with specific file paths)
- Architecture improvements aligned with the project's stated goals
- New capabilities, libraries, or patterns worth adopting
- Performance and security improvements

Organize findings by priority:
1. **Do Now** — high-impact, low-effort improvements
2. **Plan Soon** — important but needs design work
3. **Monitor** — interesting but not urgent
4. **Accept** — known trade-offs that are fine for now

Be specific — include file paths and concrete suggestions, not generic advice. Be concise."""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def call_llm(client: OpenAI, model: str, system_prompt: str, user_content: str) -> str:
    """Call LLM and return markdown response."""
    is_gpt5_plus = any(tag in model for tag in ("gpt-5", "gpt-6", "o1", "o3"))
    token_param = {"max_completion_tokens": 4096} if is_gpt5_plus else {"max_tokens": 4096}

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        **token_param,
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Weekly Quality Analysis")
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--mode", choices=["upgrade", "strategic", "both"], default="both")
    parser.add_argument("--model", default="gpt-5.2")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Error: {repo_path} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning: {repo_path}", file=sys.stderr)
    repo_context = scan_repo(repo_path)

    print("Connecting to Azure OpenAI...", file=sys.stderr)
    client = get_client()

    report_parts = [f"## Weekly Quality Report\n\n**Date**: {__import__('datetime').date.today()}\n**Model**: {args.model}\n"]

    if args.mode in ("upgrade", "both"):
        print(f"Running upgrade analysis ({args.model})...", file=sys.stderr)
        try:
            result = call_llm(client, args.model, UPGRADE_PROMPT, repo_context)
            report_parts.append(f"---\n\n### Upgrade Analysis\n\n{result}\n")
        except Exception as e:
            report_parts.append(f"---\n\n### Upgrade Analysis\n\n> Error: {e}\n")
            print(f"Upgrade analysis failed: {e}", file=sys.stderr)

    if args.mode in ("strategic", "both"):
        print(f"Running strategic analysis ({args.model})...", file=sys.stderr)
        try:
            result = call_llm(client, args.model, STRATEGIC_PROMPT, repo_context)
            report_parts.append(f"---\n\n### Strategic Analysis\n\n{result}\n")
        except Exception as e:
            report_parts.append(f"---\n\n### Strategic Analysis\n\n> Error: {e}\n")
            print(f"Strategic analysis failed: {e}", file=sys.stderr)

    report = "\n".join(report_parts)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
