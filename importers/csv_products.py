# SPDX-License-Identifier: Apache-2.0
"""Deterministic CSV product normalization with explicit mapping, no guessed fields."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/v0.1/record.schema.json"
FIELDS = {"external_id", "name", "sku", "barcode", "sale_price", "currency"}
REQUIRED_FIELDS = {"external_id", "name"}
CONFIG_KEYS = {"version", "resource", "store_id", "source_namespace", "delimiter", "encoding", "decimal_separator", "columns", "currency"}
DECIMAL_PATTERNS = {
    ".": re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$"),
    ",": re.compile(r"^(?:0|[1-9][0-9]*)(?:,[0-9]+)?$"),
}


@dataclass(frozen=True)
class RowIssue:
    row: int
    code: str
    field: str | None = None

    def as_dict(self) -> dict:
        result = {"row": self.row, "code": self.code}
        if self.field:
            result["field"] = self.field
        return result


class MappingError(ValueError):
    """Invalid configuration, not an individual CSV record."""


def validate_mapping(mapping: object) -> dict:
    if not isinstance(mapping, dict) or set(mapping) - CONFIG_KEYS:
        raise MappingError("unknown_or_invalid_config_keys")
    if mapping.get("version") != 1 or mapping.get("resource") != "product":
        raise MappingError("unsupported_mapping_version_or_resource")
    for key in ("store_id", "source_namespace"):
        if not isinstance(mapping.get(key), str) or not mapping[key].strip():
            raise MappingError("invalid_" + key)
    if mapping.get("delimiter", ",") not in {",", ";", "\t", "|"}:
        raise MappingError("invalid_delimiter")
    if mapping.get("encoding", "utf-8-sig") not in {"utf-8", "utf-8-sig"}:
        raise MappingError("invalid_encoding")
    if mapping.get("decimal_separator", ".") not in DECIMAL_PATTERNS:
        raise MappingError("invalid_decimal_separator")
    columns = mapping.get("columns")
    if not isinstance(columns, dict) or not REQUIRED_FIELDS <= set(columns) or set(columns) - FIELDS:
        raise MappingError("invalid_columns")
    if any(not isinstance(value, str) or not value.strip() for value in columns.values()):
        raise MappingError("invalid_column_name")
    if len(set(columns.values())) != len(columns):
        raise MappingError("duplicate_column_mapping")
    if "sale_price" in columns:
        if ("currency" in columns) == ("currency" in mapping):
            raise MappingError("one_currency_source_required_for_prices")
    elif "currency" in columns or "currency" in mapping:
        raise MappingError("currency_without_price")
    if "currency" in mapping and not _currency(mapping["currency"]):
        raise MappingError("invalid_fixed_currency")
    return mapping


def _currency(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Z]{3}", value))


def _price(text: str, separator: str) -> str | None:
    value = text.strip()
    if not value:
        return None
    if not DECIMAL_PATTERNS[separator].fullmatch(value):
        raise ValueError("invalid_price")
    try:
        price = Decimal(value.replace(",", "."))
    except InvalidOperation:
        raise ValueError("invalid_price") from None
    if not price.is_finite() or price.is_signed():
        raise ValueError("invalid_price")
    return format(price, "f")


def _record(row: dict[str, str], mapping: dict) -> dict:
    columns = mapping["columns"]
    source_id = row[columns["external_id"]].strip()
    name = row[columns["name"]].strip()
    if not source_id:
        raise RowValueError("missing_required", "external_id")
    if not name:
        raise RowValueError("missing_required", "name")
    # Length-prefixed tuple encoding via JSON avoids namespace/store/id ambiguity.
    identity = json.dumps([mapping["source_namespace"], mapping["store_id"], source_id], ensure_ascii=True)
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    result = {
        "schema_version": "0.1.0", "entity_type": "product", "id": "csv:" + digest,
        "store_id": mapping["store_id"], "source": {"provider": "csv:" + mapping["source_namespace"], "external_id": source_id},
        "name": name,
    }
    for field in ("sku", "barcode"):
        if field in columns:
            value = row[columns[field]].strip()
            if value:
                result[field] = value  # Keep identifiers as text, including leading zeros.
    if "sale_price" in columns:
        try:
            amount = _price(row[columns["sale_price"]], mapping.get("decimal_separator", "."))
        except ValueError:
            raise RowValueError("invalid_price", "sale_price") from None
        if amount is not None:
            currency = row[columns["currency"]].strip() if "currency" in columns else mapping["currency"]
            if not _currency(currency):
                raise RowValueError("invalid_currency", "currency")
            result["sale_price"] = {"amount": amount, "currency": currency}
    return result


class RowValueError(ValueError):
    def __init__(self, code: str, field: str | None = None):
        super().__init__(code)
        self.code = code
        self.field = field


def import_products(source_path: Path, mapping: dict, schema_path: Path = SCHEMA_PATH,
                    *, max_rows: int = 100_000) -> tuple[list[dict], list[RowIssue]]:
    """Return valid canonical records and sanitized issues; never log source cells.

    The caller decides whether partial success is acceptable. Unknown prices
    are omitted; a genuine zero remains a decimal zero.
    """
    validate_mapping(mapping)
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or max_rows < 1:
        raise MappingError("invalid_max_rows")
    with schema_path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records, issues, seen = [], [], set()
    with source_path.open(newline="", encoding=mapping.get("encoding", "utf-8-sig")) as handle:
        reader = csv.DictReader(handle, delimiter=mapping.get("delimiter", ","), strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or any(not h for h in reader.fieldnames):
            raise MappingError("invalid_or_duplicate_headers")
        missing = set(mapping["columns"].values()) - set(reader.fieldnames)
        if missing:
            # Do not print values from source data or silently guess alternative headers.
            raise MappingError("missing_mapped_headers")
        try:
            for logical_row, row in enumerate(reader, start=2):
                if logical_row - 1 > max_rows:
                    raise MappingError("max_rows_exceeded")
                if None in row or any(value is None for value in row.values()):
                    issues.append(RowIssue(logical_row, "wrong_column_count"))
                    continue
                try:
                    record = _record(row, mapping)
                    identity = record["source"]["external_id"]
                    if identity in seen:
                        issues.append(RowIssue(logical_row, "duplicate_external_id", "external_id"))
                        continue
                    seen.add(identity)
                    if not validator.is_valid(record):
                        issues.append(RowIssue(logical_row, "schema_invalid"))
                        continue
                    records.append(record)
                except RowValueError as exc:
                    issues.append(RowIssue(logical_row, exc.code, exc.field))
        except csv.Error as exc:
            raise MappingError("malformed_csv") from None
    return records, issues
