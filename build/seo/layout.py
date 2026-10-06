# -*- coding: utf-8 -*-
"""Gabarit commun des pages de contenu : en-tête, fil d'Ariane, pied de page, données structurées."""
import json, os, sys
from base import DOMAINE, MARQUE, CONTACT, MAJ, MAJ_ISO, esc, AUTEUR, AUTEUR_URL, AUTEUR_BIO
# mesure.py vit dans build/, un cran au-dessus de seo/ : une seule adresse
# de service pour les trois gabarits, sinon ils divergent en silence.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mesure
import reassurance
MESURE = mesure.extrait()

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
<a class="tb-logo" href="/">Trouver mon <span>EHPAD</span><b class="tld">.fr</b></a>
<div class="tb-r">
<div class="tb-nav-wrap">
<button type="button" id="tb-nav" class="tb-btn" aria-expanded="false" aria-controls="tb-menu" aria-haspopup="true"><span>Naviguer</span><svg viewBox="0 0 12 12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4l4 4 4-4"/></svg></button>
<nav id="tb-menu" class="tb-menu" hidden aria-label="Navigation rapide">
<a href="/">Accueil</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix des EHPAD</a>
<a href="/aides-ehpad/">Aides financières</a>
<a href="/guides/">Guides</a>
<a href="/professionnels/">Espace professionnel</a>
<a href="/lexique/">Lexique</a>
<hr>
<a href="/qui-sommes-nous.html">Qui sommes-nous&nbsp;?</a>
<a href="/comparer-devis-ehpad/" class="menu-devis">Comparer vos devis</a>
<a href="/retours/">Vos retours</a>
</nav>
</div>
<button type="button" id="theme-btn" class="tb-icon tb-sw js-theme" role="switch" aria-checked="false" aria-label="Mode sombre" title="Mode sombre : activer ou désactiver"><span class="sw-txt" aria-hidden="true">Sombre</span><span class="sw-piste" aria-hidden="true"><span class="sw-pouce"><svg class="ico-lune" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5a7 7 0 1 0 8.9 8.9Z"/></svg><svg class="ico-soleil" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.6v2M10 16.4v2M2.6 10h-2M19.4 10h-2M4.8 4.8 3.4 3.4M16.6 16.6l-1.4-1.4M15.2 4.8l1.4-1.4M3.4 16.6l1.4-1.4"/></svg></span></span></button>
<a href="/comparer-devis-ehpad/" class="tb-devis">Comparer vos devis</a>
<a href="/retours/" class="tb-avis">Vos retours</a>
<a href="/" class="tb-cta" data-ev="seo_topbar_to_calculator">Calculer<span class="tb-cta-plus">&nbsp;mon reste à charge</span></a>
</div>
</div>
<div class="tb-prog" aria-hidden="true"><i id="tb-prog"></i></div>
</div>"""

NAV = """<header class="top"><div class="top-in">
<a class="logo" href="/">Trouver mon <span>EHPAD</span><b class="tld">.fr</b></a>
<nav aria-label="Navigation principale">
<a href="/">Accueil</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix</a>
<a href="/aides-ehpad/">Aides</a>
<a href="/guides/">Guides</a>
</nav>
<button type="button" class="tb-icon tb-sw js-theme" role="switch" aria-checked="false" aria-label="Mode sombre" title="Mode sombre : activer ou désactiver"><span class="sw-txt" aria-hidden="true">Sombre</span><span class="sw-piste" aria-hidden="true"><span class="sw-pouce"><svg class="ico-lune" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5a7 7 0 1 0 8.9 8.9Z"/></svg><svg class="ico-soleil" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.6v2M10 16.4v2M2.6 10h-2M19.4 10h-2M4.8 4.8 3.4 3.4M16.6 16.6l-1.4-1.4M15.2 4.8l1.4-1.4M3.4 16.6l1.4-1.4"/></svg></span></span></button></div></header>"""

PIED = f"""<footer class="foot"><div class="foot-in">
{reassurance.bloc()}
<nav aria-label="Pied de page">
<a href="/">Accueil</a>
<a href="/ehpad/">Les EHPAD en France</a>
<a href="/prix-ehpad/">Prix des EHPAD</a>
<a href="/aides-ehpad/">Aides financières</a>
<a href="/guides/">Guides</a>
<a href="/professionnels/">Espace professionnel</a>
<a href="/lexique/">Lexique</a>
<a href="/notre-methodologie.html">Méthodologie</a>
<a href="/qui-sommes-nous.html">Qui sommes-nous ?</a>
<a href="/etudes/">Études et données</a>
<a href="/presse/">Presse</a>
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


def coupe_mot(t, n):
    """Coupe un texte à n caractères au plus, sur une frontière de mot, sans ponctuation pendante."""
    t = ' '.join(t.split())
    if len(t) <= n: return t
    c = t[:n + 1].rsplit(' ', 1)[0].rstrip(' ,;:–—-|(')
    # jamais de mot-outil orphelin en fin de titre (« … de la Vallée à »)
    while True:
        m = c.rsplit(' ', 1)
        if len(m) == 2 and m[1].lower() in {'à', 'au', 'aux', 'de', 'du', 'des', 'la', 'le', 'les', 'l’', 'd’', 'et', 'en', 'sur', ':'}:
            c = m[0].rstrip(' ,;:–—-|(')
        else:
            return c


def titre_court(options, n=60):
    """Premier titre de la liste qui tient en n caractères (marque ajoutée si la place le permet) ;
    à défaut, le dernier, coupé au mot. Google : des titres descriptifs, propres à la page, sans
    gabarit où seul un mot change."""
    for o in options:
        o = ' '.join(o.split())
        if len(o) <= n:
            return f'{o} | {MARQUE}' if len(o) + len(MARQUE) + 3 <= n else o
    return coupe_mot(options[-1], n)


def desc_courte(parties, n=155):
    """Assemble des morceaux de phrase propres à la page tant qu'ils tiennent en n caractères."""
    out = ''
    for x in parties:
        x = ' '.join(x.split())
        if not x: continue
        cand = (out + ' ' + x) if out else x
        if len(cand) <= n: out = cand
        elif not out: out = coupe_mot(x, n)
    return out


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


PERSONNE = {"@type": "Person", "@id": DOMAINE + "/#editeur", "name": AUTEUR,
            "url": DOMAINE + AUTEUR_URL, "description": AUTEUR_BIO,
            "jobTitle": "Éditeur de Trouver mon EHPAD"}


def jsonld_socle():
    return [
        {"@type": "WebSite", "@id": DOMAINE + "/#website", "url": DOMAINE + "/", "name": MARQUE,
         "alternateName": ["trouver-mon-ehpad.fr", "Trouver mon Ehpad"],
         "description": "Comprendre, comparer et estimer le coût réel des EHPAD en France.",
         "inLanguage": "fr-FR", "publisher": {"@id": DOMAINE + "/#organization"}},
        {"@type": "Organization", "@id": DOMAINE + "/#organization", "name": MARQUE,
         "url": DOMAINE + "/", "email": CONTACT,
         "logo": {"@type": "ImageObject", "url": DOMAINE + "/assets/logo-512.png", "width": 512, "height": 512},
         "founder": {"@id": DOMAINE + "/#editeur"},
         "areaServed": {"@type": "Country", "name": "France"}},
        PERSONNE,
    ]


def page(url, titre, description, corps, ariane, ld_extra=None, robots='index, follow',
         type_page='', lieu='', h1=None, maj=True):
    """Assemble une page complète. `url` commence et finit par « / » (ou pointe un fichier)."""
    # garde-fous : titre ≤ 60 caractères (la marque saute d'abord), description ≤ 158
    suffixe = f' | {MARQUE}'
    if len(titre) > 60 and titre.endswith(suffixe):
        titre = titre[:-len(suffixe)]
    if len(titre) > 60:
        titre = coupe_mot(titre, 60)
    description = coupe_mot(description, 158)
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
<link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
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
{MESURE}
</body>
</html>
"""
