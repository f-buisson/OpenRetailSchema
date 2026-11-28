# Contrat d'exécution des connecteurs

[English canonical](../CONNECTOR_EXECUTION.md) · [État des intégrations POS](POS.md) · [Sélection des adaptateurs](ADAPTER_SELECTION.md)

Ce document traduit les règles communes d'exécution des connecteurs en lecture seule. La version anglaise reste canonique. Un connecteur fournisseur peut exposer des détails supplémentaires, mais les consommateurs peuvent s'appuyer sur les règles communes ci-dessous.

## Pagination

Les curseurs de pagination sont un **état de transport éphémère**. Un curseur sert uniquement à poursuivre le parcours fournisseur en cours. Si `has_more=true`, le curseur doit être non vide. Un curseur de pagination n'est jamais un point de reprise durable et ne doit pas être enregistré ou présenté comme une progression source.

## Points de reprise

Un point de reprise est une **progression source durable appartenant à l'appelant**. Il doit être explicite et non vide. Sa valeur propre au fournisseur et ses règles d'avancement appartiennent au contrat du connecteur ; le consommateur ne doit jamais le déduire d'un curseur de pagination.

Un connecteur ne peut avancer cette progression durable qu'après le parcours et le traitement réussis des enregistrements qu'elle couvre. OpenRetailSchema n'ajoute pas de stockage persistant uniquement pour conserver ces points : la persistance reste la responsabilité du consommateur tant qu'un contrat de stockage concret n'existe pas dans le dépôt.

## Lecture complète

Une lecture prouve la fin de son parcours, ou elle échoue. Seul un marqueur documenté par le fournisseur prouve la fin : une page vide, l'absence de curseur suivant, ou un total déclaré par le fournisseur. Un curseur ou une page qui se répète, ou un budget de pages épuisé, n'est pas une fin. Le connecteur échoue alors au lieu de rendre les enregistrements déjà vus. `ReadOutcome` décrit une lecture réussie ; un parcours incomplet n'en est jamais une.

Seule une lecture `full` permet de tenir pour retiré un enregistrement non revu (`ReadOutcome.proves_absence`). Une lecture `incremental` rend ce qui a changé depuis un point de reprise : un enregistrement qu'elle ne rend pas est inchangé, pas retiré. Le consommateur l'applique sur une base déjà établie, et ne s'en sert jamais comme base.

Les données annexes lues avec les enregistrements (taux de taxe, stocks, libellés) suivent `related_data_may_be_missing` :

- un refus durable (`authorization`, `entitlement`) laisse la lecture continuer, et celle-ci nomme la donnée dans `ReadOutcome.missing` ;
- tout autre échec, y compris les échecs passagers `rate_limit` et `provider_unavailable`, fait échouer la lecture entière avec cet échec.

Un échec passager présenté comme une donnée manquante laisserait le consommateur remplacer des valeurs connues par des valeurs inconnues à la lecture complète suivante. Une donnée manquante est inconnue, jamais absente : le consommateur ne remplace pas une valeur connue par une valeur issue d'une donnée nommée dans `missing`.

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