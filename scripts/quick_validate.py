#!/usr/bin/env python3
"""Quick validation for this skill folder."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAX_SKILL_NAME_LENGTH = 64
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}


def extract_frontmatter(text: str) -> str | None:
    match = re.match(r"^---\n(.*?)\n---", text, flags=re.DOTALL)
    return match.group(1) if match else None


def parse_top_level_keys(frontmatter: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_skill(skill_dir: Path) -> tuple[bool, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    frontmatter = extract_frontmatter(content)
    if frontmatter is None:
        return False, "Invalid frontmatter format"

    fields = parse_top_level_keys(frontmatter)
    keys = set(fields.keys())

    unexpected = keys - ALLOWED_KEYS
    if unexpected:
        return False, f"Unexpected key(s): {', '.join(sorted(unexpected))}"

    if "name" not in fields:
        return False, "Missing 'name' in frontmatter"
    if "description" not in fields:
        return False, "Missing 'description' in frontmatter"

    name = fields["name"]
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, "name should be hyphen-case (lowercase letters, digits, hyphens)"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, "name cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return False, f"name too long ({len(name)}), max {MAX_SKILL_NAME_LENGTH}"

    description = fields["description"]
    if "<" in description or ">" in description:
        return False, "description cannot contain < or >"
    if len(description) > 1024:
        return False, f"description too long ({len(description)}), max 1024"

    return True, "Skill is valid!"


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick validate SKILL.md")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill folder path")
    args = parser.parse_args()

    valid, message = validate_skill(Path(args.skill_dir))
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
