"""
Weekly Quality Analysis Script

Authenticates to Azure Key Vault, scans the repo for dependencies and code,
calls GPT-5.2 (or GPT-4o) via Azure OpenAI for upgrade and strategic analysis,
and outputs structured JSON reports that the GitHub Action uses to create PRs.

Usage:
    python run_analysis.py --repo-path /path/to/repo --mode upgrade
    python run_analysis.py --repo-path /path/to/repo --mode strategic
    python run_analysis.py --repo-path /path/to/repo --mode both
"""

import argparse
import json
import os
import sys
from pathlib import Path

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from openai import OpenAI


# ---------------------------------------------------------------------------
# Azure Auth
# ---------------------------------------------------------------------------

def get_openai_client_from_keyvault() -> tuple[OpenAI, str]:
    """Authenticate to Azure Key Vault and return an OpenAI client + endpoint."""
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    kv = SecretClient(
        vault_url=os.environ["KEY_VAULT_ENDPOINT"], credential=credential
    )

    api_key = kv.get_secret("AZURE-OPENAI-API-KEY").value
    endpoint = kv.get_secret("AZURE-OPENAI-CHAT-ENDPOINT").value
    base_url = f"{endpoint.rstrip('/')}/openai/v1/"

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, endpoint


def get_openai_client_direct() -> OpenAI:
    """Use AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT directly (no Key Vault)."""
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    base_url = f"{endpoint.rstrip('/')}/openai/v1/"
    return OpenAI(api_key=api_key, base_url=base_url)


def get_client() -> OpenAI:
    """Get OpenAI client — prefer Key Vault, fall back to direct env vars."""
    if os.environ.get("KEY_VAULT_ENDPOINT"):
        client, _ = get_openai_client_from_keyvault()
        return client
    return get_openai_client_direct()


# ---------------------------------------------------------------------------
# Repo Scanner
# ---------------------------------------------------------------------------

DEPENDENCY_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
]

CONTEXT_FILES = [
    "README.md",
    "CLAUDE.md",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".python-version",
    ".node-version",
    ".tool-versions",
]


def scan_repo(repo_path: Path) -> dict:
    """Scan the repo and collect dependency files, context files, and directory structure."""
    result = {
        "dependency_files": {},
        "context_files": {},
        "directory_structure": "",
        "source_files_sample": {},
    }

    # Collect dependency files
    for fname in DEPENDENCY_FILES:
        fpath = repo_path / fname
        if fpath.exists():
            result["dependency_files"][fname] = fpath.read_text(
                encoding="utf-8", errors="replace"
            )[:10000]  # cap at 10k chars

    # Collect context files
    for fname in CONTEXT_FILES:
        fpath = repo_path / fname
        if fpath.exists():
            result["context_files"][fname] = fpath.read_text(
                encoding="utf-8", errors="replace"
            )[:5000]

    # Directory structure (top 3 levels)
    result["directory_structure"] = _get_tree(repo_path, max_depth=3)

    # Sample source files (first 20 .py or .js files, first 100 lines each)
    source_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs"}
    count = 0
    for p in sorted(repo_path.rglob("*")):
        if count >= 20:
            break
        if (
            p.is_file()
            and p.suffix in source_exts
            and ".venv" not in str(p)
            and "node_modules" not in str(p)
            and "__pycache__" not in str(p)
            and ".git" not in str(p)
        ):
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[
                    :100
                ]
                rel = str(p.relative_to(repo_path))
                result["source_files_sample"][rel] = "\n".join(lines)
                count += 1
            except Exception:
                pass

    return result


def _get_tree(path: Path, max_depth: int, prefix: str = "", depth: int = 0) -> str:
    """Generate a simple directory tree string."""
    if depth > max_depth:
        return ""

    skip_dirs = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs",
    }

    lines = []
    try:
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError:
        return ""

    dirs = [e for e in entries if e.is_dir() and e.name not in skip_dirs]
    files = [e for e in entries if e.is_file()]

    for f in files[:15]:  # cap files per dir
        lines.append(f"{prefix}{f.name}")
    if len(files) > 15:
        lines.append(f"{prefix}... ({len(files) - 15} more files)")

    for d in dirs[:10]:
        lines.append(f"{prefix}{d.name}/")
        lines.append(_get_tree(d, max_depth, prefix + "  ", depth + 1))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM Analysis
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    return (SCRIPT_DIR / "prompts" / f"{name}.md").read_text(encoding="utf-8")


def call_llm(client: OpenAI, model: str, system_prompt: str, user_content: str) -> str:
    """Call the LLM and return the response text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content


def run_upgrade_analysis(client: OpenAI, model: str, repo_data: dict) -> dict:
    """Run the upgrade advisor analysis."""
    system_prompt = load_prompt("upgrade_advisor")

    user_content = "## Dependency Files\n\n"
    for fname, content in repo_data["dependency_files"].items():
        user_content += f"### {fname}\n```\n{content}\n```\n\n"

    user_content += "## Project Context\n\n"
    for fname, content in repo_data["context_files"].items():
        user_content += f"### {fname}\n```\n{content[:3000]}\n```\n\n"

    raw = call_llm(client, model, system_prompt, user_content)

    # Extract JSON from response (handle markdown code blocks)
    return _parse_json_response(raw)


def run_strategic_analysis(client: OpenAI, model: str, repo_data: dict) -> dict:
    """Run the strategic advisor analysis."""
    system_prompt = load_prompt("strategic_advisor")

    user_content = "## Directory Structure\n```\n"
    user_content += repo_data["directory_structure"][:3000]
    user_content += "\n```\n\n"

    user_content += "## Project Context\n\n"
    for fname, content in repo_data["context_files"].items():
        user_content += f"### {fname}\n```\n{content[:3000]}\n```\n\n"

    user_content += "## Dependencies\n\n"
    for fname, content in repo_data["dependency_files"].items():
        user_content += f"### {fname}\n```\n{content[:3000]}\n```\n\n"

    user_content += "## Source Files (sample)\n\n"
    for fname, content in list(repo_data["source_files_sample"].items())[:10]:
        user_content += f"### {fname}\n```\n{content[:2000]}\n```\n\n"

    raw = call_llm(client, model, system_prompt, user_content)
    return _parse_json_response(raw)


def _parse_json_response(raw: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try extracting from code block
    if "```json" in raw:
        start = raw.index("```json") + 7
        end = raw.index("```", start)
        return json.loads(raw[start:end].strip())
    if "```" in raw:
        start = raw.index("```") + 3
        end = raw.index("```", start)
        return json.loads(raw[start:end].strip())

    # Last resort — find first { to last }
    start = raw.index("{")
    end = raw.rindex("}") + 1
    return json.loads(raw[start:end])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Weekly Quality Analysis")
    parser.add_argument(
        "--repo-path", required=True, help="Path to the repository to analyze"
    )
    parser.add_argument(
        "--mode",
        choices=["upgrade", "strategic", "both"],
        default="both",
        help="Analysis mode",
    )
    parser.add_argument(
        "--model", default="gpt-5.2", help="Model to use (default: gpt-5.2)"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write results (default: repo-path)",
    )
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    output_dir = Path(args.output_dir) if args.output_dir else repo_path
    output_dir.mkdir(parents=True, exist_ok=True)

    if not repo_path.exists():
        print(f"Error: repo path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning repo: {repo_path}")
    repo_data = scan_repo(repo_path)

    dep_count = len(repo_data["dependency_files"])
    src_count = len(repo_data["source_files_sample"])
    print(f"Found {dep_count} dependency files, {src_count} source files sampled")

    if dep_count == 0:
        print("Warning: no dependency files found", file=sys.stderr)

    print("Connecting to Azure OpenAI...")
    client = get_client()

    results = {}

    if args.mode in ("upgrade", "both"):
        print(f"Running upgrade analysis with {args.model}...")
        try:
            results["upgrade"] = run_upgrade_analysis(client, args.model, repo_data)
            print(
                f"  Found {results['upgrade']['summary']['total_findings']} upgrade findings"
            )
        except Exception as e:
            print(f"  Upgrade analysis failed: {e}", file=sys.stderr)
            results["upgrade"] = {"findings": [], "summary": {"total_findings": 0}, "error": str(e)}

    if args.mode in ("strategic", "both"):
        print(f"Running strategic analysis with {args.model}...")
        try:
            results["strategic"] = run_strategic_analysis(client, args.model, repo_data)
            print(
                f"  Found {results['strategic']['summary']['total_findings']} strategic findings"
            )
        except Exception as e:
            print(f"  Strategic analysis failed: {e}", file=sys.stderr)
            results["strategic"] = {"findings": [], "summary": {"total_findings": 0}, "error": str(e)}

    # Write combined results
    output_file = output_dir / "quality-report.json"
    output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Report written to: {output_file}")

    # Determine if there are auto-mergeable changes
    auto_merge_findings = []
    for analysis_type, data in results.items():
        for finding in data.get("findings", []):
            if finding.get("auto_mergeable"):
                auto_merge_findings.append({**finding, "_source": analysis_type})

    # Write auto-merge candidates separately (used by the workflow)
    auto_merge_file = output_dir / "auto-merge-candidates.json"
    auto_merge_file.write_text(
        json.dumps(auto_merge_findings, indent=2), encoding="utf-8"
    )
    print(f"Auto-merge candidates: {len(auto_merge_findings)}")

    # Set GitHub Actions outputs
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            total = sum(
                d.get("summary", {}).get("total_findings", 0)
                for d in results.values()
            )
            critical = sum(
                d.get("summary", {}).get("critical_count", 0)
                for d in results.values()
            )
            f.write(f"total_findings={total}\n")
            f.write(f"critical_findings={critical}\n")
            f.write(f"auto_merge_count={len(auto_merge_findings)}\n")
            f.write(f"report_path={output_file}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
