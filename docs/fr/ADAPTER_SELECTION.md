# Grille de sélection des adaptateurs

[English canonical](../ADAPTER_SELECTION.md) · [État des intégrations POS](POS.md) · [Roadmap (EN)](../ROADMAP.md)

OpenRetailSchema ne démarre pas un nouveau connecteur simplement parce qu'une API existe. Un fournisseur n'est sélectionné que lorsque les preuves permettent d'implémenter une surface minimale de lecture sans inventer de sémantique métier et qu'un chemin réaliste de vérification autorisée existe.

## Conditions obligatoires

Avant tout début d'implémentation, un futur connecteur doit satisfaire toutes les conditions suivantes :

1. **Surface fournisseur exacte** — produit/édition et version actuelle de l'API ou de l'export identifiés dans une documentation publique officielle.
2. **Compatibilité de lecture minimale** — au moins une capacité commune peut être alimentée sans inventer les valeurs absentes.
3. **Chemin d'accès autorisé** — sandbox, magasin de test, appareil API, abonnement éligible ou autre moyen légitime de vérification connu et réaliste.
4. **Sémantique d'exécution** — pagination, limites d'accès, fenêtres historiques et règles de reprise/erreur suffisamment documentées pour construire des lectures bornées.
5. **Sémantique canonique** — identité, montants/devise, taxes, horodatages, remboursements/retours et distinction absence-zéro documentés ou explicitement laissés non pris en charge.
6. **Reproductibilité synthétique** — des données entièrement fictives peuvent couvrir le mapping et les cas négatifs/limites sans publier de vraies données fournisseur.
7. **Coût de maintenance** — versionnement, variations d'abonnement et complexité spécifique restent assez bornés pour ne pas créer un second contrat commun parallèle.

Si une condition manque, le fournisseur reste **différé**. Différé ne signifie pas incompatible : cela signifie que les preuves ou l'accès sont insuffisants pour une implémentation responsable.

## Décision actuelle — 7 octobre 2026

**Aucun fournisseur supplémentaire n'est sélectionné.** Square est déjà l'implémentation active après Loyverse et doit encore être exécuté contre un Sandbox ou un compte vendeur autorisé. Commencer un troisième connecteur avant cette preuve ajouterait de la maintenance sans fermer le chemin de référence actuel.

| Fournisseur | Documentation | Chemin de test autorisé | Confiance sémantique canonique | Coût maintenance/accès | Décision | Prochaine preuve |
| --- | --- | --- | --- | --- | --- | --- |
| Square | Forte ; implémentation déjà testée synthétiquement | Sandbox/compte vendeur non encore exécuté ici | Forte pour produits/ventes/remboursements actuels ; montants conservateurs | Modéré | **Poursuivre seulement la certification** | Exécution autorisée du connecteur, distincte d'OAuth/Marketplace |
| Clover | Contrat REST public solide ; sandbox et OAuth documentés | Sandbox existant mais non exécuté ici | Bonne pour pagination, horodatages et limites de commandes ; mappings à fabriquer | Modéré | **Premier candidat à réévaluer après Square** | Test sandbox autorisé + mappings fictifs produits/commandes/paiements |
| Lightspeed Retail X-Series | API versionnée, scopes, pagination et limites bien documentés | Accès magasin de test non encore disponible | Bonnes preuves transport ; mappings canoniques non exécutés | Modéré | Différé | Magasin de test autorisé + mappings fictifs produits/ventes/magasins/stocks |
| Shopify POS | Documentation Admin GraphQL solide | Accès de développement plausible mais preuve POS absente ici | Origine POS encore non résolue | Modéré à élevé | Différé | Discriminateur POS officiel stable + preuve autorisée |
| Epos Now | V4 documente produits/stocks/transactions | Nécessite un appareil API et une licence appareil | Sémantique fuseau/offset de transaction non résolue | Modéré | Différé | Test appareil API autorisé + sémantique temporelle + mappings fictifs |
| Odoo POS | JSON-2 documenté | Nécessite une base éligible au plan Custom | Surface technique variable selon la base | Élevé | Différé | Inspection `/doc` d'une base autorisée + mappings fictifs |
| NCR Voyix / StoreLine | Interface publique exacte non établie | Aucun accès autorisé établi | Inconnue | Inconnu/élevé | Différé | Documentation publiquement partageable ou spécification d'export autorisée et expurgée |

## Règle de réévaluation

Un fournisseur différé n'est réévalué que lorsqu'une nouvelle preuve ferme l'une de ses lacunes nommées. Le simple passage du temps ou l'existence d'une implémentation dans un autre dépôt ne suffit pas.

Si plusieurs fournisseurs deviennent éligibles simultanément, privilégier celui qui :

1. élimine le plus de travail dupliqué dans les produits aval ;
2. possède le meilleur chemin de test autorisé ;
3. respecte le contrat commun existant avec le moins d'hypothèses propres au fournisseur ;
4. présente le coût de versionnement et d'accès le plus faible à maintenir.

L'ordre futur ne change que lorsque les preuves du dépôt changent.