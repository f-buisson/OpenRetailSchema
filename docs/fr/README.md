# OpenRetailSchema — présentation

[English (canonical documentation)](../../README.md) · [Import CSV](CSV.md) · [Intégrations POS et contributions](POS.md) · [Exécution des connecteurs](CONNECTOR_EXECUTION.md) · [Sélection des adaptateurs](ADAPTER_SELECTION.md) · [Architecture (EN)](../ARCHITECTURE.md) · [Roadmap (EN)](../ROADMAP.md) · [Contribuer](CONTRIBUTING.md) · [Apache 2.0](../../LICENSE)

**Un schéma commun, indépendant des éditeurs, pour faciliter l’intégration des logiciels de caisse (POS).**

OpenRetailSchema vise à permettre à plusieurs applications d’exploiter les données de différents POS sans réécrire à chaque fois toutes les correspondances de données. Le standard est public et le projet est destiné aux développeurs extérieurs comme aux produits F-Buisson.

**État : développement initial.** Les premiers contrats concernent les ventes, les produits et les indicateurs agrégés d’activité. Le validateur fonctionne localement ; aucun connecteur POS réel n’est encore certifié **dans ce dépôt**. Une connexion Loyverse par jeton a cependant été éprouvée sur un vrai compte dans un autre logiciel F-Buisson : [preuves et limites documentées](POS.md).

### Principes

- Normaliser les données tout en conservant **l’origine de chaque enregistrement**.
- Ne jamais transformer une donnée absente en zéro ni inventer un prix, un client ou une heure.
- Conserver les montants sous forme de chaînes décimales avec leur devise.
- Maintenir des schémas versionnés et des exemples synthétiques reproductibles.
- Construire les connecteurs progressivement, en annonçant les capacités réellement vérifiées.
- Préserver la confidentialité des données et des identifiants des magasins.

### Participer

Nous recherchons de la [documentation officielle, des correspondances de champs et des exemples fictifs](POS.md) pour d'autres POS. Ne publiez jamais de jeton, d'export réel ou de données clients dans une issue.

### État des principales briques

1. Contrat JSON commun v0.1 publié et validation locale disponible.
2. Import CSV d'articles disponible, avec mapping explicite et [guide pratique](CSV.md).
3. Connecteur Loyverse expérimental en lecture seule couvert par des tests synthétiques ; validation directe sur compte autorisé encore nécessaire.
4. Connecteur Square en lecture seule déjà présent et testé synthétiquement pour les surfaces principales ; test Sandbox ou vendeur autorisé encore nécessaire.
5. Les futurs connecteurs passent par une [grille de sélection explicite](ADAPTER_SELECTION.md) avant tout développement ; StoreLine reste différé tant que son interface exacte et son autorisation ne sont pas établies.

### Essayer le validateur

Avec Python installé :

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_sale.json
python -m unittest discover -s tests -v
```

La **documentation anglaise fait référence** en cas de divergence. Les traductions françaises des principaux guides évolueront avec le projet.

Site : [f-buisson.com](https://f-buisson.com).
