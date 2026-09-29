# -*- coding: utf-8 -*-
"""Souligne les mots du lexique dans les pages générées (29/09/2026). À lancer EN DERNIER, après
build_site, build_pages, build_retours, build_devis et seo/build_seo.

Règles (décisions de l'éditeur) :
  · première occurrence de chaque terme par page, jamais plus ;
  · lien vers /lexique/#terme, bulle au survol ou au focus (data-def, affichée en CSS) ;
  · uniquement dans le contenu (<main>, ou <section class="page"> des pages annexes), jamais dans
    un titre, un lien, un bouton, un libellé de formulaire, un résumé dépliable, un tableau, un menu,
    le pied de page, un script ou les données structurées ;
  · pas de lien vers le lexique sur la page qui approfondit déjà le terme (APA sur la page APA),
    ni sur le lexique lui-même, ni sur les pages de redirection (sans contenu).

Idempotent : les liens posés par une exécution précédente sont retirés avant d'être reposés.
Écrit aussi site/data/lexique.js, que l'accueil utilise pour les textes calculés en direct
(fiche d'établissement, étapes)."""
import html as H, io, json, os, re, sys

B = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(B, '..', 'site')
TERMES = json.load(open(os.path.join(B, 'lexique.json'), encoding='utf-8'))['termes']

ESP = r'(?:[   ]|&nbsp;|&#160;)+'
APO = r'(?:’|\'|&rsquo;|&#8217;)'
MOT = r'[0-9A-Za-zÀ-ÖØ-öø-ÿŒœ_]'


def motif(v):
    """Variante → expression : espaces et apostrophes tolérants, majuscule initiale admise pour les
    expressions en minuscules (début de phrase), casse stricte pour les sigles."""
    parts = []
    for i, ch in enumerate(v):
        if ch in '   ':
            if not parts or parts[-1] != ESP: parts.append(ESP)
        elif ch in '’\'':
            parts.append(APO)
        elif i == 0 and ch.islower():
            parts.append(f'[{ch}{ch.upper()}]')
        else:
            parts.append(re.escape(ch))
    return ''.join(parts)


VARIANTES = []          # (expression, id), les plus longues d'abord : « tarif global de soins » avant « tarif global »
for t in TERMES:
    for v in set(t['variantes']):
        VARIANTES.append((motif(v), t['id'], len(v)))
VARIANTES.sort(key=lambda x: -x[2])
GRAND = re.compile(f'(?<!{MOT})(?:' + '|'.join(f'(?P<t{i}>{e})' for i, (e, _, _) in enumerate(VARIANTES)) + f')(?!{MOT})')
ID_DE = {f't{i}': tid for i, (_, tid, _) in enumerate(VARIANTES)}
COURT = {t['id']: t['court'] for t in TERMES}
LIEN = {t['id']: t.get('lien') for t in TERMES}

SAUTER = {'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'button', 'label', 'legend', 'summary', 'script', 'style',
          'title', 'nav', 'footer', 'header', 'select', 'option', 'textarea', 'svg', 'code', 'table',
          'figcaption', 'noscript', 'template', 'dt'}
VIDES = {'br', 'img', 'input', 'hr', 'meta', 'link', 'source', 'wbr', 'col', 'area', 'base', 'embed', 'param', 'track'}
BALISE = re.compile(r'(<!--.*?-->|<[^>]+>)', re.S)
ANCIENS = re.compile(r'<a class="lx" href="/lexique/#[^"]*" data-def="[^"]*">(.*?)</a>', re.S)


def zone(s):
    """Début et fin de la partie à traiter, ou None."""
    m = re.search(r'<main\b[^>]*>', s)
    if m:
        f = s.rfind('</main>')
        return (m.end(), f) if f > m.end() else None
    m = re.search(r'<section class="page"[^>]*>', s)
    if m:
        f = s.find('</section>\n<footer', m.end())
        if f < 0: f = s.rfind('</section>')
        return (m.end(), f) if f > m.end() else None
    return None


def lier(s, url):
    s = ANCIENS.sub(r'\1', s)
    z = zone(s)
    if not z: return s, 0
    deb, fin = z
    morceaux = BALISE.split(s[deb:fin])
    pile = []          # balises « à sauter » ouvertes
    vus = set()
    n = 0
    for i, m in enumerate(morceaux):
        if not m: continue
        if m.startswith('<'):
            if m.startswith('<!--'): continue
            nom = re.match(r'</?\s*([a-zA-Z0-9]+)', m)
            if not nom: continue
            nom = nom.group(1).lower()
            if nom in VIDES or m.endswith('/>'): continue
            if m.startswith('</'):
                if nom in SAUTER and nom in pile:
                    while pile and pile.pop() != nom: pass
            elif nom in SAUTER:
                pile.append(nom)
            continue
        if pile: continue

        def rempl(mm):
            nonlocal n
            tid = ID_DE[mm.lastgroup]
            if tid in vus or LIEN.get(tid) == url or url == '/lexique/':
                return mm.group(0)
            vus.add(tid); n += 1
            return (f'<a class="lx" href="/lexique/#{tid}" data-def="{H.escape(COURT[tid], quote=True)}">'
                    f'{mm.group(0)}</a>')
        morceaux[i] = GRAND.sub(rempl, m)
    return s[:deb] + ''.join(morceaux) + s[fin:], n


def url_de(chemin):
    r = os.path.relpath(chemin, SITE).replace(os.sep, '/')
    if r == 'index.html': return '/'
    if r.endswith('/index.html'): return '/' + r[:-len('index.html')]
    return '/' + r


def main():
    ignore = {'/mentions-legales.html', '/404.html', '/lexique/'}
    total = pages = 0
    for rac, _, fs in os.walk(SITE):
        for f in fs:
            if not f.endswith('.html'): continue
            p = os.path.join(rac, f); u = url_de(p)
            s = io.open(p, encoding='utf-8').read()
            if u in ignore:
                s2 = ANCIENS.sub(r'\1', s); k = 0
            else:
                s2, k = lier(s, u)
            if s2 != s:
                io.open(p, 'w', encoding='utf-8').write(s2)
            total += k; pages += 1 if k else 0
    # dictionnaire pour les textes calculés dans la page d'accueil
    js = [{'id': t['id'], 'c': t['court'], 'v': sorted(set(t['variantes']), key=len, reverse=True)} for t in TERMES]
    os.makedirs(os.path.join(SITE, 'data'), exist_ok=True)
    io.open(os.path.join(SITE, 'data', 'lexique.js'), 'w', encoding='utf-8').write(
        '/* Lexique : termes, bulle courte et variantes repérées (généré par build/lexique_liens.py) */\n'
        'window.LEXIQUE=' + json.dumps(js, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'lexique : {total} mots soulignés sur {pages} pages ; data/lexique.js écrit ({len(js)} termes)')


def lier_fichier(chemin):
    """Un seul fichier (utilisé par build_site.py pour l'accueil)."""
    s = io.open(chemin, encoding='utf-8').read()
    s2, k = lier(s, url_de(chemin))
    if s2 != s: io.open(chemin, 'w', encoding='utf-8').write(s2)
    return k


if __name__ == '__main__':
    main()
