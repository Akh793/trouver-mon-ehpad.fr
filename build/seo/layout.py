# -*- coding: utf-8 -*-
"""Gabarit commun des pages de contenu : en-tête, fil d'Ariane, pied de page, données structurées."""
import json
from base import DOMAINE, MARQUE, CONTACT, MAJ, MAJ_ISO, esc

AMORCE_THEME = """<script>/* Thème : appliqué avant le premier rendu, sinon la page clignote en blanc. */
(function(){try{var k='mon_ehpad_theme',t=localStorage.getItem(k);
if(t!=='dark'&&t!=='light')t=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';
if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}catch(e){}})();</script>"""

CONSENT = """<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500});
(function(){var K='mon_ehpad_consent',T=182*24*3600*1000,c=null;
try{var r=localStorage.getItem(K);if(r){var o=JSON.parse(r);if(o&&o.v&&Date.now()-o.t<T)c=o.v;else localStorage.removeItem(K);}}catch(e){}
function ap(v){gtag('consent','update',{analytics_storage:v==='granted'?'granted':'denied'});dataLayer.push({event:v==='granted'?'consent_granted':'consent_denied'});}
window.ME_consent={get:function(){return c;},set:function(v){c=v;try{localStorage.setItem(K,JSON.stringify({v:v,t:Date.now()}));}catch(e){}ap(v);},reset:function(){c=null;try{localStorage.removeItem(K);}catch(e){}}};
if(c)ap(c);})();
// Mesure d'usage : uniquement des événements de navigation, aucune donnée personnelle.
document.addEventListener('click',function(e){var a=e.target.closest('[data-ev]');if(!a)return;
dataLayer.push({event:a.dataset.ev,seo_page:document.body.dataset.type||'',seo_lieu:document.body.dataset.lieu||''});});
</script>"""

BANDEAU = """<div id="consent-banner" hidden><div class="cb">
<p>Ce site peut utiliser une mesure d’audience, uniquement si vous l’acceptez. Les informations que vous saisissez dans le calculateur ne sont jamais transmises : elles restent sur votre appareil. <a href="/mentions-legales.html#cookies">En savoir plus</a></p>
<div class="cb-b"><button type="button" id="consent-accept" class="btn">Accepter</button>
<button type="button" id="consent-refuse" class="lien">Continuer sans accepter</button></div></div></div>"""

TOPBAR = """<div id="topbar" class="topbar print-hide">
<div class="topbar-in">
<a class="tb-logo" href="/">Trouver mon <span>EHPAD</span></a>
<div class="tb-r">
<div class="tb-nav-wrap">
<button type="button" id="tb-nav" class="tb-btn" aria-expanded="false" aria-controls="tb-menu" aria-haspopup="true"><span>Naviguer</span><svg viewBox="0 0 12 12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4l4 4 4-4"/></svg></button>
<nav id="tb-menu" class="tb-menu" hidden aria-label="Navigation rapide">
<a href="/">Le calculateur</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix des EHPAD</a>
<a href="/aides-ehpad/">Aides financières</a>
<a href="/guides/">Guides</a>
<a href="/professionnels/">Espace professionnel</a>
<hr>
<a href="/notre-methodologie.html">Notre méthodologie</a>
<a href="/qui-sommes-nous.html">Qui sommes-nous&nbsp;?</a>
<a href="/retours/">Vos retours</a>
</nav>
</div>
<button type="button" id="theme-btn" class="tb-icon js-theme" aria-label="Passer au thème sombre" title="Changer de thème"><svg class="ico-lune" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5a7 7 0 1 0 8.9 8.9Z"/></svg><svg class="ico-soleil" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.6v2M10 16.4v2M2.6 10h-2M19.4 10h-2M4.8 4.8 3.4 3.4M16.6 16.6l-1.4-1.4M15.2 4.8l1.4-1.4M3.4 16.6l1.4-1.4"/></svg></button>
<a href="/retours/" class="tb-avis">Vos retours</a>
<a href="/" class="tb-cta" data-ev="seo_topbar_to_calculator">Calculer mon reste à charge</a>
</div>
</div>
<div class="tb-prog" aria-hidden="true"><i id="tb-prog"></i></div>
</div>"""

NAV = """<header class="top"><div class="top-in">
<a class="logo" href="/">Trouver mon <span>EHPAD</span></a>
<nav aria-label="Navigation principale">
<a href="/">Calculateur</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix</a>
<a href="/aides-ehpad/">Aides</a>
<a href="/guides/">Guides</a>
<a href="/notre-methodologie.html">Méthodologie</a>
</nav>
<button type="button" class="tb-icon js-theme" aria-label="Passer au thème sombre" title="Changer de thème"><svg class="ico-lune" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5a7 7 0 1 0 8.9 8.9Z"/></svg><svg class="ico-soleil" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.6v2M10 16.4v2M2.6 10h-2M19.4 10h-2M4.8 4.8 3.4 3.4M16.6 16.6l-1.4-1.4M15.2 4.8l1.4-1.4M3.4 16.6l1.4-1.4"/></svg></button></div></header>"""

PIED = f"""<footer class="foot"><div class="foot-in">
<nav aria-label="Pied de page">
<a href="/">Le calculateur</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix des EHPAD</a>
<a href="/aides-ehpad/">Aides financières</a>
<a href="/guides/">Guides</a>
<a href="/professionnels/">Espace professionnel</a>
<a href="/notre-methodologie.html">Méthodologie</a>
<a href="/qui-sommes-nous.html">Qui sommes-nous ?</a>
<a href="/retours/">Vos retours</a>
<a href="/mentions-legales.html">Mentions légales</a>
<a href="#" data-consent-open>Gérer les cookies</a>
</nav>
<p>© 2026 {MARQUE} — service indépendant, gratuit, sans publicité et sans partenariat avec des établissements. Ce site n’est pas un service public.</p>
</div></footer>"""


def titre_page(base, marque=True):
    """La marque n'est ajoutée que si le titre reste lisible dans une page de résultats."""
    if marque and len(base) <= 44:
        return f'{base} | {MARQUE}'
    return base


def fil(items):
    """items : liste de (libellé, url ou None pour la page courante)."""
    h = ['<nav class="fil-ariane" aria-label="Fil d’Ariane">']
    parts = []
    for i, (lib, url) in enumerate(items):
        if url:
            parts.append(f'<a href="{url}">{esc(lib)}</a>')
        else:
            parts.append(f'<span aria-current="page">{esc(lib)}</span>')
    h.append(' <span aria-hidden="true">›</span> '.join(parts))
    h.append('</nav>')
    ld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": lib,
         **({"item": DOMAINE + url} if url else {})}
        for i, (lib, url) in enumerate(items)]}
    return ''.join(h), ld


def jsonld_socle():
    return [
        {"@type": "WebSite", "@id": DOMAINE + "/#website", "url": DOMAINE + "/", "name": MARQUE,
         "description": "Comprendre, comparer et estimer le coût réel des EHPAD en France.",
         "inLanguage": "fr-FR", "publisher": {"@id": DOMAINE + "/#organization"}},
        {"@type": "Organization", "@id": DOMAINE + "/#organization", "name": MARQUE,
         "url": DOMAINE + "/", "email": CONTACT,
         "areaServed": {"@type": "Country", "name": "France"}},
    ]


def page(url, titre, description, corps, ariane, ld_extra=None, robots='index, follow',
         type_page='', lieu='', h1=None, maj=True):
    """Assemble une page complète. `url` commence et finit par « / » (ou pointe un fichier)."""
    ariane_html, ld_fil = fil(ariane)
    graph = jsonld_socle() + [ld_fil] + (ld_extra or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, separators=(',', ':'))
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{AMORCE_THEME}
<title>{esc(titre)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{DOMAINE}{url}">
<meta name="robots" content="{robots}">
<meta property="og:title" content="{esc(titre)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAINE}{url}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{MARQUE}">
<meta property="og:image" content="{DOMAINE}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{DOMAINE}/assets/og-image.png">
<meta name="theme-color" content="#2548FF">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{ld}</script>
<script src="/assets/pages.js" defer></script>
</head>
<body data-type="{esc(type_page)}" data-lieu="{esc(lieu)}">
{TOPBAR}
{NAV}
<main class="wrap">
{ariane_html}
{corps}
</main>
{PIED}
{BANDEAU}
</body>
</html>
"""
