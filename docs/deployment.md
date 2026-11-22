# Déploiement HTTPS

La stack de production utilise Caddy comme seul point d’entrée public. Caddy écoute sur les ports 80 et 443, obtient et renouvelle automatiquement les certificats, puis transmet le trafic à Nginx (`frontend:80`). Nginx sert l’application et conserve le proxy vers FastAPI pour `/api/`, `/docs`, `/redoc` et `/openapi.json`. PostgreSQL, l’API, la migration et l’ETL ne publient pas de ports sur l’hôte.

Les réseaux limitent les connexions entre services : Caddy rejoint uniquement `web`, le frontend rejoint `web` et `enso`, et l’API rejoint `enso` et `data`. PostgreSQL, Alembic et l’ETL rejoignent uniquement `data`. Ainsi, Caddy ne peut joindre que le frontend, et le frontend ne partage pas de réseau avec la base.

## Prérequis réseau et DNS

- Un nom de domaine que vous contrôlez. Remplacez `your-domain.example` par ce nom partout dans `.env` ; c’est un placeholder réservé à la documentation, pas un domaine à utiliser en production.
- Les enregistrements DNS `A` (et, si IPv6 est activé, `AAAA`) du nom doivent pointer vers l’adresse publique du serveur. Chaque enregistrement publié doit mener à ce serveur et être joignable.
- Les ports TCP 80 et 443 doivent être autorisés dans le pare-feu du serveur et chez l’hébergeur. Le port UDP 443 est aussi publié pour HTTP/3.
- Docker Engine et le plugin Docker Compose v2 doivent être installés.

Caddy doit pouvoir recevoir les connexions entrantes directement pour effectuer les validations ACME. Un proxy DNS/CDN placé devant le serveur doit être configuré pour laisser passer les validations nécessaires ou être pris en charge explicitement par une configuration DNS challenge, qui n’est pas incluse ici.

## Variables d’environnement

Si `.env` n’existe pas, copiez `.env.example` vers `.env`. S’il existe déjà, mettez-le à jour sans écraser vos valeurs locales. Remplacez ensuite les placeholders :

| Variable | Exemple / forme attendue | Usage |
| --- | --- | --- |
| `DOMAIN` | `app.votre-domaine.example` | Nom d’hôte utilisé par Caddy pour HTTPS. |
| `POSTGRES_DB` | `enso` | Nom de la base PostgreSQL. |
| `POSTGRES_USER` | `enso_prod` | Compte PostgreSQL de l’application. |
| `POSTGRES_PASSWORD` | secret aléatoire | Mot de passe PostgreSQL ; n’utilisez pas le placeholder. |
| `DATABASE_URL` | `postgresql+psycopg://UTILISATEUR:MOT_DE_PASSE@db:5432/BASE` | Connexion utilisée par l’API, l’ETL et Alembic. Les composants doivent correspondre aux variables PostgreSQL. |
| `FRONTEND_ORIGIN` | `https://app.votre-domaine.example` | Origine autorisée par CORS ; doit correspondre exactement au domaine et au schéma public. |

Générez un secret, par exemple avec `openssl rand -hex 32`. Reportez la même valeur dans `POSTGRES_PASSWORD` et `DATABASE_URL`. Un secret hexadécimal évite les caractères qui demanderaient un encodage URL dans `DATABASE_URL`. Gardez `.env` hors du dépôt : il est ignoré par Git. Ne partagez pas ce fichier et ne commitez aucun secret.

## Lancement

```sh
cp .env.example .env  # uniquement si .env n'existe pas déjà
# Éditez .env : domaine réel, secret aléatoire et FRONTEND_ORIGIN correspondant.
docker compose config --quiet
docker compose up --build -d
```

Le démarrage conserve les dépendances actuelles : PostgreSQL devient sain, Alembic applique les migrations, l’ETL importe le fichier fourni, puis l’API devient saine et le frontend démarre. Caddy attend le démarrage du frontend.

## Vérifications

```sh
docker compose ps
docker compose logs --tail=100 caddy
curl -I "http://your-domain.example"
curl -fsS "https://your-domain.example/api/v1/health"
curl -I "https://your-domain.example/docs"
```

Remplacez `your-domain.example` par la valeur de `DOMAIN`. La requête HTTP doit rediriger vers HTTPS ; les requêtes HTTPS doivent aboutir sans erreur de certificat. `docker compose ps` doit montrer les services applicatifs en cours d’exécution, avec `migrate` et `etl` terminés avec succès. Les journaux Caddy indiquent l’émission du certificat ou une erreur ACME explicite.

Ces vérifications réseau ne peuvent être confirmées depuis le dépôt : elles dépendent du DNS public, du pare-feu, du routage entrant du serveur et de l’accès aux autorités ACME. La configuration Compose peut être validée localement indépendamment de ces prérequis.

## Arrêt, certificats et renouvellement

```sh
docker compose down
```

Les données PostgreSQL restent dans `postgres_data` et les certificats et données d’état Caddy dans `caddy_data` et `caddy_config`. Laissez Caddy démarré et conservez ces volumes : Caddy surveille automatiquement l’expiration et renouvelle les certificats. Aucune commande de renouvellement périodique n’est à planifier. Sauvegardez les volumes Caddy avec les données persistantes de l’application.

`docker compose down -v` supprime aussi ces volumes, y compris la base et l’état des certificats ; ne l’utilisez pas pour un arrêt ordinaire.
