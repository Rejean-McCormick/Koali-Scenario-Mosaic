#!/usr/bin/env python3
"""Patch Koali Scenario Mosaic V2.2 to remove the undeclared PyYAML build dependency.

Run from the repository root:
    python path/to/apply_fix.py

The patch is intentionally narrow and idempotent:
- creates scripts/frontmatter_stdlib.py
- patches scripts/validate-v2.py
- patches scripts/build-offline-preview.py when present
- does not change scenario content, Astro code, CSS, or Netlify config
"""
from pathlib import Path
import re
import sys

ROOT = Path.cwd()
SCRIPTS = ROOT / "scripts"
VALIDATOR = SCRIPTS / "validate-v2.py"
BUILDER = SCRIPTS / "build-offline-preview.py"
HELPER = SCRIPTS / "frontmatter_stdlib.py"

HELPER_CONTENT = r'''"""Minimal YAML-front-matter reader for Koali scenario metadata.

This intentionally supports the subset used by Scenario Mosaic:
- top-level scalar keys
- top-level block lists (`key:` followed by `- item`)
- simple inline lists (`[a, b, "c"]`)
- quoted/unquoted strings, booleans, nulls, ints, floats

It is not a general YAML implementation. Keeping the scenario metadata subset
small makes Netlify validation independent of PyYAML or other Python packages.
"""
from __future__ import annotations

import csv
import io
import json
import re
from typing import Any

_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]*(.*))?$")
_LIST_RE = re.compile(r"^[ \t]*-[ \t]+(.*)$")


def _quoted(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value[0:1] in {'"', "'"} and value[-1:] == value[0:1]:
        return _quoted(value)
    low = value.lower()
    if low in {"true", "false"}:
        return low == "true"
    if low in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        try:
            return int(value)
        except ValueError:
            pass
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?", value):
        try:
            return float(value)
        except ValueError:
            pass
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        row = next(csv.reader(io.StringIO(inner), skipinitialspace=True))
        return [_scalar(item) for item in row]
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        # Empty lines and full-line comments are harmless in our metadata subset.
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        list_match = _LIST_RE.match(raw_line)
        if list_match:
            if current_list_key is None:
                raise ValueError(f"front matter line {line_no}: list item without a key")
            data[current_list_key].append(_scalar(list_match.group(1)))
            continue

        if raw_line[:1].isspace():
            raise ValueError(
                f"front matter line {line_no}: nested YAML is outside the supported Koali metadata subset"
            )

        key_match = _KEY_RE.match(raw_line)
        if not key_match:
            raise ValueError(f"front matter line {line_no}: unsupported syntax: {raw_line!r}")

        key, rest = key_match.group(1), key_match.group(2)
        rest = "" if rest is None else rest
        if rest.strip() == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = _scalar(rest)
            current_list_key = None

    return data
'''


def patch_python_file(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    text = original

    # Remove yaml from comma-style imports, e.g. `import re, sys, yaml, json`.
    text = re.sub(
        r"^import ([^\n]*)$",
        lambda m: "import " + ", ".join(
            part.strip() for part in m.group(1).split(",") if part.strip() != "yaml"
        ),
        text,
        flags=re.MULTILINE,
    )
    # Remove standalone import if present.
    text = re.sub(r"^import yaml\s*\n", "", text, flags=re.MULTILINE)

    if "yaml.safe_load(" in text:
        text = text.replace("yaml.safe_load(", "parse_frontmatter(")

    if "parse_frontmatter(" in text and "from frontmatter_stdlib import parse_frontmatter" not in text:
        # Scripts are executed as files (`python scripts/foo.py`), so the scripts
        # directory is on sys.path and a sibling module imports cleanly.
        lines = text.splitlines()
        insert_at = 0
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        # Keep `from __future__` first if one exists.
        while insert_at < len(lines) and (
            lines[insert_at].startswith("from __future__") or not lines[insert_at].strip()
        ):
            insert_at += 1
        lines.insert(insert_at, "from frontmatter_stdlib import parse_frontmatter")
        text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not VALIDATOR.exists():
        print(f"ERROR: {VALIDATOR} not found. Run this patch from the V2.2 repository root.", file=sys.stderr)
        return 2

    SCRIPTS.mkdir(parents=True, exist_ok=True)
    HELPER.write_text(HELPER_CONTENT, encoding="utf-8")

    changed_validator = patch_python_file(VALIDATOR)
    changed_builder = patch_python_file(BUILDER) if BUILDER.exists() else False

    remaining = []
    for path in (VALIDATOR, BUILDER):
        if path.exists() and re.search(r"(^|\n)(?:import\s+yaml\b|.*\byaml\.safe_load\()", path.read_text(encoding="utf-8")):
            remaining.append(str(path))

    if remaining:
        print("ERROR: PyYAML references remain in: " + ", ".join(remaining), file=sys.stderr)
        return 3

    print("Koali Netlify/PyYAML fix applied.")
    print(f"  helper:    {HELPER.relative_to(ROOT)}")
    print(f"  validator: {'patched' if changed_validator else 'already compatible'}")
    if BUILDER.exists():
        print(f"  offline:   {'patched' if changed_builder else 'already compatible'}")
    print("Next: python scripts/validate-v2.py && npm run build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
