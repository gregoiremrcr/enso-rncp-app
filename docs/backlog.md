# Backlog

Cette liste regroupe les prochaines actions concrètes connues pour le projet. Les priorités indiquent l’ordre recommandé : **P0** bloque la mise en production, **P1** est nécessaire pour valider l’exploitation, **P2** est une amélioration de documentation.

## À faire

- [ ] **P0 — Configurer le vrai domaine de production.** Remplacer `your-domain.example` dans le `.env` local par un domaine contrôlé, et régler `FRONTEND_ORIGIN` sur `https://<domaine>`. Créer les enregistrements DNS `A` et, si IPv6 est utilisé, `AAAA` vers le serveur ; autoriser les ports TCP 80/443 et UDP 443. Le dernier démarrage a échoué à obtenir un certificat, car Let's Encrypt a rejeté `your-domain.example` comme suffixe non public.
- [ ] **P0 — Obtenir et vérifier le certificat HTTPS.** Après configuration du domaine, relancer Caddy avec `docker compose up -d caddy`, examiner `docker compose logs -f caddy`, puis vérifier la redirection HTTP, le certificat HTTPS et `https://<domaine>/api/v1/health` ainsi que `/docs`.
- [ ] **P1 — Effectuer un contrôle de mise en production.** Vérifier avec `docker compose ps` que l’API et le frontend sont sains et que `migrate` et `etl` se sont terminés avec succès ; tester la page et les routes principales via le domaine HTTPS.
- [ ] **P2 — Aligner la documentation sur les métadonnées de la source.** `data/raw/SOURCE.md` indique une date d’extraction au 11 novembre 2026, tandis que le README dit encore que cette date reste à compléter. Mettre à jour le README pour refléter la valeur confirmée dans la fiche source.

## Terminé

- [x] Ajouter Caddy comme point d’entrée HTTPS avec certificats et configuration persistés dans des volumes.
- [x] Ne publier que les ports de Caddy ; isoler l’API et PostgreSQL des ports de l’hôte et limiter les communications par réseaux Docker.
- [x] Documenter les variables, le DNS, le démarrage et les vérifications de déploiement.
- [x] Démarrer la stack : PostgreSQL, migration, ETL, API, frontend et Caddy ont démarré. L’obtention du certificat reste bloquée par le domaine placeholder, voir les tâches P0.
