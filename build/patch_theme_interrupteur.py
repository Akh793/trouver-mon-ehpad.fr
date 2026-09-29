# -*- coding: utf-8 -*-
"""Le bouton de thème devient un interrupteur étiqueté « Sombre » (role=switch).

L'ancienne icône lune/soleil de 32 px, sans texte, passait inaperçue. Même
place, même classe .js-theme : seul l'aspect et l'état ARIA changent.
Idempotent : relancé, il ne modifie plus rien.
"""
import re, os
B = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(B, '..', 'site')

ANCIEN = re.compile(
    r'<button type="button" (id="theme-btn" )?class="tb-icon js-theme" aria-label="Passer au thème sombre" '
    r'title="Changer de thème">(<svg class="ico-lune".*?</svg>)(<svg class="ico-soleil".*?</svg>)</button>', re.S)

def bouton(m):
    ident = m.group(1) or ''
    return ('<button type="button" ' + ident + 'class="tb-icon tb-sw js-theme" role="switch" aria-checked="false" '
            'aria-label="Mode sombre" title="Mode sombre : activer ou désactiver">'
            '<span class="sw-txt" aria-hidden="true">Sombre</span>'
            '<span class="sw-piste" aria-hidden="true"><span class="sw-pouce">'
            + m.group(2) + m.group(3) + '</span></span></button>')

for f in ['index.template.html', 'build_pages.py', os.path.join('seo', 'layout.py')]:
    p = os.path.join(B, f); s = open(p, encoding='utf-8').read()
    s2, n = ANCIEN.subn(bouton, s)
    if n: open(p, 'w', encoding='utf-8').write(s2)
    print(f, ':', n, 'bouton(s) remplacé(s) ;', s2.count('tb-sw js-theme'), 'interrupteur(s) présent(s)')

JS_ANCIEN = """      b.setAttribute('aria-label', t === 'dark' ? 'Repasser au thème clair' : 'Passer au thème sombre');
      b.setAttribute('aria-pressed', String(t === 'dark'));"""
JS_NOUVEAU = """      b.setAttribute('aria-checked', String(t === 'dark'));   // interrupteur : role=switch"""
for p in [os.path.join(SITE, 'app.js'), os.path.join(B, 'seo_pages.js')]:
    s = open(p, encoding='utf-8').read()
    if JS_ANCIEN in s: s = s.replace(JS_ANCIEN, JS_NOUVEAU); open(p, 'w', encoding='utf-8').write(s)
    print(os.path.basename(p), ':', 'aria-checked' in s)

CSS = """
/* ---------- Interrupteur du mode sombre ----------
   Texte « Sombre » + curseur : l'état se lit sans survol ni infobulle.
   « button. » en tête : l'emporte sur .head-act .tb-icon et .top-in .tb-icon (seo.css).
   Contraste curseur / piste ≥ 3:1 dans les deux thèmes (WCAG 1.4.11). */
button.tb-icon.tb-sw{width:auto;height:34px;padding:0 .3rem 0 .75rem;display:inline-flex;align-items:center;
  gap:.5rem;border-radius:999px;font-family:inherit;font-size:.8rem;font-weight:600;white-space:nowrap;flex:0 0 auto}
button.tb-sw .sw-piste{position:relative;flex:0 0 auto;width:36px;height:20px;border-radius:999px;background:var(--mut);transition:background .2s}
button.tb-sw .sw-pouce{position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;
  color:#0f172a;display:grid;place-items:center;box-shadow:0 1px 3px rgba(0,0,0,.3);transition:transform .2s}
button.tb-sw .sw-pouce svg{width:10px;height:10px}
button.tb-sw .ico-lune{display:none}
button.tb-sw .ico-soleil{display:block}
[data-theme="dark"] button.tb-sw .sw-piste{background:var(--bl-t)}
[data-theme="dark"] button.tb-sw .sw-pouce{transform:translateX(16px);background:var(--pg);color:var(--ink)}
[data-theme="dark"] button.tb-sw .ico-lune{display:block}
[data-theme="dark"] button.tb-sw .ico-soleil{display:none}
@media (prefers-reduced-motion:reduce){button.tb-sw .sw-piste,button.tb-sw .sw-pouce{transition:none}}
"""
p = os.path.join(B, 'site.css'); s = open(p, encoding='utf-8').read()
if 'button.tb-icon.tb-sw' not in s: open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS)
print('site.css : interrupteur', 'button.tb-icon.tb-sw' in open(p, encoding='utf-8').read())
