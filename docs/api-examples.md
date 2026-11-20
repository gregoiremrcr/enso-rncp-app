# Exemples API

Avec l'application lancée sur `http://localhost:8080` :

```sh
curl -i http://localhost:8080/api/v1/health
curl -i 'http://localhost:8080/api/v1/observations?start=2000-01-01&end=2001-12-31'
curl -i http://localhost:8080/api/v1/source
curl -i http://localhost:8080/api/v1/episodes
curl -i 'http://localhost:8080/api/v1/episodes/compare?a=ID_EPISODE_A&b=ID_EPISODE_B'
```

Remplacer `ID_EPISODE_A` et `ID_EPISODE_B` par des identifiants renvoyés par `GET /api/v1/episodes`. La documentation OpenAPI est disponible sur `/docs`.
