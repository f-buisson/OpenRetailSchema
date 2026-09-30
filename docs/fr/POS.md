# Intégrations POS — état des preuves

[Documentation de référence (anglais)](../POS_INTEGRATIONS.md) · [Accueil](README.md) · [Contribuer (anglais)](../../CONTRIBUTING.md)

OpenRetailSchema vise à rendre les intégrations aux logiciels de caisse réutilisables. Il faut distinguer **trois niveaux** : une API officiellement documentée, une connexion éprouvée dans un autre produit et un connecteur OpenRetailSchema effectivement testé et publié.

**Loyverse fonctionne déjà par jeton dans un autre logiciel F-Buisson**, et ce fonctionnement a été vérifié sur un vrai compte le **29 septembre 2026**. La lecture du catalogue (43 articles, 43 variantes), la synchronisation incrémentale et la conservation des champs manquants ont été observées. Il ne s'agit **pas encore** d'une certification du futur connecteur OpenRetailSchema ni d'une validation OAuth.

Ces tests ont révélé des pièges essentiels : un prix ou un stock absent ne vaut jamais zéro, la TVA inconnue doit rester inconnue, la devise peut être livrée sous forme d'objet (THB sur le compte étudié) et une demande d'historique trop ancien peut produire un **HTTP 402** lié à l'abonnement plutôt qu'au jeton. Le compte de test a également servi à éprouver séparément la normalisation de ventes et de remboursements ; le branchement général reste à réaliser.

La documentation officielle de [Loyverse](https://developer.loyverse.com/docs/) confirme deux modes d'autorisation : le jeton personnel et OAuth 2.0. **Un jeton personnel doit être considéré comme très sensible**, même si nos essais n'effectuaient que des lectures. Pour une application publique multi-commerçants, l'objectif est OAuth avec les autorisations nécessaires.

### Autres POS : contributions recherchées

Nous recherchons des informations **publiques et légalement partageables** sur d'autres plateformes :

- [Square](https://developer.squareup.com/reference/square) : catalogues, commandes, stocks et autorisations.
- [Shopify](https://shopify.dev/docs/api/admin-graphql/latest) : données POS accessibles depuis l'API Admin, autorisations et pagination.
- [Lightspeed Retail X-Series](https://x-series-api.lightspeedhq.com/docs/introduction) : méthodes d'autorisation et limites d'accès.
- [Clover](https://docs.clover.com/dev/docs/making-rest-api-calls) : API REST, sandbox et autorisations OAuth.
- [Odoo](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html) : API externe JSON-2 (selon la formule d'abonnement et les modèles accessibles).
- [Epos Now](https://developer.eposnowhq.com/Docs/Authentication) : documentation d'authentification des appareils/API.
- **StoreLine / NCR Voyix** : documentation vérifiable ou description d'export autorisé ; ne pas présumer une API StoreLine publique.
- Tout autre POS disposant d'une API ou d'un export CSV documenté.

Pour contribuer, [ouvrez une proposition de connecteur](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose) en indiquant l'URL officielle, les ressources réellement disponibles, les limitations éventuelles, les formats de devise/TVA, les remboursements et la manière d'horodater les transactions. Des **exemples entièrement inventés** sont bienvenus pour construire nos tests.

**Ne partagez jamais de jeton, mot de passe, identifiant de client, données RH, export réel ou documentation confidentielle.** Les traductions françaises facilitent la participation, mais les spécifications anglaises font foi.
