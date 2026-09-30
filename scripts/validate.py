#!/usr/bin/env python3
"""Validate OpenRetailSchema v0.1 records offline, without calling POS APIs."""
import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit("Missing dependency: install with python -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "v0.1" / "record.schema.json"


def validate_file(document_path: Path, validator: Draft202012Validator) -> bool:
    try:
        with document_path.open(encoding="utf-8") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL {document_path}: {exc}", file=sys.stderr)
        return False

    errors = sorted(validator.iter_errors(document), key=lambda e: (list(map(str, e.absolute_path)), e.message))
    if errors:
        print(f"FAIL {document_path}", file=sys.stderr)
        for error in errors:
            at = "/".join(str(part) for part in error.absolute_path) or "/"
            print(f"  {at}: {error.message}", file=sys.stderr)
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
