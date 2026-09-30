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

## Strict import by default

Any invalid row blocks output, so pre-existing output remains unchanged. To intentionally export valid rows alongside row-numbered rejection messages, add `--allow-partial`. Existing outputs require an explicit `--overwrite`; output may not be the CSV or mapping file. Atomic replacement avoids leaving partial JSONL files after an interrupted write.

The CLI reports counts and rejection codes on the local machine. Do not share outputs or source files containing real store information in public issues; use [synthetic contributions](../CONTRIBUTING.md).

## Current limitations

This is a local product adapter, **not** a verified StoreLine, Loyverse, Square or other POS connector. No timezone or date guessing is needed for this product-only import. It does not resolve product-tax basis, purchase cost, historical prices, sale events or employee schedules. Future sales imports will require explicit timestamps/timezones and refund semantics.
