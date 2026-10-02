#!/usr/bin/env python3
"""Validate OpenRetailSchema v0.1 records offline, without calling POS APIs."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit("Missing dependency: install with python -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "v0.1" / "record.schema.json"


def _has_explicit_offset(value: str) -> bool:
    """Canonical event timestamps must include Z or an explicit UTC offset."""
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _sale_currencies(document: dict) -> set[str]:
    """Return currencies reported by monetary fields within one sale."""
    currencies = set()
    for field in ("gross_total", "net_total", "tax_total"):
        money = document.get(field)
        if isinstance(money, dict) and isinstance(money.get("currency"), str):
            currencies.add(money["currency"])
    for line in document.get("lines", []):
        if not isinstance(line, dict):
            continue
        money = line.get("gross_total")
        if isinstance(money, dict) and isinstance(money.get("currency"), str):
            currencies.add(money["currency"])
    return currencies


def semantic_errors(document: object) -> list[str]:
    """Small cross-field checks JSON Schema cannot express clearly."""
    if not isinstance(document, dict):
        return []
    errors = []
    for field in ("occurred_at", "interval_start", "interval_end"):
        if field in document and not _has_explicit_offset(document[field]):
            errors.append(f"{field}: date-time must include Z or an explicit UTC offset")
    if document.get("entity_type") == "sale":
        currencies = _sale_currencies(document)
        if len(currencies) > 1:
            errors.append("currency: all monetary values in a sale must use one currency")
    if document.get("entity_type") == "activity_metric":
        start = document.get("interval_start")
        end = document.get("interval_end")
        if _has_explicit_offset(start) and _has_explicit_offset(end):
            start_instant = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_instant = datetime.fromisoformat(end.replace("Z", "+00:00"))
            if end_instant <= start_instant:
                errors.append("interval_end: must represent an instant after interval_start")
    return errors


def validate_file(document_path: Path, validator: Draft202012Validator) -> bool:
    try:
        with document_path.open(encoding="utf-8") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL {document_path}: {exc}", file=sys.stderr)
        return False

    errors = sorted(validator.iter_errors(document), key=lambda e: (list(map(str, e.absolute_path)), e.message))
    semantics = semantic_errors(document) if not errors else []
    if errors or semantics:
        print(f"FAIL {document_path}", file=sys.stderr)
        for error in errors:
            at = "/".join(str(part) for part in error.absolute_path) or "/"
            print(f"  {at}: {error.message}", file=sys.stderr)
        for error in semantics:
            print(f"  {error}", file=sys.stderr)
        return False
    print(f"PASS {document_path}")
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate vendor-neutral retail records locally")
    parser.add_argument("documents", nargs="+", type=Path, help="JSON record files to validate")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args(argv)
    try:
        with args.schema.open(encoding="utf-8") as stream:
            schema = json.load(stream)
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid schema: {exc}", file=sys.stderr)
        return 2

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    success = True
    for document in args.documents:
        if not validate_file(document, validator):
            success = False
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
