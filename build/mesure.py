# -*- coding: utf-8 -*-
"""Relevé d'audience : l'adresse du service et l'extrait posé sur chaque page.

Un seul endroit pour les trois gabarits (accueil, pages annexes, pages de
contenu) : sans cela l'adresse finirait par diverger entre eux, et une partie
du site cesserait d'être mesurée sans que rien ne le signale.

L'extrait n'envoie que le chemin. Jamais la chaîne de requête ni l'ancre : les
liens de partage du calculateur y transportent la situation du visiteur.
"""

# Remplacer après « wrangler deploy » (voir worker-mesure/LISEZMOI.md).
API = 'https://mesure-tme.trouver-mon-ehpad.workers.dev'

ACTIF = 'VOTRE-SOUS-DOMAINE' not in API

# Posé en fin de corps, après le contenu : le relevé ne doit rien retarder.
# Enveloppé dans un try : une page ne doit jamais se casser pour un compteur.
#
# Trois filtres agissent ici, dans la page :
#  · B4 — rien n'est envoyé tant que la page est un PRÉ-RENDU (Chrome prépare
#    parfois une page « au cas où ») ou un onglet jamais affiché : une page que
#    personne n'a vue n'est pas une vue ;
#  · B1/B2 — un indicateur de navigateur automatisé, en masque de bits, pour que
#    le Worker range la vue parmi les suspects sans la jeter, et que l'on sache
#    quelle règle l'a signalée :
#      1 = navigator.webdriver (Selenium, Puppeteer, Playwright standard)
#      2 = « HeadlessChrome » dans l'agent utilisateur
#      4 = agent Chrome sans objet window.chrome, hors vues intégrées Android
#          (Facebook, WhatsApp, Instagram), qui n'exposent pas cet objet
#      8 = aucune langue déclarée
#  · B3 — deux évènements : « c » au chargement, « g » au premier geste humain
#    (défilement, clic, toucher, clavier, souris) ou après 10 secondes d'onglet
#    VISIBLE. L'écart entre les deux mesure les passages éclairs et les robots
#    qui chargent sans rien faire.
#
# Envoi par fetch(keepalive), PAS par sendBeacon : la liste EasyPrivacy (active
# par défaut dans uBlock Origin, Brave, AdGuard) contient « *$ping,third-party »,
# qui bloque TOUT sendBeacon vers un autre domaine — or le Worker est sur
# workers.dev. sendBeacon ne sert plus que de repli si fetch manque.
#
# Étapes du parcours (accueil seulement, depuis le 29/09/2026) : app.js appelle
# ME_etape('a' | 'cp' | 'r' | 'f') — arrivée, résultats affichés, budget calculé, fiche
# ouverte. Chaque étape part au plus une fois par chargement, avec d=1 si l'écran est
# tactile (pointer: coarse). Rien d'autre : ni montant, ni commune, ni réponse. Avant
# que la page soit réellement affichée (pré-rendu), les étapes attendent dans une file.
#
# Propriétaire du site : le lien #ne-pas-me-compter pose la marque « tme_proprio »
# dans CE navigateur (#ne-plus-m-exclure la retire). Les vues marquées partent
# avec m=1 et le Worker les range dans la colonne « Vous ». Chez un visiteur
# ordinaire rien n'est jamais écrit : la lecture renvoie simplement « rien ».
EXTRAIT = """<script>/* relevé d'audience : aucun cookie, aucun identifiant, chemin seul */
(function(){try{
var A='__API__',D=document,N=navigator,W=window,ua=N.userAgent||'';
var a=(N.webdriver?1:0)|(/HeadlessChrome/.test(ua)?2:0)
 |(/Chrome\\//.test(ua)&&!/; wv\\)|Version\\/\\d/.test(ua)&&!W.chrome?4:0)
 |(!N.languages||!N.languages.length?8:0);
var m=0;try{var S=W.localStorage,K='tme_proprio',H=location.hash,M='';
if(H==='#ne-pas-me-compter'){S.setItem(K,'1');M='Ce navigateur ne compte plus dans l\u2019audience : vos visites sont rang\u00e9es \u00e0 part, colonne \u00ab Vous \u00bb.';}
else if(H==='#ne-plus-m-exclure'){S.removeItem(K);M='Ce navigateur est de nouveau compt\u00e9 comme un visiteur ordinaire.';}
if(M){history.replaceState(null,'',location.pathname+location.search);
 var B=D.createElement('div');B.setAttribute('role','status');B.textContent=M;
 B.style.cssText='position:fixed;left:50%;bottom:1.2rem;transform:translateX(-50%);z-index:99999;max-width:min(34rem,calc(100% - 2rem));padding:.8rem 1.1rem;border-radius:12px;background:#0b6b4a;color:#fff;font:600 .95rem/1.4 system-ui,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.25)';
 D.body.appendChild(B);setTimeout(function(){B.remove();},7000);}
m=S.getItem(K)==='1'?1:0;}catch(e){}
var r=D.referrer||'',d='';
try{if(r){var h=new URL(r).hostname.replace(/^www\\./,'');if(h!==location.hostname.replace(/^www\\./,''))d=h;}}catch(e){}
function env(t,x){var q=A+'/v?t='+t+'&p='+encodeURIComponent(location.pathname)+'&a='+a+(m?'&m=1':'')+(x||'');
 if(W.fetch){try{fetch(q,{method:'POST',mode:'no-cors',keepalive:true,credentials:'omit'}).catch(function(){});return;}catch(e){}}
 try{if(N.sendBeacon)N.sendBeacon(q);}catch(e){}}
var ok=0,E={},Q=[],dv=W.matchMedia&&W.matchMedia('(pointer: coarse)').matches?1:0;
W.ME_etape=function(k){if(!/^(a|cp|r|f)$/.test(k)||E[k])return;E[k]=1;if(ok)env('e','&k='+k+'&d='+dv);else Q.push(k);};
var fait=0,vis=0,tic;
function engage(){if(fait)return;fait=1;clearInterval(tic);
 ['scroll','wheel','pointerdown','keydown','touchstart','mousemove'].forEach(function(k){W.removeEventListener(k,engage,true);});
 env('g');}
function part(){ok=1;
 env('c','&e='+((!r||d)?1:0)+(d?'&r='+encodeURIComponent(d):''));
 ['scroll','wheel','pointerdown','keydown','touchstart','mousemove'].forEach(function(k){W.addEventListener(k,engage,{capture:true,passive:true});});
 tic=setInterval(function(){if(D.visibilityState==='visible'&&++vis>=10)engage();},1000);
 while(Q.length)env('e','&k='+Q.shift()+'&d='+dv);}
function pret(){return !D.prerendering&&D.visibilityState==='visible';}
if(pret())part();else{var f=function(){if(!pret())return;
 D.removeEventListener('visibilitychange',f);D.removeEventListener('prerenderingchange',f);part();};
 D.addEventListener('visibilitychange',f);D.addEventListener('prerenderingchange',f);}
}catch(e){}})();</script>"""


def extrait():
    """L'extrait prêt à insérer, ou rien tant que le Worker n'est pas déployé."""
    return EXTRAIT.replace('__API__', API) if ACTIF else \
        '<!-- relevé d\'audience : en attente du déploiement du Worker de mesure -->'
