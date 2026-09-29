-- Compteur d'audience de trouver-mon-ehpad.fr
--
-- Aucune adresse IP, aucun cookie, aucun identifiant : rien n'est écrit ni lu
-- dans le navigateur du visiteur. L'article 82 de la loi Informatique et Libertés
-- ne s'applique donc pas, et aucun bandeau n'est requis.
--
-- Le grain est (jour, heure, chemin, classe). Semaine et mois sont des GROUP BY :
-- on agrège toujours vers le haut, jamais vers le bas. Jour et heure de Paris.
--
-- Trois classes, jamais fusionnées :
--   0 humain   — rien ne signale un robot ;
--   1 déclaré  — le robot s'annonce dans son agent utilisateur (Googlebot…) ;
--   2 suspect  — navigateur automatisé, réseau d'hébergeur, ou requête sans
--                origine. Ni jeté ni compté comme humain : une vue jetée ne se
--                récupère pas, une vue mal classée se reclasse.
--   3 vous     — le propriétaire, depuis un navigateur marqué par le lien
--                #ne-pas-me-compter.

CREATE TABLE IF NOT EXISTS vues (
  jour    TEXT    NOT NULL,            -- 'AAAA-MM-JJ', heure de Paris
  heure   INTEGER NOT NULL,            -- 0 à 23 ; -1 = journée compactée
  chemin  TEXT    NOT NULL,            -- chemin du sitemap, ou '/(hors-liste)'
  classe  INTEGER NOT NULL DEFAULT 0,  -- 0 humain · 1 déclaré · 2 suspect · 3 vous
  vues    INTEGER NOT NULL DEFAULT 0,  -- chargements de page
  engages INTEGER NOT NULL DEFAULT 0,  -- visites où quelqu'un a fait quelque chose
  entrees INTEGER NOT NULL DEFAULT 0,  -- arrivées depuis l'extérieur du site
  PRIMARY KEY (jour, heure, chemin, classe)
);

-- Pourquoi une vue est suspecte, au jour : sert à vérifier que la règle ne
-- range pas trop d'humains parmi les suspects (VPN, relais privé d'Apple…).
CREATE TABLE IF NOT EXISTS motifs (
  jour   TEXT NOT NULL,
  motif  TEXT NOT NULL,               -- 'auto', 'hebergeur:<organisation>', 'sans-origine'
  vues   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (jour, motif)
);

CREATE TABLE IF NOT EXISTS sources (
  jour    TEXT NOT NULL,
  domaine TEXT NOT NULL,
  vues    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (jour, domaine)
);

CREATE TABLE IF NOT EXISTS pays (
  jour     TEXT NOT NULL,
  code     TEXT NOT NULL,
  visites  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (jour, code)
);

-- Parcours sur l'accueil (depuis le 29/09/2026) : étapes atteintes pendant un chargement.
--   a  = arrivée · cp = résultats affichés · r = budget calculé · f = fiche ouverte.
-- appareil : 1 = écran tactile (pointer: coarse), 0 = souris. Rien d'autre : ni montant,
-- ni commune, ni réponse. Même classement humain / robot que les vues.
CREATE TABLE IF NOT EXISTS etapes (
  jour     TEXT    NOT NULL,
  etape    TEXT    NOT NULL,
  appareil INTEGER NOT NULL DEFAULT 0,
  classe   INTEGER NOT NULL DEFAULT 0,
  n        INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (jour, etape, appareil, classe)
);

-- Aucun index secondaire, volontairement. Toutes les lectures filtrent sur
-- « jour >= ? », que la clé primaire (jour en tête) sert déjà. Chez D1, chaque
-- index touché par une écriture compte une ligne écrite de plus, et le quota
-- gratuit (100 000 lignes écrites par jour) est commun à tout le compte : le
-- service des retours y puise aussi. Si une base créée avec l'ancien schéma
-- porte encore ces index, les retirer :
DROP INDEX IF EXISTS idx_vues_jour;
DROP INDEX IF EXISTS idx_vues_chemin;
