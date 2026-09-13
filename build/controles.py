# -*- coding: utf-8 -*-
"""Contrôles automatiques sur les données publiées (mission §5.3).

À lancer après chaque import, avant publication :
    python3 controles.py            # rapport lisible
    python3 controles.py --json     # rapport machine
    python3 controles.py --ref      # enregistre l'état courant comme référence

Chaque contrôle a un niveau :
    bloquant   — la publication doit être interrompue
    alerte     — à examiner, la donnée est servie mais marquée
    info       — mesure suivie dans le temps

Rien n'est écrit en dur : tout est recalculé depuis site/data/dep/*.js.
"""
import json, os, re, sys, datetime, collections, statistics

B = os.path.dirname(os.path.abspath(__file__))
DEP = os.path.join(B, '..', 'site', 'data', 'dep')
COLS = json.load(open(os.path.join(B, 'cols_v2.json'), encoding='utf-8'))
IDX = {n: i for i, n in enumerate(COLS)}
REF = os.path.join(B, 'controles_reference.json')

# Le FINESS fait neuf caractères : deux de département — chiffres, ou 2A / 2B pour la
# Corse — puis sept chiffres. La règle « neuf chiffres » rejetait à tort la Corse.
RE_FINESS = re.compile(r'^(\d{2}|2A|2B)\d{7}$')


def charge():
    lignes, fichiers = [], sorted(f for f in os.listdir(DEP) if re.match(r'ehpad-.+\.js$', f))
    for f in fichiers:
        t = open(os.path.join(DEP, f), encoding='utf-8').read()
        for r in json.loads(t[t.find('['):t.rfind(']') + 1]):
            lignes.append((f, r))
    return lignes, fichiers


def v(r, nom):
    i = IDX.get(nom)
    return r[i] if i is not None and i < len(r) else None


def main():
    lignes, fichiers = charge()
    rows = [r for _, r in lignes]
    auj = datetime.date.today().isoformat()
    res = []          # (niveau, code, libellé, nombre, exemples)

    def ctl(niveau, code, libelle, cas, exemples=None):
        res.append({'niveau': niveau, 'code': code, 'libelle': libelle,
                    'cas': len(cas) if hasattr(cas, '__len__') else cas,
                    'exemples': (exemples if exemples is not None else cas)[:5]})

    # ── 1. Identifiants : unicité, format, zéros de tête
    fin = [v(r, 'fin') for r in rows]
    doublons = [f for f, c in collections.Counter(fin).items() if c > 1]
    ctl('bloquant', 'fin.unicite', 'FINESS en double', doublons)
    mauvais = [f for f in fin if not (isinstance(f, str) and RE_FINESS.match(f))]
    ctl('bloquant', 'fin.format', 'FINESS hors format (2 car. de département + 7 chiffres)', mauvais)
    # Un FINESS stocké en nombre perdrait son zéro initial : 010001261 → 1001261.
    ctl('bloquant', 'fin.type', 'FINESS non stocké en chaîne (zéro de tête perdu)',
        [f for f in fin if not isinstance(f, str)])
    cp = [v(r, 'cp') for r in rows]
    ctl('bloquant', 'cp.format', 'Code postal hors format (5 caractères, chaîne)',
        [c for c in cp if c is not None and not (isinstance(c, str) and re.match(r'^\d{5}$', c))])

    # ── 2. Dates
    futures = [(v(r, 'fin'), v(r, 'nom'), v(r, 'hasD')) for r in rows
               if v(r, 'hasD') and str(v(r, 'hasD'))[:10] > auj]
    ctl('alerte', 'hasD.futur', 'Date d’évaluation HAS postérieure à aujourd’hui', futures)
    majs = [str(v(r, 'maj')) for r in rows if v(r, 'maj')]
    ctl('bloquant', 'maj.futur', 'Mois de déclaration de prix dans le futur',
        [m for m in majs if m > auj[:7]])
    ctl('info', 'maj.anciennete', 'Déclarations de prix de plus de 24 mois',
        [m for m in majs if m < (datetime.date.today() - datetime.timedelta(days=730)).isoformat()[:7]])

    # ── 3. Prix : valeurs impossibles, valeurs atypiques
    prix = [(v(r, 'fin'), v(r, 'p')) for r in rows if v(r, 'p') is not None]
    ctl('bloquant', 'p.signe', 'Prix journalier nul ou négatif', [x for x in prix if x[1] <= 0])
    vals = sorted(x[1] for x in prix)
    if vals:
        q1, med, q3 = (statistics.quantiles(vals, n=4) if len(vals) > 3 else (vals[0], vals[0], vals[-1]))
        haut = q3 + 3 * (q3 - q1)
        ctl('alerte', 'p.atypique', 'Prix journalier très au-dessus de la dispersion habituelle (q3 + 3 écarts interquartiles = %.2f €)' % haut,
            [x for x in prix if x[1] > haut])
        ctl('alerte', 'p.bas', 'Prix journalier inférieur à 30 €', [x for x in prix if x[1] < 30])

    # ── 4. Tarifs GIR : l'ordre t12 ≥ t34 ≥ t56 est une règle du barème
    desordre = []
    for r in rows:
        a, b_, c = v(r, 't12'), v(r, 't34'), v(r, 't56')
        if None in (a, b_, c):
            continue
        if a < b_ - 0.001 or b_ < c - 0.001:
            desordre.append((v(r, 'fin'), v(r, 'nom'), a, b_, c))
    ctl('alerte', 'gir.ordre', 'Tarifs GIR dans un ordre impossible (t12 < t34 ou t34 < t56)', desordre)

    # ── 5. Régime de financement
    regs = collections.Counter(v(r, 'reg') for r in rows)
    ctl('bloquant', 'reg.absent', 'Régime de financement non renseigné',
        [v(r, 'fin') for r in rows if v(r, 'reg') not in ('exp', 'classique', 'inconnu')])
    ctl('info', 'reg.repartition', 'Répartition des régimes : ' +
        ', '.join('%s %d' % (k, n) for k, n in sorted(regs.items(), key=lambda x: -x[1])), [])
    # Une égalité des trois tarifs GIR en régime classique est un signal, pas une preuve.
    egaux_classique = []
    for r in rows:
        a, b_, c = v(r, 't12'), v(r, 't34'), v(r, 't56')
        if None in (a, b_, c) or v(r, 'reg') != 'classique':
            continue
        if abs(a - b_) < 0.01 and abs(b_ - c) < 0.01:
            egaux_classique.append((v(r, 'fin'), v(r, 'nom'), a))
    ctl('alerte', 'gir.egaux_hors_exp',
        'Trois tarifs GIR identiques hors territoire d’expérimentation : l’APA ressort à zéro, le tarif réel est probablement différent',
        egaux_classique)

    # ── 6. Géographie
    sans_pos = [v(r, 'fin') for r in rows if v(r, 'lat') is None or v(r, 'lon') is None]
    ctl('alerte', 'geo.absente', 'Établissement sans coordonnées : absent de la carte', sans_pos)
    hors = [(v(r, 'fin'), v(r, 'lat'), v(r, 'lon')) for r in rows
            if v(r, 'lat') is not None and not (-25 < v(r, 'lat') < 52 and -64 < v(r, 'lon') < 56)]
    ctl('bloquant', 'geo.hors_france', 'Coordonnées hors des emprises françaises', hors)
    # Cohérence entre le département du FINESS et celui du fichier qui le sert.
    # Outre-mer : les FINESS commencent tous par « 970 », quel que soit le département
    # (971 Guadeloupe, 972 Martinique…). Le préfixe n'y détermine donc rien, et un
    # contrôle qui le supposerait signalerait 77 lignes parfaitement correctes.
    incoherents = []
    for f, r in lignes:
        dep_fichier = re.match(r'ehpad-(.+)\.js$', f).group(1)
        code = str(v(r, 'fin') or '')
        if code[:2] == '97':
            continue
        if code[:2] and code[:2] != dep_fichier:
            incoherents.append((v(r, 'fin'), f))
    ctl('bloquant', 'geo.fichier', 'Établissement servi dans le fichier d’un autre département (hors outre-mer)', incoherents)

    # ── 7. Qualité HAS : le dénominateur des critères impératifs est de 18
    hors_bornes = [(v(r, 'fin'), v(r, 'hasCI')) for r in rows
                   if v(r, 'hasCI') is not None and not (0 <= v(r, 'hasCI') <= 18)]
    ctl('bloquant', 'has.ci_bornes', 'Critères impératifs atteints hors de l’intervalle 0-18', hors_bornes)
    note_sans_date = [(v(r, 'fin'), v(r, 'hasN')) for r in rows if v(r, 'hasN') and not v(r, 'hasD')]
    ctl('alerte', 'has.note_sans_date', 'Note HAS publiée sans date d’évaluation : impossible de dire de quand elle date', note_sans_date)
    moy = [(v(r, 'fin'), v(r, 'hasM')) for r in rows
           if v(r, 'hasM') is not None and not (0 <= v(r, 'hasM') <= 100)]
    ctl('bloquant', 'has.moyenne_bornes', 'Moyenne des objectifs hors de l’intervalle 0-100', moy)
    chap = [(v(r, 'fin'), v(r, 'hasC')) for r in rows
            if isinstance(v(r, 'hasC'), list)
            and any(x is not None and not (0 <= x <= 4) for x in v(r, 'hasC'))]
    ctl('bloquant', 'has.chapitres_bornes', 'Score de chapitre hors de l’intervalle 0-4', chap)

    # ── 8. Couverture : comparaison avec la référence enregistrée
    couverture = {
        'lignes': len(rows),
        'avec_prix': sum(1 for r in rows if v(r, 'p') is not None or v(r, 'pcd') is not None),
        'avec_has': sum(1 for r in rows if v(r, 'hasN')),
        'avec_capacite': sum(1 for r in rows if v(r, 'cap')),
        'avec_position': len(rows) - len(sans_pos),
        'avec_tel': sum(1 for r in rows if v(r, 'tel')),
        'exp': regs.get('exp', 0), 'classique': regs.get('classique', 0), 'inconnu': regs.get('inconnu', 0),
    }
    perdus = []
    if os.path.exists(REF):
        ref = json.load(open(REF, encoding='utf-8'))
        for k, n in couverture.items():
            avant = ref.get('couverture', {}).get(k)
            # Une perte de plus de 2 % sur un champ déjà couvert est une régression d'import.
            if avant and n < avant * 0.98:
                perdus.append('%s : %d → %d (−%.1f %%)' % (k, avant, n, 100 * (1 - n / avant)))
    ctl('bloquant', 'couverture.perte', 'Champs dont la couverture recule de plus de 2 % depuis la dernière référence', perdus)

    if '--ref' in sys.argv:
        json.dump({'enregistre_le': auj, 'couverture': couverture},
                  open(REF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('référence enregistrée :', REF)

    rapport = {'date': auj, 'fichiers': len(fichiers), 'lignes': len(rows),
               'couverture': couverture, 'controles': res}
    if '--json' in sys.argv:
        print(json.dumps(rapport, ensure_ascii=False, indent=1))
    else:
        larg = 76
        print('=' * larg)
        print('CONTRÔLES AUTOMATIQUES — %s — %d lignes, %d fichiers' % (auj, len(rows), len(fichiers)))
        print('=' * larg)
        for k, n in couverture.items():
            print('  %-16s %6d  (%5.1f %%)' % (k, n, 100 * n / max(1, len(rows))))
        print('-' * larg)
        for c in res:
            marque = {'bloquant': '[BLOQUANT]', 'alerte': '[alerte]  ', 'info': '[info]    '}[c['niveau']]
            etat = 'OK' if c['cas'] == 0 else '%d cas' % c['cas']
            print('%s %-8s %s' % (marque, etat, c['libelle']))
            if c['cas'] and c['niveau'] != 'info':
                for ex in c['exemples']:
                    print('             · %s' % (ex,))
        print('-' * larg)

    bloquants = sum(c['cas'] for c in res if c['niveau'] == 'bloquant')
    if bloquants:
        print('%d anomalie(s) bloquante(s) : publication à interrompre.' % bloquants, file=sys.stderr)
    return 1 if bloquants else 0


if __name__ == '__main__':
    sys.exit(main())
