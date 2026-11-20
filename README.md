# ENSO Monitor

ENSO Monitor présente la série historique RONI publiée par la NOAA CPC.
L'application filtre les observations et compare les épisodes historiques calculés à partir de la série importée.
Elle comprend une API FastAPI, une base PostgreSQL et une interface React en français.

## Données et précautions

La RONI (Relative Oceanic Niño Index) est distincte de l'ONI. La source fournie indique ERSSTv6 ; la page CPC consultée confirme cette version. La date réelle de téléchargement n'était pas fournie et reste à compléter dans `data/raw/SOURCE.md`. La série présente couvre DJF 1950 à ASO 2026. Les épisodes appliquent le seuil ±0,5 °C sur au moins cinq saisons glissantes consécutives. L'application ne fait aucune prévision.

## Prérequis

- Docker et Docker Compose v2.
- Git, pour récupérer le dépôt.

## Variables d'environnement

| Variable | Valeur de développement | Usage |
| --- | --- | --- |
| `POSTGRES_DB` | `enso` | Base PostgreSQL |
| `POSTGRES_USER` | `enso` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | `enso-dev-only` | Mot de passe local factice |
| `DATABASE_URL` | `postgresql+psycopg://enso:enso-dev-only@db:5432/enso` | Connexion API, migration et ETL |
| `FRONTEND_ORIGIN` | `http://localhost:8080` | Origine autorisée par CORS |

Les valeurs fournies sont réservées au développement local. `.env` est ignoré par Git.

## Lancement

```sh
cp .env.example .env
docker compose up --build
```

Compose démarre PostgreSQL, applique la migration, importe le fichier fourni, puis démarre l'API et l'interface. La base, l'ETL et l'API partagent un réseau interne ; seul le frontend rejoint aussi le réseau d'entrée qui publie le port. Ouvrir <http://localhost:8080>. L'API est accessible via le proxy `/api/v1`; sa documentation se trouve sur <http://localhost:8080/docs>.

Pour arrêter les services : `docker compose down`. Les données PostgreSQL restent dans le volume nommé. `docker compose down -v` supprime ce volume.

## Routes

- `GET /api/v1/health`
- `GET /api/v1/observations?start=&end=`
- `GET /api/v1/source`
- `GET /api/v1/episodes`
- `GET /api/v1/episodes/compare?a=&b=`

Voir [les exemples curl](docs/api-examples.md) et `/docs`.

## Tests

```sh
make test
```

Résultats réels : ETL `1 passed`, API `1 passed`, frontend Vitest `1 passed`, sur Python 3.12.10 et Node 24.8.0. Le parseur a lu 921 observations réelles, sans rejet. `npm run build`, ESLint, Prettier, Ruff et Black passent. Vite signale un bundle JavaScript de plus de 500 Ko.

`docker compose config --quiet` passe. `docker compose up --build -d` a démarré la stack. Les vérifications HTTP ont renvoyé 200 pour la page, `/api/v1/health` et `/docs` ; l'API retourne 921 observations, la source RONI/ERSSTv6 et 44 épisodes. La route de comparaison sur deux épisodes calculés répond également.

## Qualité et conventions

`make lint` lance Ruff et Black côté Python, puis ESLint et Prettier côté TypeScript. Les commits suivent Conventional Commits. Les requêtes SQL utilisent des paramètres ; la logique de classification d'épisodes se trouve dans `backend/app/episodes.py`.

## Usage de l'IA

TODO : décrire honnêtement les outils utilisés, les parties générées ou modifiées, et les vérifications humaines effectuées.

## Limites connues

- La date d'extraction exacte doit être ajoutée dans `data/raw/SOURCE.md`.
- La date réelle de téléchargement de la série reste à compléter. La déclaration d'usage de l'IA reste à compléter.
- La comparaison décrit uniquement les valeurs de RONI et la règle historique de seuil. Elle n'établit pas de causalité et n'intègre pas d'autres variables climatiques.
