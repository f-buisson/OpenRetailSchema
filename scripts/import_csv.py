#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Import product CSV via an explicit mapping; output locally, atomically."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from importers.csv_products import MappingError, import_products


def atomic_jsonl(destination: Path, records: list[dict], *, overwrite: bool) -> None:
    if destination.exists() and not overwrite:
        raise FileExistsError("output_already_exists")
    if not destination.parent.is_dir():
        raise FileNotFoundError("output_directory_missing")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         prefix=".ors-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if destination.exists() and not overwrite:
            raise FileExistsError("output_already_exists")
        os.replace(temporary, destination)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Import a generic product CSV using a fully explicit mapping")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-partial", action="store_true", help="Export valid rows even when other rows fail")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    sources = {args.input.resolve(), args.mapping.resolve()}
    if args.output.resolve() in sources:
        print("ERROR output_must_differ_from_inputs", file=sys.stderr)
        return 2
    try:
        with args.mapping.open(encoding="utf-8") as handle:
            mapping = json.load(handle)
        records, issues = import_products(args.input, mapping)
        if issues:
            for issue in issues:
                print(json.dumps(issue.as_dict(), separators=(",", ":")), file=sys.stderr)
        if issues and not args.allow_partial:
            print(f"ABORT {len(issues)} invalid rows; no output written", file=sys.stderr)
            return 1
        atomic_jsonl(args.output, records, overwrite=args.overwrite)
    except (OSError, ValueError, MappingError, json.JSONDecodeError) as exc:
        # No source cells or user-provided paths are displayed by design.
        error_code = str(exc) if isinstance(exc, (MappingError, FileExistsError)) else "import_failed"
        print("ERROR " + error_code, file=sys.stderr)
        return 2
    print(f"OK {len(records)} products, {len(issues)} rejected rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
