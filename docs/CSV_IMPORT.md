# Generic CSV import: products (experimental)

[Home](../README.md) · [Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md) · [French guide](fr/CSV.md)

The first generic CSV importer produces **OpenRetailSchema v0.1 canonical product records** from a **local, explicitly mapped product CSV**. It does not contact a POS, infer field types, read employee records, update inventory, import sales, or store raw records. Other entity types are future work.

This is useful when a POS lacks an authorized API or offers only file exports.

## Local reproducible example

Python 3.10+ is required. Install dependencies locally, then run:

```bash
python -m pip install -r requirements-dev.txt
mkdir -p local-data
python scripts/import_csv.py \
  --input examples/csv/products.csv \
  --mapping examples/csv/products_mapping.json \
  --output local-data/imported-products.jsonl
python -m unittest discover -s tests -v
```

`local-data/` is ignored by Git. All committed input rows are fictional.

The JSONL output contains one canonical JSON product per line. Run validation on a line as an individual JSON object, or use `importers.csv_products.import_products()`, which checks each record against the versioned schema.

## Mapping file

- `version: 1` and `resource: "product"` explicitly identify the mapping contract.
- `store_id` identifies the destination store and `source_namespace` scopes the external export format. Use stable, **non-secret** values. A SHA-256 digest of namespace, store and external ID forms a repeatable canonical record ID. Different stores or export providers do not accidentally collide.
- `columns.external_id` and `columns.name` are mandatory. Optional mappings: `sku`, `barcode`, `sale_price`, `currency`.
- If `sale_price` is mapped, define **exactly one** currency source: a fixed uppercase ISO 4217 `currency` in the mapping **or** a mapped per-row `columns.currency`. A missing price omits `sale_price` entirely; it is **not** zero. A present price requires a valid currency.
- `decimal_separator` must be explicitly set to `"." ` or `","` for non-default formats. Grouping separators, scientific notation, negative prices and implicit conversions are intentionally rejected.
- `delimiter` supports comma, semicolon, tab and vertical bar. `encoding` is `utf-8` or `utf-8-sig` (default, BOM-tolerant). No encoding guessing or unbounded rows.
- SKU and barcode are always **strings**: leading zeroes survive.
- Duplicate source IDs in one file, inconsistent column counts, missing headers and invalid rows produce sanitized row-numbered error codes; real cell values are never copied into errors.

## Sales and activity time mapping contract

Sales/activity CSV import is **not implemented yet**. The following rules define the mapping boundary that an implementation and its fixtures must satisfy; they do not certify an importer that does not exist.

- A sale maps its event column to canonical `occurred_at`. An activity row maps two columns to `interval_start` and `interval_end`.
- Canonical event/interval timestamps must be RFC 3339 date-times with an explicit numeric UTC offset or `Z`. A naive local timestamp must never be emitted as canonical data.
- A source timestamp that already contains an offset is authoritative for that instant. The importer must preserve its instant and must not replace its offset using a store timezone.
- If source timestamps are local wall-clock values without offsets, the mapping must explicitly provide an IANA timezone such as `Europe/Paris`. No timezone may be inferred from locale, currency, country, store name, machine settings or the current date.
- Local wall-clock conversion must use timezone rules for the date being imported, not today's offset. A nonexistent local time during a DST spring-forward transition is rejected.
- An ambiguous local time during a DST fall-back transition is rejected unless the mapping/input supplies an explicit disambiguation that identifies the intended offset/instant. Choosing the first or second occurrence silently is forbidden.
- Activity `interval_start` and `interval_end` are converted independently and then ordered by absolute instant. Local clock text alone is not sufficient to decide ordering across an offset change.
- `store_timezone`, when emitted for an activity record, records the explicitly configured IANA zone; it does not replace the required offsets in `interval_start` or `interval_end`.
- Missing timestamp/timezone/disambiguation data is an import rejection, not a zero value, midnight default, UTC default or guessed offset.
- Mapping configuration must distinguish source format explicitly. An implementation may support offset-bearing RFC 3339 directly and explicitly declared local formats, but it must not auto-detect competing date orders such as `03/04/2026`.

These rules deliberately separate a source's civil-time context (IANA timezone) from the canonical instant (offset-bearing timestamp). Synthetic fixtures are required before the sales/activity importer can be considered implemented.

## Strict import by default

Any invalid row blocks output, so pre-existing output remains unchanged. To intentionally export valid rows alongside row-numbered rejection messages, add `--allow-partial`. Existing outputs require an explicit `--overwrite`; output may not be the CSV or mapping file. Atomic replacement avoids leaving partial JSONL files after an interrupted write.

The CLI reports counts and rejection codes on the local machine. Do not share outputs or source files containing real store information in public issues; use [synthetic contributions](../CONTRIBUTING.md).

## Current limitations

This is a local product adapter, **not** a verified StoreLine, Loyverse, Square or other POS connector. Product import needs no date/time mapping. Sales/activity import remains unimplemented; the contract above exists so its future implementation cannot silently guess timestamps, timezones or DST offsets. The current importer also does not resolve product-tax basis, purchase cost, historical prices, sale events or employee schedules.
