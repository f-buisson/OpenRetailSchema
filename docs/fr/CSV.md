# Import CSV générique — articles (expérimental)

[English (canonical guide)](../CSV_IMPORT.md) · [Accueil français](README.md) · [Code](../../importers/csv_products.py)

Ce premier importeur transforme un **catalogue d'articles CSV local** en objets « product » du schéma OpenRetailSchema v0.1. Il peut servir pour des logiciels de caisse qui fournissent un export plutôt qu'une API accessible. Il ne lit pas encore les ventes, les employés ni les stocks et **n'est pas un connecteur POS certifié**.

Le mapping est explicite : aucun nom de colonne, aucune devise et aucun séparateur décimal ne sont devinés. Les montants sont stockés en chaînes décimales pour conserver la précision ; un prix absent est **omis**, tandis que `0,00` reste un vrai zéro. Les SKU et codes-barres sont conservés comme du texte, y compris leurs zéros initiaux.

## Essai local sur des données entièrement fictives

Installer Python 3.10 ou supérieur, puis lancer depuis la racine du dépôt :

```bash
python -m pip install -r requirements-dev.txt
mkdir -p local-data
python scripts/import_csv.py \
  --input examples/csv/products.csv \
  --mapping examples/csv/products_mapping.json \
  --output local-data/imported-products.jsonl
python -m unittest discover -s tests -v
```

Le dossier `local-data/` est exclu de Git. **Ne publiez jamais d'export réel**, même pour demander de l'aide. Vous pouvez fournir un petit fichier dont toutes les lignes sont inventées.

## Ce qui est paramétrable

- `store_id` : magasin de destination.
- `source_namespace` : espace d'identification stable de l'export ; ne pas y placer de secret.
- `columns` : correspondance obligatoire pour la référence source et le nom, facultative pour SKU, code-barres, prix et devise par ligne.
- `currency` : devise fixe si le prix est mappé et qu'il n'existe pas de colonne devise. La devise n'est jamais déduite du pays.
- `delimiter` et `decimal_separator` : séparateur du CSV et séparateur décimal, configurés sans ambiguïté.
- `encoding` : UTF-8 ou UTF-8 avec prise en charge du BOM.

Par défaut, **une seule ligne invalide empêche la création du fichier de sortie**, sans écraser le précédent. L'option `--allow-partial` permet d'exporter uniquement les lignes valides ; `--overwrite` est nécessaire si la sortie existe déjà. Les erreurs indiquent le numéro de ligne et un code, jamais le contenu des cellules.

Le [guide anglais détaillé](../CSV_IMPORT.md) et les [tests](../../tests/test_csv_products.py) restent les références pour l'implémentation actuelle.
