# Contrat d'exécution des connecteurs

[English canonical](../CONNECTOR_EXECUTION.md) · [État des intégrations POS](POS.md) · [Sélection des adaptateurs](ADAPTER_SELECTION.md)

Ce document traduit les règles communes d'exécution des connecteurs en lecture seule. La version anglaise reste canonique. Un connecteur fournisseur peut exposer des détails supplémentaires, mais les consommateurs peuvent s'appuyer sur les règles communes ci-dessous.

## Pagination

Les curseurs de pagination sont un **état de transport éphémère**. Un curseur sert uniquement à poursuivre le parcours fournisseur en cours. Si `has_more=true`, le curseur doit être non vide. Un curseur de pagination n'est jamais un point de reprise durable et ne doit pas être enregistré ou présenté comme une progression source.

## Points de reprise

Un point de reprise est une **progression source durable appartenant à l'appelant**. Il doit être explicite et non vide. Sa valeur propre au fournisseur et ses règles d'avancement appartiennent au contrat du connecteur ; le consommateur ne doit jamais le déduire d'un curseur de pagination.

Un connecteur ne peut avancer cette progression durable qu'après le parcours et le traitement réussis des enregistrements qu'elle couvre. OpenRetailSchema n'ajoute pas de stockage persistant uniquement pour conserver ces points : la persistance reste la responsabilité du consommateur tant qu'un contrat de stockage concret n'existe pas dans le dépôt.

## Limites et nouvelles tentatives

Une réponse `429` appartient à la classe stable `rate_limit` et peut être retentée. Lorsqu'un fournisseur expose un délai `Retry-After`, sa représentation dans le contrat commun doit être explicite et non négative. Le contrat commun n'invente aucun délai lorsque le fournisseur n'en fournit pas.

Les erreurs fournisseur `5xx` appartiennent à `provider_unavailable` et peuvent être retentées. Le contrat générique n'impose volontairement ni nombre de tentatives, ni calendrier de backoff, ni jitter : chaque connecteur peut employer une stratégie bornée adaptée aux contraintes documentées du fournisseur.

Les erreurs d'authentification (`401`), de droit commercial (`402`), d'autorisation (`403`) et les autres erreurs client permanentes ne sont pas retentables. Le contrat refuse qu'une classe permanente soit déclarée retentable.

## Classes d'erreur stables

Les classes communes sont :

- `authentication`
- `authorization`
- `entitlement`
- `rate_limit`
- `provider_unavailable`
- `invalid_request`
- `invalid_response`

Les codes HTTP inconnus de succès ou de redirection ne sont pas acceptés par le classificateur d'échec. Une validation propre au fournisseur peut produire `invalid_response` ; les connecteurs doivent conserver séparément un contexte fournisseur nettoyé lorsqu'il peut être conservé sans risque, plutôt que d'étendre la taxonomie commune à chaque message fournisseur.

## Limite de preuve

Ces règles sont des sémantiques de contrat OpenRetailSchema. Elles ne certifient à elles seules aucun connecteur fournisseur. Loyverse reste le premier connecteur de référence : ses tests synthétiques de pagination, nouvelles tentatives et points de reprise soutiennent ce contrat commun, sans transformer une preuve synthétique en test réel. Les preuves Loyverse directes et OAuth restent des critères séparés de la roadmap.