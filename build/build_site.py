# -*- coding: utf-8 -*-
"""Assemble index.html : CSS inlinés, FAQ synchronisée avec data.js (texte identique au balisage FAQPage)."""
import json, subprocess, html, re, os
SITE='../site'
# json.dumps produit un littéral de chaîne JavaScript correctement échappé.
# Sans lui, un chemin Windows « C:\Users\rival\… » voit ses \U, \r, \t interprétés
# comme des séquences d'échappement par Node, et le require échoue.
_data = json.dumps(os.path.join(os.path.abspath(SITE), 'data.js').replace('\\', '/'))
faq = json.loads(subprocess.check_output(['node','-e',
  "global.window={};require(%s);console.log(JSON.stringify(window.FAQ))" % _data]).decode())

# Un seul balisage est admis dans une réponse : un lien interne. Tout le reste est
# échappé. Sans cette liste blanche, la balise <a> d'une réponse ressortait telle
# quelle à l'écran — « <a href="…">Les conditions</a> » affiché en toutes lettres.
LIEN = re.compile(r'&lt;a href="(/[^"&<>]*)"&gt;([^&<>]+)&lt;/a&gt;')

def esc(s):
  """Échappe un texte pouvant déjà contenir des entités HTML : on les résout d'abord,
  sinon « &nbsp; » ressortirait en « &amp;nbsp; », affiché littéralement par le navigateur.
  Les liens internes sont ensuite rétablis, eux seuls."""
  return LIEN.sub(r'<a href="\1">\2</a>', html.escape(html.unescape(s), quote=False))

def nu(s):
  """Texte nu pour les données structurées : ni entité, ni espace insécable.
  Le lien est conservé : Google admet <a> dans un Answer.text, et le retirer
  laissait « Les conditions. » en fragment orphelin, sans rien à désigner."""
  return re.sub(r'\s+', ' ', html.unescape(s).replace('\u00a0', ' ')).strip()
faq_html = '\n'.join(
  '<details class="faq-i"%s><summary><span>%s</span></summary><p>%s</p></details>' % (' open' if i==0 else '', esc(q), esc(a))
  for i,(q,a) in enumerate(faq))
faq_ld = ',\n      '.join(json.dumps({"@type":"Question","name":nu(q),"acceptedAnswer":{"@type":"Answer","text":nu(a)}}, ensure_ascii=False) for q,a in faq)

tpl = open('index.template.html', encoding='utf-8').read()
css = '\n'.join([open('vendor_leaflet.css', encoding='utf-8').read()]) if os.path.exists('vendor_leaflet.css') else ''
leaflet = open('vendor/leaflet.css', encoding='utf-8').read() + '\n' + open('vendor/markercluster.css', encoding='utf-8').read() + '\n' + open('vendor/markercluster.default.css', encoding='utf-8').read()
out = (tpl.replace('{FONTFACE}', open('fontface.css', encoding='utf-8').read())
          .replace('{LEAFLETCSS}', leaflet)
          .replace('{SITECSS}', open('site.css', encoding='utf-8').read())
          .replace('{FAQ_HTML}', faq_html)
          # Le gabarit porte « "mainEntity": [FAQ_JSONLD] » : les crochets sont ceux du
          # tableau JSON. Les remplacer avec le marqueur produisait « "mainEntity": {…},{…} »,
          # un JSON-LD invalide qu'aucun moteur ne lisait. On ne remplace que le marqueur.
          .replace('FAQ_JSONLD', '\n      ' + faq_ld + '\n    '))
open(SITE + '/index.html', 'w', encoding='utf-8').write(out)
print('index.html écrit :', len(out.encode()), 'octets ;', len(faq), 'questions synchronisées')

# --- contrôle : tout bloc de données structurées doit être du JSON valide.
# Sans ce contrôle, une virgule de trop passe en production sans bruit.
_erreurs = 0
for _i, _b in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S)):
    try:
        _d = json.loads(_b)
    except ValueError as _e:
        print('JSON-LD invalide (bloc %d) : %s' % (_i, _e)); _erreurs += 1
        continue
    _g = _d.get('@graph') if isinstance(_d, dict) else None
    for _n in (_g or [_d]):
        if _n.get('@type') == 'FAQPage' and not isinstance(_n.get('mainEntity'), list):
            print('JSON-LD : mainEntity d’une FAQPage doit être un tableau'); _erreurs += 1
if _erreurs:
    raise SystemExit('%d anomalie(s) de données structurées : index.html non publiable.' % _erreurs)
print('données structurées : %d bloc(s) JSON-LD valides' % len(re.findall(r'application/ld\+json', out)))
