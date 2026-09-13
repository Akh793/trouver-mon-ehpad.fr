# -*- coding: utf-8 -*-
"""Détermination du régime de financement de la dépendance, établissement par établissement.

Règle de méthode : le régime vient du TERRITOIRE d'implantation, jamais des tarifs déclarés.
Une égalité des trois tarifs GIR n'est pas une preuve d'appartenance à l'expérimentation —
elle se rencontre aussi dans 42 % des EHPAD du Rhône hors Métropole, qui n'est pas
territoire expérimentateur.

Utilisation :
    from regime import Regimes
    R = Regimes()
    R.pour(insee='69266', cp='69100')   # -> 'exp'  (Villeurbanne, Métropole de Lyon)
    R.pour(insee='69123', cp='69003')   # -> 'exp'  (Lyon)
    R.pour(insee='69264', cp='69400')   # -> 'classique' (Villefranche, Rhône)
"""
import json, os, datetime

B = os.path.dirname(os.path.abspath(__file__))


class Regimes:
    def __init__(self, chemin=None, communes_metropole=None):
        self.ref = json.load(open(chemin or os.path.join(B, 'regimes.json'), encoding='utf-8'))
        exp = self.ref['experimentation_fusion']
        self.debut = exp['debut']
        self.codes_dep = {t['code'] for t in exp['territoires'] if t['type'] == 'departement'}
        # La Métropole de Lyon ne se déduit pas d'un code postal : il faut la liste des communes.
        self.communes_metropole = set(communes_metropole or self._charge_metropole())
        self.pf = exp['participation_forfaitaire']

    def _charge_metropole(self):
        f = os.path.join(B, 'metropole_lyon.json')
        if os.path.exists(f):
            return json.load(open(f, encoding='utf-8'))
        return set()

    # ------------------------------------------------------------------ régime
    def pour(self, insee=None, cp=None):
        """Retourne 'exp', 'classique' ou 'inconnu'."""
        if insee:
            s = str(insee)
            if s in self.communes_metropole:
                return 'exp'
            # arrondissements de Lyon : 69381 à 69389 dans FINESS, 691xx en code postal
            if s.startswith('6938') or s.startswith('6912'):
                return 'exp'
            dep = self._dep(s)
            if dep in self.codes_dep:
                return 'exp'
            if dep:
                return 'classique'
        if cp:
            dep = str(cp)[:3] if str(cp)[:2] in ('97', '98') else str(cp)[:2]
            # le 69 est ambigu sans code commune : Métropole ou département du Rhône
            if dep == '69':
                return 'inconnu'
            if dep in self.codes_dep:
                return 'exp'
            return 'classique'
        return 'inconnu'

    @staticmethod
    def _dep(insee):
        s = str(insee or '')
        if s[:3] in ('971', '972', '973', '974', '975', '976'):
            return s[:3]
        if s[:2] == '20':
            return '2A' if s[:3] < '202' else '2B'
        return s[:2] or None

    # ------------------------------- participation forfaitaire à une date donnée
    def participation(self, date=None):
        """Montant journalier de la participation forfaitaire applicable à cette date,
        avec sa source. Retourne None si la date précède l'expérimentation."""
        d = date or datetime.date.today().isoformat()
        retenu = None
        for p in self.pf:
            if p['debut'] <= d and (p['fin'] is None or d <= p['fin']):
                retenu = p
        return retenu

    def resume(self):
        exp = self.ref['experimentation_fusion']
        return {
            'verifie_le': self.ref['verifie_le'],
            'debut': exp['debut'],
            'fin_annoncee': exp['fin_annoncee'],
            'fin_incertaine': exp['fin_incertaine'],
            'note_fin': exp['note_fin'],
            'territoires': len(exp['territoires']),
            'participation': self.participation(),
            'exclusions': exp['exclusions'],
            'sources': exp['sources'],
        }


if __name__ == '__main__':
    R = Regimes()
    print('participation forfaitaire applicable aujourd’hui :', R.participation())
    for insee, attendu, lib in [
        ('69266', 'exp', 'Villeurbanne — Métropole de Lyon'),
        ('69123', 'exp', 'Lyon — Métropole de Lyon'),
        ('69264', 'classique', 'Villefranche-sur-Saône — département du Rhône'),
        ('56260', 'exp', 'Morbihan'),
        ('75056', 'classique', 'Paris'),
        ('93066', 'exp', 'Seine-Saint-Denis'),
        ('97411', 'exp', 'La Réunion'),
        ('2A004', 'classique', 'Corse-du-Sud'),
    ]:
        got = R.pour(insee=insee)
        print('  %-6s %-46s %-10s %s' % (insee, lib, got, 'OK' if got == attendu else 'ATTENDU ' + attendu))
