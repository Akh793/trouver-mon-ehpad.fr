-- Table des retours de trouver-mon-ehpad.fr
--
-- Aucune adresse e-mail, aucune adresse IP en clair : ce que le service ne
-- collecte pas ne peut ni fuiter, ni être réclamé, ni avoir à être protégé.
-- L'empreinte ne sert qu'à limiter le débit sur une heure ; elle est effacée
-- au bout de deux jours par la tâche planifiée du Worker.

CREATE TABLE IF NOT EXISTS retours (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  nom       TEXT,                              -- facultatif, libre, jamais vérifié
  message   TEXT NOT NULL,
  etat      TEXT NOT NULL DEFAULT 'publie',    -- publie (par défaut) | refuse (retiré du site)
  recu_le   TEXT NOT NULL,
  publie_le TEXT,
  empreinte TEXT                               -- SHA-256 tronqué de l'IP, effacé après 2 jours
);

CREATE INDEX IF NOT EXISTS idx_etat ON retours (etat, publie_le DESC);
CREATE INDEX IF NOT EXISTS idx_emp  ON retours (empreinte, recu_le);
