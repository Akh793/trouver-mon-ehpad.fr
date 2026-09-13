# -*- coding: utf-8 -*-
"""Audit de la version publiée : on recompte tout depuis les fichiers départementaux
réellement servis (site/data/dep/*.js), pas depuis les sources intermédiaires.

Aucun chiffre n'est écrit en dur : tout est recalculé à chaque exécution.
    python3 audit_v3.py
"""
import json, os, re, sys, collections, datetime, statistics

B = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(B, '..', 'site')
DEP = os.path.join(SITE, 'data', 'dep')

# Le mappage des colonnes, tel que le moteur le lit (site/app.js, const C)
COLS = json.load(open(os.path.join(B, 'cols_v2.json'), encoding='utf-8')) \
    if os.path.exists(os.path.join(B, 'cols_v2.json')) else None


def charge_dep():
    """Relit les tableaux compacts servis au navigateur."""
    lignes = []
    fichiers = sorted(f for f in os.listdir(DEP) if re.match(r'ehpad-.+\.js$', f))
    for f in fichiers:
        t = open(os.path.join(DEP, f), encoding='utf-8').read()
        i, j = t.find('['), t.rfind(']')
        data = json.loads(t[i:j + 1])
        for r in data:
            lignes.append(r)
    return lignes, fichiers


def main():
    rows, fichiers = charge_dep()
    C = COLS
    if C is None:
        print('cols_v2.json introuvable : impossible de nommer les colonnes')
        sys.exit(1)
    idx = {n: i for i, n in enumerate(C)} if isinstance(C, list) else C

    def v(r, nom):
        i = idx.get(nom)
        return r[i] if i is not None and i < len(r) else None

    aujourdhui = datetime.date.today().isoformat()
    out = collections.OrderedDict()
    out['fichiers departementaux'] = len(fichiers)
    out['lignes'] = len(rows)
    fin = [v(r, 'fin') for r in rows]
    out['FINESS uniques'] = len(set(fin))
    out['FINESS non conformes (9 chiffres)'] = sum(1 for f in fin if not (isinstance(f, str) and re.fullmatch(r'\d{9}', f)))

    p = [v(r, 'p') for r in rows]
    pcd = [v(r, 'pcd') for r in rows]
    pa = [v(r, 'pa') for r in rows]
    utilisable = [i for i in range(len(rows)) if p[i] is not None or pcd[i] is not None]
    out['avec prix permanent simple ou double'] = len(utilisable)
    sans = [i for i in range(len(rows)) if p[i] is None and pcd[i] is None]
    out['sans prix permanent'] = len(sans)
    out['  dont un tarif ASH renseigne'] = sum(1 for i in sans if pa[i] is not None)
    out['prix double sans prix simple'] = sum(1 for i in range(len(rows)) if p[i] is None and pcd[i] is not None)

    maj = [v(r, 'maj') for r in rows]
    def annee(m):
        if not m: return None
        s = str(m)
        mm = re.match(r'(\d{4})', s)
        return int(mm.group(1)) if mm else None
    out['tarifs utilisables declares en 2025'] = sum(1 for i in utilisable if annee(maj[i]) == 2025)
    def avant_oct2025(m):
        if not m: return False
        s = str(m)
        mm = re.match(r'(\d{4})-(\d{2})', s)
        if not mm: return False
        a, mo = int(mm.group(1)), int(mm.group(2))
        return (a < 2025) or (a == 2025 and mo <= 9)
    out['tarifs utilisables de 09/2025 ou avant'] = sum(1 for i in utilisable if avant_oct2025(maj[i]))

    out['evaluations HAS'] = sum(1 for r in rows if v(r, 'hasN'))
    out['inspections hygiene appariees'] = sum(1 for r in rows if v(r, 'alim'))
    out['capacites renseignees'] = sum(1 for r in rows if v(r, 'cap'))
    out['sans coordonnees'] = sum(1 for r in rows if v(r, 'lat') is None or v(r, 'lon') is None)
    out['positions = centre de commune'] = sum(1 for r in rows if v(r, 'approx'))

    def deux_dec(x):
        if x is None: return False
        s = repr(float(x))
        if '.' not in s: return True
        return len(s.split('.')[1].rstrip('0')) <= 2
    out['positions a 2 decimales au plus'] = sum(
        1 for r in rows if v(r, 'lat') is not None and deux_dec(v(r, 'lat')) and deux_dec(v(r, 'lon')))

    out['valeurs de taux d occupation'] = sum(1 for r in rows if v(r, 'occ') is not None)
    out['valeurs de densite'] = sum(1 for r in rows if v(r, 'dens') is not None)

    # --- anomalies ponctuelles citees par l'audit
    print('=' * 74)
    print('AUDIT DE LA VERSION PUBLIEE —', aujourdhui)
    print('=' * 74)
    for k, val in out.items():
        print('%-46s %8s' % (k, val))

    print()
    print('--- dates HAS dans le futur ---')
    fut = []
    for r in rows:
        d = v(r, 'hasD')
        if d and str(d) > aujourdhui:
            fut.append((v(r, 'fin'), v(r, 'nom'), d))
    print('  %d cas' % len(fut))
    for f in fut[:6]:
        print('   ', f)

    print()
    print('--- ordre des tarifs GIR incoherent (t12 < t34 ou t34 < t56) ---')
    inc = []
    for r in rows:
        a, b2, c = v(r, 't12'), v(r, 't34'), v(r, 't56')
        if None in (a, b2, c): continue
        if a < b2 - 1e-9 or b2 < c - 1e-9:
            inc.append((v(r, 'fin'), v(r, 'nom'), a, b2, c))
    print('  %d cas' % len(inc))
    for f in inc[:6]:
        print('   ', f)

    print()
    print('--- egalite des trois tarifs GIR (peut etre normale : experimentation) ---')
    eg = [r for r in rows if None not in (v(r, 't12'), v(r, 't34'), v(r, 't56'))
          and abs(v(r, 't12') - v(r, 't56')) < 0.01 and abs(v(r, 't34') - v(r, 't56')) < 0.01]
    print('  %d etablissements' % len(eg))
    dep_eg = collections.Counter(str(v(r, 'cp'))[:2] for r in eg)
    print('  repartition par debut de code postal (10 premiers) :')
    for d, n in dep_eg.most_common(10):
        tot = sum(1 for r in rows if str(v(r, 'cp'))[:2] == d)
        print('    %s : %4d / %4d  (%.0f %%)' % (d, n, tot, 100 * n / tot if tot else 0))

    print()
    print('--- prix atypiques ---')
    px = [x for x in p if x]
    px.sort()
    if px:
        print('  min %.2f  q1 %.2f  mediane %.2f  q3 %.2f  max %.2f'
              % (px[0], px[len(px)//4], statistics.median(px), px[3*len(px)//4], px[-1]))
        print('  nuls ou negatifs :', sum(1 for x in p if x is not None and x <= 0))
        print('  au-dessus de 200 €/jour :', sum(1 for x in px if x > 200))

    print()
    print('--- cas de controle : Accueil des Buers (690025192) ---')
    for r in rows:
        if v(r, 'fin') == '690025192':
            for nom in ('nom', 'ville', 'p', 'pcd', 'pa', 't12', 't34', 't56', 'maj', 'cap', 'ash', 'hasN', 'occ'):
                print('   %-6s %s' % (nom, v(r, nom)))
            break
    else:
        print('   introuvable')


if __name__ == '__main__':
    main()
