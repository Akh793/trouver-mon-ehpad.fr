# Compteur d'audience — déploiement

Service **séparé** de celui des retours, et base séparée : un pic de trafic ne
doit pas empêcher un visiteur de déposer un message.

Attention : les quotas gratuits sont **par compte**, pas par service. Les deux
Workers partagent les 100 000 requêtes par jour, et les deux bases partagent
les 100 000 lignes écrites par jour de D1. Depuis le 1er septembre 2026, D1
refuse toute écriture du compte une fois ce plafond atteint, jusqu'à minuit UTC.

**Plafond pratique : de l'ordre de 20 000 pages vues par jour** (voir « Budget »).

---

## 1. Créer la base

```bash
cd worker-mesure
wrangler d1 create mesure-tme
```

Recopier le `database_id` affiché dans `wrangler.toml`, à la place de
`A_REMPLACER_PAR_L_ID_RENVOYE_A_LA_CREATION`. Puis créer les tables :

```bash
wrangler d1 execute mesure-tme --remote --file=schema.sql
```

Une base déjà créée avec l'**ancien** schéma (colonne `robot`) ne se met pas à
jour toute seule : `CREATE TABLE IF NOT EXISTS` la laisse telle quelle. Tant
qu'elle est vide, la supprimer et la recréer :

```bash
wrangler d1 delete mesure-tme
wrangler d1 create mesure-tme      # nouvel id à recopier dans wrangler.toml
```

## 2. Poser la clé de lecture

```bash
wrangler secret put CLE_MESURE      # mot de passe de l'écran d'audience : long et unique
```

Elle ne protège que la **lecture**. Sans elle, l'écran renvoie 403.
Ne jamais la coller dans un fichier du dépôt ni dans une conversation.

## 3. Déployer

```bash
wrangler deploy
```

La commande affiche l'adresse, de la forme `https://mesure-tme.VOTRE-COMPTE.workers.dev`.

## 4. Brancher le site

Ouvrir `build/mesure.py`, remplacer la valeur de `API` par cette adresse, puis
reconstruire les pages :

```bash
cd build
python3 build_site.py          # accueil
python3 build_pages.py         # pages annexes
python3 build_retours.py       # page des retours
python3 build_devis.py         # comparateur de devis
cd seo && python3 build_seo.py # pages de contenu
```

Contrôle avant de committer — les deux nombres doivent être égaux :

```bash
grep -rl 'sendBeacon' --include='*.html' ../site | wc -l
grep -rl 'tb-avis'    --include='*.html' ../site | wc -l
```

Tant que `API` porte encore `VOTRE-SOUS-DOMAINE`, les pages reçoivent un
commentaire HTML à la place de l'extrait : rien n'est envoyé, rien ne casse.

## 5. Quand des pages sont ajoutées au site

Le service ne compte sous leur nom que les chemins présents dans le sitemap.
Une page nouvelle absente de la liste tombe dans `/(hors-liste)`. Après toute
reconstruction qui ajoute ou retire des pages :

```bash
cd build
python3 chemins_mesure.py      # régénère worker-mesure/chemins.js depuis site/sitemap-*.xml
cd ../worker-mesure && wrangler deploy
```

Le script refuse d'écrire s'il trouve moins de 1 000 chemins : un sitemap
absent ne vide pas la liste par accident.

---

## Lire les chiffres

```
https://mesure-tme.VOTRE-COMPTE.workers.dev/mesure?cle=VOTRE_CLE
```

`?jours=365` élargit la fenêtre (90 par défaut, 1095 au maximum).
`/mesure.json?cle=…` renvoie les mêmes données en JSON. L'écran porte un
`noindex` et n'est servi que par le service lui-même.

| Colonne | Ce qu'elle compte |
|---|---|
| **Engagés** | Visites humaines où quelqu'un a fait quelque chose : défilement, clic, touche, souris, ou 10 secondes d'onglet visible. **Le chiffre à suivre.** |
| Chargements | Pages affichées à l'écran par un navigateur au profil humain |
| Taux d'engagement | Engagés ÷ chargements |
| Entrées | Arrivées depuis l'extérieur du site |
| Déclarés | Robots qui s'annoncent (Googlebot, Bingbot, GPTBot…) |
| Suspects | Vues qui ressemblent à un robot sans qu'il se déclare |
| Vous | Vos propres chargements, depuis un navigateur marqué (voir plus bas) |

S'y ajoutent : pages les plus vues (avec leurs engagés), **motifs de suspicion**, nombre de
vues hors liste, sites référents, pays, profil horaire des engagements.

## Les trois classes

Rien n'est jeté, sauf les appels venus d'un **autre site** (en-tête `Origin`
étranger). Une vue jetée ne se récupère pas ; une vue mal classée se reclasse.

| Classe | Règle | Code |
|---|---|---|
| 1 · déclaré | L'agent utilisateur contient bot, crawl, spider, headless, curl, python… ou est vide | serveur |
| 2 · suspect | `navigator.webdriver` vrai (1), « HeadlessChrome » (2), Chrome sans `window.chrome` hors WebView Android (4), aucune langue (8) | navigateur → `auto:<somme>` |
| 2 · suspect | Réseau d'un hébergeur (AWS, Google Cloud, Azure, OVH SAS, Hetzner, DigitalOcean…) | serveur → `hebergeur:<nom>` |
| 2 · suspect | Requête sans en-tête `Origin` (appel à la main) | serveur → `sans-origine` |
| 3 · vous | Navigateur marqué par le lien `#ne-pas-me-compter`, requête venue du site | navigateur → `m=1` |
| 0 · humain | Aucun des signes ci-dessus | — |

Akamai, Cloudflare et Fastly ne sont **pas** tenus pour des hébergeurs : ils
portent le Relais privé d'iCloud, donc de vrais visiteurs sur iPhone. OVH
Télécom (box ADSL/fibre, AS35540) n'est pas confondu avec OVH SAS (AS16276).

Côté navigateur, rien n'est envoyé tant que la page est **pré-rendue** ou
dans un **onglet d'arrière-plan** : une page ouverte et jamais regardée n'est
pas une vue.

**Le tableau des motifs sert de garde-fou.** Si `hebergeur:…` ou
`sans-origine` monte fort sans raison, la règle range peut-être des humains
(VPN d'entreprise, navigateur exotique) parmi les suspects : c'est là qu'on le voit.

## Ne pas compter vos propres visites

Ouvrir **une fois, dans chaque navigateur et sur chaque appareil** :

```
https://trouver-mon-ehpad.fr/#ne-pas-me-compter
```

Un message vert confirme. Ce navigateur garde la marque `tme_proprio` ; ses
visites partent avec `m=1` et tombent dans la colonne **Vous**, jamais chez les
humains, ni dans les sources ni dans les pays. Pour annuler :
`https://trouver-mon-ehpad.fr/#ne-plus-m-exclure`.

La marque disparaît si l'on efface les données du site, et n'existe pas en
navigation privée : il suffit de rouvrir le lien. Un robot déclaré reste
« déclaré », et un appel sans origine reste « suspect », même avec `m=1`.

Chez un visiteur ordinaire, rien n'est écrit : l'extrait lit la clé, ne la
trouve pas, et s'arrête là — comme pour la préférence de thème déjà lue.

Effacer après coup les visites humaines d'une journée (vos tests, par exemple) :

```
wrangler d1 execute mesure-tme --remote --command "DELETE FROM vues WHERE jour='2026-09-29' AND classe=0; DELETE FROM sources WHERE jour='2026-09-29'; DELETE FROM pays WHERE jour='2026-09-29';"
```

Cela efface aussi les éventuels vrais visiteurs de ce jour-là : à réserver aux
journées de test.

## Budget

| Événement | Requêtes Worker | Lignes D1 écrites |
|---|---|---|
| Chargement d'une page (ligne nouvelle) | 1 | 2 |
| Chargement d'une page (ligne existante) | 1 | 1 |
| Engagement | 1 | 1 |
| Entrée depuis l'extérieur | — | jusqu'à +4 (référent, pays) |
| Vue suspecte | — | jusqu'à +2 (motif) |

Une page vue par un humain coûte donc 2 requêtes et 2 à 7 lignes écrites.
C'est D1 qui plafonne en premier : **environ 20 000 pages vues par jour**, en
comptant large et en laissant de la marge aux retours. Le schéma n'a
volontairement aucun index secondaire : chacun ajouterait une ligne écrite à
chaque nouvelle ligne. En cas de dépassement, le service répond quand même
204 au navigateur : le visiteur ne voit rien, seules les mesures de la fin de
journée manquent.

## Ce qui est enregistré, et ce qui ne l'est pas

| Donnée | Enregistrée ? |
|---|---|
| Chemin de la page, **s'il figure au sitemap** | Oui ; sinon `/(hors-liste)` |
| Jour et heure, **heure de Paris** | Oui |
| Classe (humain / déclaré / suspect) et motif | Oui |
| Domaine du site référent (`google.fr`) | Oui, le domaine seul, visites humaines |
| Pays, sur les entrées | Oui, le code à deux lettres, visites humaines |
| Chaîne de requête, ancre | **Jamais** — les liens de partage y portent la situation du visiteur |
| Adresse IP | **Jamais**, ni en clair ni sous forme d'empreinte |
| Numéro et nom du réseau (AS) | Lus pour classer, **jamais stockés**, sauf le nom de l'hébergeur dans le motif |
| Cookie, `localStorage`, identifiant | **Aucun** |

Les signes `webdriver`, `window.chrome` et langues sont lus dans le navigateur
mais seul un **chiffre de 0 à 15** part, sans rien stocker sur le terminal.
⚠️ Lecture de l'article 82 de la loi Informatique et Libertés : il vise le
stockage et l'accès à des informations déjà stockées dans le terminal. La
lecture de ces propriétés standard, sans identifiant ni conservation, se situe
au même niveau que l'agent utilisateur envoyé à chaque page. À mentionner dans
les mentions légales ; en cas de doute, la CNIL reste l'interlocuteur.

## Le grain, et pourquoi il est fin

Une ligne par `(jour, heure, chemin, classe)`. Semaine et mois sont des
`GROUP BY` sur cette table : on agrège vers le haut, jamais vers le bas.

Au-delà de **400 jours**, la tâche de 3 h 45 replie les 24 lignes horaires d'une
page et d'une classe en une seule (`heure = -1`). Le total du jour reste intact,
le détail horaire disparaît.

## Ce que ce compteur ne dira jamais

Visiteurs uniques, sessions, parcours d'une page à l'autre : impossible sans
identifiant, c'est le prix de l'absence de bandeau.

**Limite du filtre** : un robot qui pilote un vrai navigateur, maquille ses
signes et passe par une connexion résidentielle est indiscernable d'un humain
— pour ce compteur comme pour Google Analytics. Le taux d'engagement limite le
dégât : un tel robot doit en plus simuler un geste pour être compté engagé.

## Vérifier sans déployer

```bash
node worker-mesure/test.mjs        # 32 tests du service (classes, réseaux, chemins, tables, « Vous »)
node build/t_mesure.mjs            # 16 tests de l'extrait, dans un vrai navigateur
node build/t_mesure_chaine.mjs     # 7 tests navigateur → vrai code du service
node build/t_proprio_theme.mjs     # marque « Vous » + interrupteur Sombre, site servi sur le port 8911
```

Les deux derniers exigent Playwright, une page de test servie sur
`http://127.0.0.1:8902/index.html` (variable `PAGE` pour une autre adresse)
contenant l'extrait actif pointé vers `http://127.0.0.1:8901`.
