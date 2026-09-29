# -*- coding: utf-8 -*-
"""Barre de défilement sur téléphone : le bouton « Calculer mon reste à charge »
dépassait déjà de l'écran (droite coupée) ; l'interrupteur « Sombre », plus
large que l'ancienne icône, aggravait le débordement.

Sous 720 px : l'interrupteur de la barre perd son mot (le curseur reste, et son
nom accessible « Mode sombre » aussi) ; sous 480 px le bouton se réduit à
« Calculer », la suite restant lue par les lecteurs d'écran (masquage visuel,
pas display:none). Idempotent.
"""
import os
B = os.path.dirname(os.path.abspath(__file__))
for f in ['index.template.html', 'build_pages.py', os.path.join('seo', 'layout.py')]:
    p = os.path.join(B, f); s = open(p, encoding='utf-8').read()
    n = s.count('>Calculer mon reste à charge</a>')
    s = s.replace('class="tb-cta">Calculer mon reste à charge</a>',
                  'class="tb-cta">Calculer<span class="tb-cta-plus"> mon reste à charge</span></a>')
    s = s.replace('class="tb-cta" data-ev="seo_topbar_to_calculator">Calculer mon reste à charge</a>',
                  'class="tb-cta" data-ev="seo_topbar_to_calculator">Calculer<span class="tb-cta-plus"> mon reste à charge</span></a>')
    open(p, 'w', encoding='utf-8').write(s)
    print(f, ':', n, 'remplacé(s) ;', s.count('tb-cta-plus'), 'présent(s)')

CSS = """
/* ---------- Barre de défilement sur téléphone : rien ne dépasse de l'écran ---------- */
@media (max-width:720px){
  .topbar button.tb-sw .sw-txt{display:none}
  .topbar button.tb-icon.tb-sw{padding:0 .3rem}
}
@media (max-width:480px){
  .tb-cta-plus{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
}
"""
p = os.path.join(B, 'site.css'); s = open(p, encoding='utf-8').read()
if '.tb-cta-plus{' not in s: open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS)
print('site.css :', '.tb-cta-plus{' in open(p, encoding='utf-8').read())
