# Backlog du projet ENSO Monitor

Ce backlog couvre le produit, les données, la qualité et l’exploitation. Les livraisons ci-dessous reprennent les commits visibles dans l’historique du dépôt, notamment les références locales `origin/main` et `origin/caddy-deployment`. Les tâches ouvertes sont limitées aux lacunes et actions concrètes repérées dans le dépôt et dans le dernier démarrage de la stack.

Priorités : **P0** bloque la mise en production, **P1** est important pour fiabiliser le projet, **P2** est une amélioration utile mais non bloquante.

## Livré dans l’historique Git

| Commit | Livraison |
| --- | --- |
| `ccb8557` | Initialisation de la structure du projet. |
| `3442662` | Schéma PostgreSQL et migration Alembic. |
| `057af86` | ETL NOAA RONI : lecture, validation, transformation et import des observations. |
| `6bfe1b8` | API FastAPI pour les observations et les épisodes historiques. |
| `1ed303d` | Tableau de bord React et filtre par période. |
| `2c20fca` | Comparaison d’épisodes et premier déploiement Docker Compose. |
| `1c4e1bd` | Correction des métadonnées de date d’extraction dans la source. |
| `17224f7` | Mise à jour complémentaire de `SOURCE.md`. |
| `ee5cb36` | Documentation du projet. |
| `875ab23` | Exposition de la date d’extraction dans l’API. |
| `dabf108` | Caddy, HTTPS automatique, volumes persistants et isolation réseau pour le déploiement. |
| `6e4d9cc` | Première version du backlog, centrée sur le déploiement. |

Les fonctionnalités déjà présentes comprennent les routes de santé, observations filtrées, métadonnées source, épisodes et comparaison ; le frontend affiche le graphique, le tableau, les filtres et la comparaison. L’ETL est relançable via `make etl`.

## À faire

- [ ] **P2 — Mettre le site en ligne sur un domaine contrôlé (facultatif pour le sujet).** Configurer le DNS, le pare-feu et `FRONTEND_ORIGIN`, puis vérifier le certificat HTTPS. Le dernier démarrage a lancé les services, mais Let's Encrypt a refusé `your-domain.example`, qui est un domaine réservé aux exemples.
- [ ] **P2 — Valider le déploiement public de bout en bout (facultatif pour le sujet).** Après configuration DNS, contrôler la redirection HTTP→HTTPS, la page, `/docs`, `/api/v1/health` et les principales routes de données. Confirmer également que la migration et l’ETL se terminent avec succès.
- [ ] **P1 — Renforcer les tests métier des épisodes.** Ajouter des tests unitaires de `detect_episodes` pour les seuils ±0,5 °C, les cinq saisons consécutives, les séries interrompues ou avec des mois manquants et les changements d’épisode. Tester aussi les réponses de comparaison, les identifiants inconnus et les statistiques calculées.
- [ ] **P1 — Documenter la mise à jour des données NOAA.** Décrire une procédure reproductible pour récupérer le fichier RONI, mettre à jour `data/raw/SOURCE.md`, contrôler la période et le SHA-256, puis relancer l’ETL. Vérifier qu’une réimportation après mise à jour ne crée pas de doublons.
- [ ] **P1 — Définir et vérifier les sauvegardes de production.** Documenter les sauvegardes PostgreSQL et des volumes Caddy, leur rétention et une procédure de restauration. Le guide recommande de sauvegarder ces volumes, mais ne fournit pas encore de procédure opérationnelle.

## À préciser avant d’ajouter des fonctionnalités

Aucun besoin produit supplémentaire n’est documenté dans le dépôt. Il n’y a donc pas de tâches spéculatives pour l’authentification, les prévisions ou de nouveaux indices ; les ajouter nécessiterait une décision produit explicite.
