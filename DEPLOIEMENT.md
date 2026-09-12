# Mettre le site en ligne

Trois étapes, une seule fois. Ensuite, chaque `git push` sur `main` republie le site.

---

## 1. Avant le premier push : compléter les mentions légales

`build/build_pages.py` contient deux mentions marquées **`À COMPLÉTER`** : le nom de l'éditeur et
son adresse. Elles sont exigées par l'article 6 III de la loi pour la confiance dans l'économie
numérique.

```bash
# remplacer les deux « À COMPLÉTER » dans build/build_pages.py, puis :
cd build && python3 build_pages.py
grep -c "À COMPLÉTER" ../site/mentions-legales.html   # doit afficher 0
```

Le workflow de publication **refuse de déployer** tant que ces mentions ne sont pas remplies.
C'est volontaire.

> Un éditeur non professionnel peut ne rendre publics que son nom et une adresse de courrier
> électronique, à condition d'avoir communiqué son identité complète à l'hébergeur.

---

## 2. Créer le dépôt et pousser

```bash
cd /chemin/vers/trouver-mon-ehpad
git init -b main
git add .
git commit -m "trouver-mon-ehpad.fr — version 2.4"
git remote add origin git@github.com:VOTRE-COMPTE/trouver-mon-ehpad.git
git push -u origin main
```

Le premier push transfère environ 120 Mo et 12 000 fichiers : comptez quelques minutes.
Le dépôt peut être public ou privé — GitHub Pages fonctionne avec les deux sur un compte gratuit.

---

## 3. Activer GitHub Pages

Dans **Settings → Pages** du dépôt :

| Réglage | Valeur |
|---|---|
| Source | **GitHub Actions** (et non « Deploy from a branch ») |
| Custom domain | `trouver-mon-ehpad.fr` |
| Enforce HTTPS | coché, dès que le certificat est émis (quelques minutes) |

Le fichier `site/CNAME` porte déjà le domaine : GitHub le reprend automatiquement.

### DNS à créer chez votre registrar

Pour le domaine racine `trouver-mon-ehpad.fr`, quatre enregistrements **A** :

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

et, pour `www`, un **CNAME** vers `VOTRE-COMPTE.github.io.`

> ⚠️ Ces adresses sont celles publiées par GitHub pour les domaines apex.
> Vérifiez-les dans la documentation GitHub Pages le jour de la bascule : elles peuvent changer.

La propagation prend de quelques minutes à 24 heures. Tant qu'elle n'est pas faite, le site reste
accessible sur `VOTRE-COMPTE.github.io/trouver-mon-ehpad/` — **mais en partie cassé** : tous les
liens internes sont absolus et supposent un site servi à la racine d'un domaine. C'est normal, et
cela se résout dès que le domaine pointe.

---

## 4. Après la mise en ligne

1. **Search Console** : ajouter la propriété, déclarer `https://trouver-mon-ehpad.fr/sitemap.xml`.
2. **Mesure d'audience** : renseigner `ME_GTM_ID` en tête de `build/index.template.html`, puis
   `python3 build_site.py`. Tant qu'il est vide, aucune mesure ne part — le bandeau de consentement
   reste actif et les événements sont seulement empilés localement.
3. **Vérifier** : `https://trouver-mon-ehpad.fr/`, une page de ville, une fiche d'établissement,
   `/sitemap.xml`, `/robots.txt`, et une adresse inexistante (doit afficher la page 404).

---

## Ce que le workflow vérifie avant de publier

- aucune mention `À COMPLÉTER` dans les pages ;
- l'adresse canonique de l'accueil correspond au domaine du fichier `CNAME` ;
- aucun fichier de travail (`*.v2.js`, `*.bak`) dans le dossier publié ;
- il affiche le nombre de pages et le poids publiés.

Si l'une de ces vérifications échoue, rien n'est mis en ligne.

---

## Republier

```bash
git add -A && git commit -m "mise à jour des tarifs CNSA" && git push
```

Ou, sans rien changer, l'onglet **Actions → Publier le site → Run workflow**.
