"""profile.py — load a per-product review profile (profiles/<name>.json).

The review layers are product-neutral; everything that differs between
Proxy and Hub (docs location, doc engine, style guide, which code counts as
user-facing, which bot PRs to skip) lives in one JSON file per product.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"

REQUIRED_KEYS = ("name", "repo", "engine", "docs_root", "source", "style_guide")


def load(name_or_path: str) -> dict:
    """Load a profile by bare name ('proxy') or by explicit path."""
    p = Path(name_or_path)
    if not p.suffix:
        p = PROFILES_DIR / f"{name_or_path}.json"
    data = json.loads(p.read_text())
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ValueError(f"profile {p} missing keys: {missing}")
    return data


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python3 -m scripts.profile <name-or-path>", file=sys.stderr)
        return 2
    print(json.dumps(load(argv[0]), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
