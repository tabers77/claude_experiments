"""
Validate all SKILL.md files in the skills/ directory.

Checks:
- Every skill dir has a SKILL.md
- SKILL.md has valid YAML frontmatter with 'name' and 'description'
- Skill names use hyphens only (no underscores)
- Skill name matches directory name
- Directory names use hyphens only
"""
import os
import sys
import re

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "agents")


def parse_frontmatter(content):
    """Extract YAML frontmatter from a SKILL.md file."""
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    frontmatter = content[3:end].strip()
    result = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def test_skill_directories_use_hyphens():
    errors = []
    for name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_path):
            continue
        if "_" in name:
            errors.append(f"  {name}: uses underscores, should use hyphens")
    if errors:
        print("FAIL: Skill directories with underscores:")
        print("\n".join(errors))
        return False
    print("PASS: All skill directories use hyphens")
    return True


def test_all_skills_have_skill_md():
    errors = []
    for name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_path):
            continue
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_md):
            errors.append(f"  {name}: missing SKILL.md")
    if errors:
        print("FAIL: Skills missing SKILL.md:")
        print("\n".join(errors))
        return False
    print("PASS: All skill directories have SKILL.md")
    return True


def test_all_skills_have_valid_frontmatter():
    errors = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_path):
            continue
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_md):
            continue
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        if fm is None:
            errors.append(f"  {name}: no YAML frontmatter found")
            continue
        if "name" not in fm:
            errors.append(f"  {name}: frontmatter missing 'name'")
        if "description" not in fm:
            errors.append(f"  {name}: frontmatter missing 'description'")
    if errors:
        print("FAIL: Skills with invalid frontmatter:")
        print("\n".join(errors))
        return False
    print("PASS: All skills have valid frontmatter (name + description)")
    return True


def test_skill_names_match_directories():
    errors = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_path):
            continue
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_md):
            continue
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        if fm and "name" in fm:
            if fm["name"] != name:
                errors.append(
                    f"  {name}: frontmatter name '{fm['name']}' != dir name '{name}'"
                )
    if errors:
        print("FAIL: Skill name/directory mismatches:")
        print("\n".join(errors))
        return False
    print("PASS: All skill names match their directory names")
    return True


def test_skill_names_no_underscores():
    errors = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_path):
            continue
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_md):
            continue
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        if fm and "name" in fm:
            if "_" in fm["name"]:
                errors.append(
                    f"  {name}: frontmatter name '{fm['name']}' has underscores"
                )
    if errors:
        print("FAIL: Skill names with underscores in frontmatter:")
        print("\n".join(errors))
        return False
    print("PASS: No skill names contain underscores")
    return True


def test_agents_have_frontmatter():
    errors = []
    for name in os.listdir(AGENTS_DIR):
        if not name.endswith(".md"):
            continue
        agent_path = os.path.join(AGENTS_DIR, name)
        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        if fm is None:
            errors.append(f"  {name}: no YAML frontmatter found")
            continue
        if "name" not in fm:
            errors.append(f"  {name}: frontmatter missing 'name'")
        if "description" not in fm:
            errors.append(f"  {name}: frontmatter missing 'description'")
    if errors:
        print("FAIL: Agents with invalid frontmatter:")
        print("\n".join(errors))
        return False
    print("PASS: All agents have valid frontmatter")
    return True


def test_expected_skill_count():
    count = sum(
        1
        for name in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, name))
    )
    if count < 21:
        print(f"FAIL: Expected at least 21 skills, found {count}")
        return False
    print(f"PASS: Found {count} skills (expected >= 21)")
    return True


if __name__ == "__main__":
    print(f"Skills dir: {os.path.abspath(SKILLS_DIR)}")
    print(f"Agents dir: {os.path.abspath(AGENTS_DIR)}")
    print()

    tests = [
        test_skill_directories_use_hyphens,
        test_all_skills_have_skill_md,
        test_all_skills_have_valid_frontmatter,
        test_skill_names_match_directories,
        test_skill_names_no_underscores,
        test_agents_have_frontmatter,
        test_expected_skill_count,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    if not all(results):
        sys.exit(1)
    print("All checks passed!")
