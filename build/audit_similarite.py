# -*- coding: utf-8 -*-
"""Mesure de la part de texte gabarit sur les pages générées (fiches, villes, départements).

Même méthode que l'audit SEO du 29/09/2026 : 50 pages tirées au hasard (graine 42), texte de
<main> hors fils d'Ariane, phrases de plus de 20 caractères.
  · « partagées » : part médiane des phrases d'une page présentes à l'identique sur au moins
    une autre page de l'échantillon ;
  · « masquées » : idem une fois les nombres remplacés par # (mesure le gabarit pur) ;
  · Jaccard : similarité médiane des 5-grammes de mots entre deux pages.
Usage : python3 audit_similarite.py [dossier_site]"""
import os, re, sys, random, statistics as st, collections, glob
from lxml import html as LH

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')

def texte(p):
    doc = LH.fromstring(open(p, 'rb').read())
    if doc.xpath('//meta[@http-equiv="refresh"]'): return None
    for b in doc.xpath('//script|//style|//noscript'): b.getparent().remove(b)
    m = doc.xpath('//main')
    if not m: return None
    for n in m[0].xpath('.//nav'): n.getparent().remove(n)
    return doc.xpath('//body/@data-type')[0] if doc.xpath('//body/@data-type') else '', ' '.join(m[0].text_content().split())

def phrases(s): return [x.strip() for x in re.split(r'(?<=[.!?])\s+', s) if len(x.strip()) > 20]
def sh(s, k=5):
    w = s.lower().split(); return set(tuple(w[i:i + k]) for i in range(len(w) - k + 1))

pages = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(SITE, 'ehpad', '**', 'index.html'), recursive=True)):
    r = texte(p)
    if r: pages[r[0]].append(r[1])

res = {}
for typ in ('etablissement', 'ville', 'departement'):
    L = pages.get(typ, [])
    if len(L) < 50: continue
    random.seed(42); S = random.sample(L, 50)
    ss = [set(phrases(t)) for t in S]
    mk = lambda x: re.sub(r'\d[\d\s,.]*', '#', x)
    ssm = [set(mk(x) for x in s) for s in ss]
    c = collections.Counter(x for s in ss for x in s); cm = collections.Counter(x for s in ssm for x in s)
    part = st.median(sum(1 for x in s if c[x] >= 2) / len(s) for s in ss if s)
    partm = st.median(sum(1 for x in s if cm[x] >= 2) / len(s) for s in ssm if s)
    shs = [sh(t) for t in S]
    j = st.median(len(shs[a] & shs[b]) / len(shs[a] | shs[b]) for a in range(50) for b in range(a + 1, 50))
    mots = st.median(len(t.split()) for t in L)
    res[typ] = (part, partm, j, mots)
    print(f'{typ:14s} pages={len(L):5d}  phrases partagées={part:.0%}  masquées={partm:.0%}  Jaccard 5-g={j:.2f}  mots médians={mots:.0f}')
