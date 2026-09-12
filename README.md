# trouver-mon-ehpad.fr

Le vrai reste à charge en EHPAD, établissement par établissement, sur une carte.
Service indépendant, gratuit, sans publicité et sans partenariat avec des établissements.

**7 417 EHPAD · 7 901 pages · aucune donnée personnelle transmise : tout le calcul s'exécute dans le navigateur.**

## Ce que fait le site

- Un **calculateur** : à partir d'un code postal, de la retraite et du niveau d'autonomie, il affiche
  ce qui resterait réellement à payer dans chaque établissement, après l'allocation personnalisée
  d'autonomie, l'aide au logement et la réduction d'impôt.
- Un **annuaire** : une page par région, département, ville et établissement documenté, avec les
  tarifs déclarés, leur évolution depuis 2018, l'habilitation à l'aide sociale et l'évaluation officielle.
- Des **guides** et un **baromètre des prix**, construits à partir des données publiques.

## Organisation du dépôt

```
site/        ce qui est mis en ligne — et rien d'autre
build/       les scripts qui fabriquent site/ à partir des données publiques
MAINTENANCE.md   toutes les bases de données, leurs licences, et la procédure de mise à jour
```

Les **données sources téléchargées** (environ 200 Mo) ne sont pas versionnées : elles se
retéléchargent en suivant le §2.2 et le §4 de `MAINTENANCE.md`.

## Reconstruire le site

```bash
cd build
python3 build_data_v2.py     # croise les sources          → merged_v2.json
python3 split_data_v2.py     # découpe par département     → ../site/data/**
python3 build_site.py        # assemble le calculateur     → ../site/index.html
python3 build_pages.py       # pages annexes
python3 seo/build_seo.py     # 7 901 pages de contenu + sitemaps
```

Voir le site en local :

```bash
cd site && python3 -m http.server 8000   # puis http://127.0.0.1:8000/
```

Dans la console du navigateur, `runTests()` doit renvoyer `true` (37 tests : formule de l'APA,
seuils, réduction d'impôt, aide sociale, répartition entre les enfants, géographie).

## Mise en ligne

Un push sur `main` déclenche `.github/workflows/pages.yml`, qui vérifie puis publie **uniquement le
dossier `site/`** sur GitHub Pages. Voir `DEPLOIEMENT.md`.

## Sources

CNSA (prix et tarifs), FINESS / Agence du numérique en santé, Haute Autorité de santé,
Direction générale de l'alimentation, DREES, INSEE, Base adresse nationale, IGN Géoplateforme,
OpenFisca-France. Chaque page cite sa source et sa date ; le détail est dans `MAINTENANCE.md`.

Les chiffres agrégés publiés par le site sont libres de reprise avec la mention
« Données : Trouver mon EHPAD, à partir des tarifs déclarés à la CNSA ».
