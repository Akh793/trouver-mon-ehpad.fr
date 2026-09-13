# Point de réception des retours — déploiement

Le site est statique : il ne peut rien recevoir. Ce dossier contient le petit service
qui reçoit les messages de la page `/retours/` et les publie aussitôt, ainsi que
l'écran depuis lequel vous en retirez ce qui doit l'être.

**Gratuit et sans carte bancaire.** L'offre gratuite de Cloudflare couvre 100 000
requêtes par jour et 5 Go de base ; elle ne se met jamais en pause.

---

## 1. Créer le compte et installer l'outil

Un compte sur `dash.cloudflare.com` suffit — **aucun changement DNS n'est nécessaire**,
le site reste chez GitHub Pages.

```bash
npm install -g wrangler
wrangler login
```

## 2. Créer la base

```bash
cd worker
wrangler d1 create retours-tme
```

La commande affiche un `database_id`. **Recopiez-le dans `wrangler.toml`**, à la place de
`A_REMPLACER_PAR_L_ID_RENVOYE_A_LA_CREATION`. Puis créez la table :

```bash
wrangler d1 execute retours-tme --remote --file=schema.sql
```

## 3. Poser les deux secrets

```bash
wrangler secret put CLE_ADMIN    # mot de passe de l'écran de modération : long et unique
wrangler secret put SEL_IP       # chaîne aléatoire quelconque, jamais à retenir
```

`SEL_IP` sert à rendre les empreintes d'adresses IP non réversibles. Le changer efface
l'historique de limitation de débit, sans autre conséquence.

## 4. Déployer

```bash
wrangler deploy
```

La commande affiche l'adresse du service, de la forme
`https://retours-tme.VOTRE-COMPTE.workers.dev`.

## 5. Brancher la page

Ouvrir `build/build_retours.py`, remplacer la valeur de `API` par cette adresse, puis :

```bash
cd build
python3 build_retours.py     # doit afficher « envoi ACTIF »
```

Committez et poussez : la page accepte les messages.

---

## Retirer un message

Ouvrir `https://retours-tme.VOTRE-COMPTE.workers.dev/admin?cle=VOTRE_CLE_ADMIN`.

L'écran liste les messages, les plus récents d'abord. Deux actions : **retirer du site**
(réversible, le message reste en base) et **effacer définitivement**. L'écran est servi par
le service lui-même : rien n'est déposé sur le site, et il porte un `noindex`.

Les messages sont publiés sans relecture. C'est le régime de l'**hébergeur** au sens de la
LCEN : la responsabilité n'est engagée qu'à défaut de retrait prompt après signalement —
mais ce régime ne tient qu'à deux conditions, toutes deux en place :

1. un **moyen de signaler** accessible : chaque message porte un lien « Signaler » qui
   ouvre un courriel pré-rempli avec son numéro ;
2. un **retrait rapide** quand le signalement est fondé. C'est la seule obligation réelle,
   et la seule chose à ne pas laisser traîner.

Ce qui se retire sans hésiter : la mise en cause nommée d'un établissement, tout message
permettant d'identifier une personne — résident, proche, salarié — et tout contenu
manifestement illicite. Retirer d'abord, réfléchir ensuite : l'action est réversible.

Pensez à consulter cet écran régulièrement — rien ne vous prévient de l'arrivée d'un message.

---

## Ce qui est enregistré, et ce qui ne l'est pas

| Donnée | Conservation |
|---|---|
| Le message | Jusqu'au retrait ; 30 jours après retrait, puis effacé |
| Le prénom ou pseudonyme, s'il est fourni | Idem |
| Empreinte SHA-256 tronquée de l'adresse IP | 2 jours, puis effacée automatiquement |
| Adresse e-mail | **Jamais demandée** |
| Adresse IP en clair | **Jamais enregistrée** |

Le ménage est automatique : une tâche planifiée s'exécute chaque nuit à 3 h 30.

## Protection contre les robots

Pas de captcha — il ajouterait un service tiers, et un traceur, sur une page qui
n'en porte aucun. À la place, trois barrières cumulées :

- un champ invisible qu'un humain ne remplit jamais ;
- un délai minimal de trois secondes entre l'affichage et l'envoi ;
- trois messages par heure et par adresse au maximum.

Ces barrières arrêtent le spam automatisé, qui est le seul volume qu'un humain ne peut
pas suivre. Ce qui passe est publié : le retrait est votre dernière barrière.

## Vérifier sans déployer

```bash
node worker/test.mjs
```

19 tests couvrent la publication immédiate, le piège à robots, le délai minimal, la
longueur, la neutralisation du balisage, la limitation de débit, l'absence d'IP en clair,
le retrait, la remise en ligne, l'effacement, le refus de l'administration sans clé et
l'échappement de l'écran d'administration.
