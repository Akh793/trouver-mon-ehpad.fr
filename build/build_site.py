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

def esc(s): return html.escape(s, quote=False)
faq_html = '\n'.join(
  '<details class="faq-i"%s><summary><span>%s</span></summary><p>%s</p></details>' % (' open' if i==0 else '', esc(q), esc(a))
  for i,(q,a) in enumerate(faq))
faq_ld = ',\n      '.join(json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}, ensure_ascii=False) for q,a in faq)

tpl = open('index.template.html', encoding='utf-8').read()
css = '\n'.join([open('vendor_leaflet.css', encoding='utf-8').read()]) if os.path.exists('vendor_leaflet.css') else ''
leaflet = open('vendor/leaflet.css', encoding='utf-8').read() + '\n' + open('vendor/markercluster.css', encoding='utf-8').read() + '\n' + open('vendor/markercluster.default.css', encoding='utf-8').read()
out = (tpl.replace('{FONTFACE}', open('fontface.css', encoding='utf-8').read())
          .replace('{LEAFLETCSS}', leaflet)
          .replace('{SITECSS}', open('site.css', encoding='utf-8').read())
          .replace('{FAQ_HTML}', faq_html)
          .replace('[FAQ_JSONLD]', '\n      ' + faq_ld + '\n    '))
open(SITE + '/index.html', 'w', encoding='utf-8').write(out)
print('index.html écrit :', len(out.encode()), 'octets ;', len(faq), 'questions synchronisées')
