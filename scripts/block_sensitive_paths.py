#!/usr/bin/env python3
"""Block staged sensitive files before commit."""

from __future__ import annotations

import subprocess
from pathlib import Path


BLOCKED_PREFIXES = ("input/", "output/", "__pycache__/")
SENSITIVE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".tif", ".tiff", ".bmp", ".gif"}
SAFE_MEDIA_PREFIXES = ("examples/", "assets/")


def staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_sensitive_media(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() not in SENSITIVE_EXTENSIONS:
        return False
    return not path.startswith(SAFE_MEDIA_PREFIXES)


def main() -> int:
    files = staged_files()
    if not files:
        return 0

    violations: list[str] = []
    for path in files:
        if path.startswith(BLOCKED_PREFIXES):
            violations.append(f"{path} (blocked directory)")
            continue
        if path.endswith(".pyc"):
            violations.append(f"{path} (.pyc should not be committed)")
            continue
        if is_sensitive_media(path):
            violations.append(f"{path} (media files allowed only under examples/ or assets/)")

    if not violations:
        return 0

    print("Commit blocked: detected potential sensitive files.")
    for item in violations:
        print(f" - {item}")
    print("If this is intentional, move sample files to examples/ and re-stage.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
