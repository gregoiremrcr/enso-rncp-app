# Installer Caddy sur le VPS ENSO Monitor

Ce guide décrit une installation de Caddy sur un VPS Debian ou Ubuntu. Caddy tourne comme service système sur l’hôte et reçoit le trafic public en HTTPS. Il transmet ensuite les requêtes au frontend ENSO Monitor exécuté dans Docker. Il s’agit d’une procédure de déploiement proposée, pas d’un déploiement déjà effectué.

## 1. Prérequis

- Un VPS Debian ou Ubuntu administrable avec `sudo`.
- Un nom de domaine, par exemple `enso.example.org`, dont l’enregistrement DNS A pointe vers l’IP publique du VPS. Ajouter un enregistrement AAAA seulement si le VPS dispose d’une IPv6 publique fonctionnelle.
- Les ports TCP 80 et 443 autorisés à la fois dans le pare-feu du fournisseur VPS et sur le serveur.
- Docker Compose fonctionnel pour l’application ENSO Monitor.
- Le port du frontend publié uniquement sur l’interface locale de l’hôte. Pour un service frontend exposé sur le port interne 80 du conteneur, la publication Compose doit prendre la forme `127.0.0.1:8080:80` (adapter le port hôte au Compose du projet). Ne publiez pas PostgreSQL ni l’API sur Internet.

Avant de continuer, vérifiez l’adresse et le port effectivement publiés :

```bash
docker compose ps
```

La colonne des ports doit montrer une adresse locale telle que `127.0.0.1:8080->80/tcp` pour le frontend. Si elle affiche `0.0.0.0:8080`, limitez la publication à `127.0.0.1` dans le fichier Compose destiné au VPS, puis recréez le service.

## 2. Autoriser le trafic réseau nécessaire

Configurez les règles du fournisseur VPS pour laisser entrer TCP 80 et 443 depuis Internet. Pour SSH (TCP 22), limitez les IP sources à votre adresse d’administration si le fournisseur le permet.

Sur Ubuntu avec UFW, après avoir confirmé que SSH fonctionne et que sa règle est autorisée :

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

La politique entrante doit refuser les autres ports. Si UFW n’est pas utilisé, appliquez la même politique avec le pare-feu système choisi. Le pare-feu du fournisseur et le pare-feu de l’hôte doivent être cohérents.

## 3. Installer le paquet officiel Caddy

Sur Debian ou Ubuntu, les commandes suivantes ajoutent le dépôt stable officiel de Caddy puis installent son paquet. L’installation configure et démarre le service systemd `caddy`.

```bash
sudo apt install --yes debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install --yes caddy
```

Vérifiez que le service est actif :

```bash
systemctl status caddy --no-pager
caddy version
```

## 4. Configurer le reverse proxy

Le fichier de configuration est `/etc/caddy/Caddyfile`. Remplacez le domaine d’exemple par le vrai domaine et adaptez `127.0.0.1:8080` au port local vérifié à l’étape 1.

```caddyfile
enso.example.org {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8080
}
```

Le frontend Nginx du projet doit continuer à router les appels `/api/...` vers l’API comme en environnement Docker. Caddy envoie ici les chemins reçus au frontend sans modifier leur URI ; vérifiez le routage du frontend dans la configuration réelle du projet.

Validez la configuration, puis rechargez le service :

```bash
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

Lorsque le domaine pointe vers ce VPS et que les connexions entrantes sur 80 et 443 arrivent bien sur Caddy, celui-ci peut obtenir et renouveler automatiquement les certificats TLS pour le domaine. Une IP seule ou un DNS encore incorrect ne permet pas de suivre cette procédure de certificat public avec un nom de domaine.

## 5. Vérifier le service

Depuis le VPS, vérifiez d’abord le frontend local :

```bash
curl -I http://127.0.0.1:8080/
```

Puis vérifiez le site public depuis votre poste :

```bash
curl -I https://enso.example.org/
```

Consultez les journaux de Caddy en cas de problème de démarrage, de proxy ou de certificat :

```bash
sudo journalctl -u caddy --since "30 minutes ago" --no-pager
```

Vérifiez aussi les services applicatifs et leurs journaux :

```bash
docker compose ps
docker compose logs --tail=100 frontend api
```

Ne rendez pas publics les ports internes de l’API, de PostgreSQL ou l’interface d’administration Docker pour résoudre un problème de proxy.

## 6. Exploitation et sauvegardes

- Caddy se lance au démarrage du serveur via systemd. Contrôle : `systemctl is-enabled caddy`.
- Pour une modification du Caddyfile, validez avant de recharger : `sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`.
- Sauvegardez séparément le Caddyfile, les fichiers Compose et leurs configurations non secrètes. Stockez les secrets dans un gestionnaire adapté ou des fichiers protégés, pas dans le dépôt Git.
- La base PostgreSQL doit faire l’objet de sauvegardes applicatives cohérentes, chiffrées et copiées hors du VPS, avec des tests de restauration. La présence du certificat TLS Caddy ne sauvegarde pas les données de l’application.
- Le répertoire de données Caddy contient notamment les données nécessaires à la gestion des certificats. Évitez de le supprimer ou de le recopier à chaud comme méthode de sauvegarde improvisée. Suivez la documentation Caddy si sa sauvegarde/restauration est nécessaire.

## Sources officielles

- [Installation de Caddy — documentation officielle](https://caddyserver.com/docs/install)
- [Directive reverse_proxy — documentation officielle](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Démarrage rapide HTTPS — documentation officielle](https://caddyserver.com/docs/quick-starts/https)
