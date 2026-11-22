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

La RONI (Relative Oceanic Niño Index) est distincte de l’ONI. La source fournie indique ERSSTv6 ; la page CPC consultée confirme cette version. Le fichier fourni a été extrait le 11 novembre 2026 ; sa période et son SHA-256 sont consignés dans `data/raw/SOURCE.md`. La série présente couvre DJF 1950 à ASO 2026. Les épisodes appliquent le seuil ±0,5 °C sur au moins cinq saisons glissantes consécutives. L’application ne fait aucune prévision.

La comparaison décrit uniquement les valeurs de RONI et la règle historique de seuil. Elle n’établit pas de causalité et n’intègre pas d’autres variables climatiques.

## Développement

Prérequis : Docker et Docker Compose v2. Si `.env` n’existe pas, copiez `.env.example` vers `.env`, puis renseignez le domaine et les secrets avant de lancer la stack avec `docker compose up --build -d`. La stack sert le frontend via Caddy en HTTPS ; les détails de configuration et de vérification sont dans le [guide de déploiement](docs/deployment.md). Pour lancer les vérifications applicatives, utiliser `make test` et `make lint`.

Les commits suivent Conventional Commits. Les requêtes SQL utilisent des paramètres et la logique de classification des épisodes se trouve dans `backend/app/episodes.py`.

## Utilisation de l’intelligence artificielle

**Outil utilisé : Codex.** L’IA a contribué à la conception et à la documentation du projet. Elle a réalisé la mise en place technique du déploiement Docker Compose/Caddy : configuration des services, des réseaux, du reverse proxy et du HTTPS. La mise en ligne publique sur un domaine contrôlé et la validation d’un certificat HTTPS restent à effectuer ; le sujet rend le déploiement réel facultatif. Les choix et le code doivent pouvoir être expliqués et défendus individuellement à l’oral.
