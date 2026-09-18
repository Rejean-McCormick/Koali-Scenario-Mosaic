"""Minimal YAML-front-matter reader for Koali scenario metadata.

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
