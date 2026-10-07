# Contribuer à OpenRetailSchema

[Canonical English guide](../../CONTRIBUTING.md) · [Intégrations POS](POS.md) · [Exécution des connecteurs](CONNECTOR_EXECUTION.md) · [Sélection des adaptateurs](ADAPTER_SELECTION.md) · [Licence Apache 2.0](../../LICENSE)

Merci de participer à un projet destiné à faciliter les échanges de données entre logiciels de caisse et applications métier. **Les spécifications, les interfaces publiques, les descriptions des PR et la documentation de référence sont en anglais.** Le français est une langue secondaire bienvenue pour les discussions et les traductions.

## Proposer un autre logiciel de caisse

Vous pouvez apporter de la valeur au projet **sans écrire de code**. Nous recherchons de la documentation officielle publique et des informations légalement communicables sur Square, Shopify POS, Lightspeed, StoreLine/NCR Voyix et toute autre caisse.

[Créer une proposition de connecteur POS](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose)

Indiquez le modèle exact et, si possible, les liens officiels de l'API ou de l'export CSV, les ressources accessibles en lecture (articles, prix, TVA, stocks, tickets, remboursements, salariés), les autorisations nécessaires, la pagination, les restrictions d'abonnement et les subtilités de devises ou de fuseaux horaires.

Différenciez clairement **la documentation publique**, **les tests synthétiques du dépôt**, **les observations sur un compte autorisé hors connecteur** et **les tests directs du connecteur OpenRetailSchema**. Les données absentes ne doivent jamais devenir des valeurs nulles présentées comme vraies ou des zéros inventés.

## Sécurité et propriété

Ne publiez jamais de jeton, mot de passe, secret OAuth, identité de commerçant, donnée client/salarié, export réel, documentation confidentielle ni code propriétaire sans autorisation explicite. Construisez plutôt de petites réponses et des mappings entièrement **fictifs**, qui permettront de reproduire des cas difficiles sans exposer un magasin. Contactez le responsable à l'adresse du [guide de sécurité](../../SECURITY.md) pour un problème sensible.

Vous devez être autorisé à soumettre les contributions. Indiquez la provenance du code, des exemples et des affirmations techniques ; tout élément destiné à être intégré doit être votre travail original ou être redistribuable sous des conditions compatibles avec la [licence Apache 2.0](../../LICENSE), avec les mentions requises. Les noms commerciaux restent la propriété de leurs titulaires respectifs.

## Tests locaux

Depuis la racine du dépôt, avec Python 3.10 ou supérieur :

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_sale.json examples/valid_product.json examples/valid_activity_metric.json
python -m unittest discover -s tests -v
```

Joignez les commandes réellement exécutées et leurs résultats dans votre PR, ajoutez des témoins synthétiques et documentez tout changement incompatible du schéma. Le workflow public `Tests` s'exécute aussi sur les PR vers `main` et sur `main` ; un résultat vert prouve l'état des régressions du dépôt, pas l'accès réel à un fournisseur ni la certification d'un connecteur.

Le [guide anglais](../../CONTRIBUTING.md) reste la source canonique pour les règles de contribution.
