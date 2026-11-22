# ENSO Monitor

ENSO Monitor présente la série historique RONI publiée par la NOAA CPC. L’application comprend une API FastAPI, une base PostgreSQL et une interface React en français. Elle filtre les observations et compare les épisodes historiques calculés à partir de la série importée.

## Déploiement

La configuration de production fait passer le trafic public par Caddy. Caddy termine HTTPS et transmet les requêtes au frontend Nginx ; Nginx relaie `/api/`, `/docs`, `/redoc` et `/openapi.json` vers l’API. L’API et PostgreSQL ne publient aucun port sur l’hôte.

Suivre [le guide de déploiement](docs/deployment.md) pour configurer le DNS et `.env`, lancer Compose, vérifier HTTPS et conserver les certificats. Les actions restantes sont listées dans le [backlog](docs/backlog.md).

## Routes

- `GET /api/v1/health`
- `GET /api/v1/observations?start=&end=`
- `GET /api/v1/source`
- `GET /api/v1/episodes`
- `GET /api/v1/episodes/compare?a=&b=`

Les exemples sont dans [docs/api-examples.md](docs/api-examples.md) et la documentation interactive est disponible sur `/docs`.

## Données et précautions

La RONI (Relative Oceanic Niño Index) est distincte de l’ONI. La source fournie indique ERSSTv6 ; la page CPC consultée confirme cette version. La date réelle de téléchargement n’était pas fournie et reste à compléter dans `data/raw/SOURCE.md`. La série présente couvre DJF 1950 à ASO 2026. Les épisodes appliquent le seuil ±0,5 °C sur au moins cinq saisons glissantes consécutives. L’application ne fait aucune prévision.

La comparaison décrit uniquement les valeurs de RONI et la règle historique de seuil. Elle n’établit pas de causalité et n’intègre pas d’autres variables climatiques.

## Développement

Prérequis : Docker et Docker Compose v2. La stack est configurée pour le déploiement HTTPS. Pour lancer les vérifications applicatives, utiliser `make test` et `make lint`.

Les commits suivent Conventional Commits. Les requêtes SQL utilisent des paramètres et la logique de classification des épisodes se trouve dans `backend/app/episodes.py`.
