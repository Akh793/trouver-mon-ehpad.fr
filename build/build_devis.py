# -*- coding: utf-8 -*-
"""Génère /comparer-devis-ehpad/ : la grille de saisie et de comparaison des devis.

Aucun document n'est déposé, aucun fichier n'est lu, aucune IA n'intervient : la
famille recopie les lignes de ses devis, le calcul se fait dans le navigateur et
rien ne sort de l'appareil. C'est la contrepartie de la règle du site — les
calculs restent déterministes, explicables et exécutables par scripts.

La grille n'est pas inventée. Elle vient de trois sources normalisées :
  · le socle de prestations (annexe 2-3-1 du CASF, décret 2022-734) qui fixe la
    frontière entre ce qui est compris dans le tarif et ce qui est facturable ;
  · la liste fermée des prestations du formulaire de déclaration CNSA
    (PREST3 à PREST11, en « comprise » et en « en sus ») ;
  · quatre lignes relevées dans le champ libre réellement rempli par 408
    établissements, dont « repas invité » revient 209 fois.

Le régime de financement est déduit de l'établissement choisi, jamais des
tarifs : dans les 23 territoires de l'expérimentation, la grille GIR n'existe
plus et la page affiche une participation forfaitaire unique.
"""
import os

SITE = '../site'
SLUG = 'comparer-devis-ehpad'
FONT = open('fontface.css', encoding='utf-8').read()
CSS = open('site.css', encoding='utf-8').read()

# Les neuf prestations de la liste fermée CNSA encore collectées. Les deux
# premières de l'ancienne liste — entretien et marquage du linge — sont entrées
# dans le socle au 1er janvier 2023 : elles ne sont plus facturables à part, et
# les colonnes correspondantes sont vides chez tous les établissements.
PRESTATIONS = [
    ('hyg', 'Produits d’hygiène', 'Savon, gel douche, shampoing, dentifrice'),
    ('tel', 'Téléphone en chambre', 'Mise à disposition du poste'),
    ('ent', 'Appels reçus', 'Les appels entrants'),
    ('sor', 'Appels passés', 'Les appels sortants'),
    ('tv',  'Télévision en chambre', 'Mise à disposition du poste'),
    ('net', 'Internet, wifi', 'Abonnement ou accès au réseau'),
    ('coi', 'Coiffure', 'Shampoing, coupe'),
    ('est', 'Soins esthétiques', 'Prestations de base'),
    ('ped', 'Pédicure', 'Hors prescription médicale'),
]

SOCLE = [
    ('Le logement', 'La chambre, la salle de bain, l’eau, l’électricité, le chauffage, l’entretien et le ménage.'),
    ('Les repas', 'Trois repas, un goûter, et une collation disponible la nuit.'),
    ('Le linge', 'Draps et serviettes fournis et lavés — et depuis 2023, le marquage et le lavage du linge personnel.'),
    ('La vie sociale', 'Les animations de l’établissement et l’organisation des sorties.'),
    ('L’administratif', 'La préparation de l’entrée, le contrat, les courriers pour vos dossiers d’aides.'),
]


CORPS = r'''
<p class="lead">Vous avez reçu deux ou trois devis et vous n’arrivez pas à savoir lequel coûte
le moins cher&nbsp;? C’est normal&nbsp;: aucun modèle de devis n’est imposé aux EHPAD, chacun présente
ses prix à sa façon. Recopiez les lignes ici, on les remet dans le même ordre.</p>

<div class="dv-promesse">
  <div><b>Rien ne sort de votre appareil.</b><span>Aucun document à envoyer, aucun compte, aucun serveur. Le calcul se fait dans votre navigateur.</span></div>
  <div><b>7 champs suffisent.</b><span>Le reste est facultatif et affine la comparaison. Vous pouvez vous arrêter quand vous voulez.</span></div>
  <div><b>Rien n’est inventé.</b><span>Ce qui n’est pas écrit sur votre devis reste marqué « non indiqué », jamais compté comme zéro.</span></div>
</div>

<!-- ============ LES ONGLETS DE DEVIS ============ -->
<div class="dv-barre" role="tablist" aria-label="Vos devis">
  <div id="dv-onglets" class="dv-onglets"></div>
  <button type="button" id="dv-add" class="dv-add">+ Ajouter un devis</button>
</div>

<!-- ============ LE FORMULAIRE ============ -->
<form id="dv-form" novalidate>

<!-- ---------- Étape 1 ---------- -->
<section class="et" data-et="1">
  <h2><span class="n">1</span><span class="t">L’essentiel</span></h2>
  <p class="et-i">Les six lignes qui suffisent à comparer honnêtement. Tout est sur la première page de votre devis.</p>

  <div class="ch">
    <label for="dv-nom">Nom de l’établissement</label>
    <input id="dv-nom" type="text" autocomplete="off" placeholder="Résidence Les Tilleuls">
    <p class="ai">Pour vous y retrouver dans la comparaison.</p>
  </div>

  <div class="g2">
    <div class="ch">
      <label for="dv-cp">Code postal de l’établissement</label>
      <input id="dv-cp" type="text" inputmode="numeric" maxlength="5" autocomplete="off" placeholder="69003">
      <p class="ai" id="dv-cp-a">Sert à savoir quelles règles de dépendance s’appliquent chez lui.</p>
    </div>
    <div class="ch" id="dv-etab-ch" hidden>
      <label for="dv-etab">Lequel est-ce&nbsp;?</label>
      <select id="dv-etab"><option value="">Choisir dans la liste…</option></select>
      <p class="ai">Facultatif. Permet d’afficher ce que l’établissement a déclaré publiquement.</p>
    </div>
  </div>

  <div class="g2">
    <div class="ch">
      <label for="dv-date">Date du devis</label>
      <input id="dv-date" type="date">
      <p class="ai" id="dv-date-a">Les tarifs changent au 1<sup>er</sup> janvier.</p>
    </div>
    <div class="ch">
      <label>Type de séjour</label>
      <div class="seg" role="radiogroup" aria-label="Type de séjour">
        <button type="button" data-f="sejour" data-v="perm" role="radio" aria-checked="true" class="on">Définitif</button>
        <button type="button" data-f="sejour" data-v="temp" role="radio" aria-checked="false">Temporaire</button>
      </div>
      <p class="ai">Un séjour temporaire ne dépasse pas 90 jours par an.</p>
    </div>
  </div>

  <div class="ch">
    <label>Type de chambre</label>
    <div class="seg" role="radiogroup" aria-label="Type de chambre">
      <button type="button" data-f="chambre" data-v="cs" role="radio" aria-checked="true" class="on">Individuelle</button>
      <button type="button" data-f="chambre" data-v="cd" role="radio" aria-checked="false">Partagée</button>
    </div>
    <p class="ai">Une chambre partagée coûte 3 à 7&nbsp;€ de moins par jour. Comparer l’une à l’autre fausse tout.</p>
  </div>

  <div class="ch ch-gros">
    <label for="dv-heb">Prix de l’hébergement écrit sur le devis</label>
    <div class="mt">
      <label class="in-eur"><span class="sr">Montant</span>
        <input id="dv-heb" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
      <div class="seg seg-p" role="radiogroup" aria-label="Unité du prix">
        <button type="button" data-f="hebU" data-v="j" role="radio" aria-checked="true" class="on">par jour</button>
        <button type="button" data-f="hebU" data-v="m" role="radio" aria-checked="false">par mois</button>
      </div>
    </div>
    <p class="ai">Le montant tel qu’il est écrit, sans rien ajouter ni retrancher.</p>
  </div>

  <!-- LA question -->
  <div class="ch ch-cle">
    <div class="cle-h"><span class="cle-p" aria-hidden="true">?</span>
      <div><label id="lab-incl">Ce montant comprend-il déjà la dépendance&nbsp;?</label>
      <p class="ai">C’est la question qui fausse le plus les comparaisons. Certains devis affichent un
      «&nbsp;prix de journée&nbsp;» tout compris, d’autres mettent la dépendance sur une ligne à part.
      Entre les deux, l’écart atteint 200&nbsp;€ par mois — sans qu’aucun établissement soit plus cher.</p></div>
    </div>
    <div class="seg seg-v" role="radiogroup" aria-labelledby="lab-incl">
      <button type="button" data-f="incl" data-v="non" role="radio" aria-checked="false">
        <b>Non</b><span>La dépendance est sur une autre ligne</span></button>
      <button type="button" data-f="incl" data-v="oui" role="radio" aria-checked="false">
        <b>Oui</b><span>C’est un prix de journée tout compris</span></button>
      <button type="button" data-f="incl" data-v="nsp" role="radio" aria-checked="true" class="on">
        <b>Je ne sais pas</b><span>La page affichera une fourchette</span></button>
    </div>
  </div>

  <!-- dépendance, régime classique -->
  <div id="dv-dep-cl" class="ch-bloc">
    <div class="g2">
      <div class="ch">
        <label for="dv-gir">Tarif dépendance du GIR de la personne</label>
        <label class="in-eur"><span class="sr">Montant par jour</span>
          <input id="dv-gir" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai">Par jour. Sur le devis&nbsp;: «&nbsp;GIR 1-2&nbsp;», «&nbsp;GIR 3-4&nbsp;» ou «&nbsp;GIR 5-6&nbsp;».</p>
      </div>
      <div class="ch">
        <label for="dv-talon">Tarif «&nbsp;GIR 5-6&nbsp;»</label>
        <label class="in-eur"><span class="sr">Montant par jour</span>
          <input id="dv-talon" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai">Par jour. Il reste toujours à votre charge, quel que soit le GIR.
        Souvent appelé «&nbsp;ticket modérateur&nbsp;» ou «&nbsp;participation forfaitaire&nbsp;».</p>
      </div>
    </div>
  </div>

  <!-- dépendance, régime expérimental -->
  <div id="dv-dep-exp" class="ch-bloc" hidden>
    <div class="dv-note dv-note-bl">
      <b>Ici, la grille GIR n’existe plus.</b>
      Ce territoire fait partie des 23 où les financements soins et dépendance ont été fusionnés
      depuis le 1<sup>er</sup> juillet 2025. Tous les résidents paient la même somme par jour,
      quel que soit leur GIR et quelles que soient leurs ressources.
      Si votre devis affiche encore des tarifs GIR, signalez-le à l’établissement.
    </div>
    <div class="ch">
      <label for="dv-forf">Participation forfaitaire</label>
      <label class="in-eur"><span class="sr">Montant par jour</span>
        <input id="dv-forf" type="number" min="0" step="0.01" inputmode="decimal"></label>
      <p class="ai">Par jour. Pré-remplie au montant national 2026. Corrigez si votre devis diffère.</p>
    </div>
  </div>
</section>

<!-- ---------- Étape 2 ---------- -->
<details class="et et-d" data-et="2">
  <summary><h2><span class="n">2</span><span class="t">Ce qui est compris, ce qui est en plus</span></h2>
    <span class="et-c" id="dv-c2">0 sur 9 renseignées</span></summary>
  <div class="et-in">
    <p class="et-i">Neuf prestations, celles-là précisément&nbsp;: c’est la liste que l’État demande
    aux EHPAD de remplir chaque année. Laissez «&nbsp;non dit&nbsp;» si votre devis n’en parle pas —
    c’est une information en soi.</p>
    <div class="pr-grille">{PRESTATIONS}</div>

    <h3 class="so-t">Ce qui est obligatoirement compris, et ne doit jamais vous être facturé</h3>
    <div class="so-grille">{SOCLE}</div>
    <p class="ai so-a">C’est le «&nbsp;socle de prestations&nbsp;», fixé par décret. Si l’une de ces
    lignes apparaît en supplément sur votre devis, ce n’est pas normal.</p>

    <div class="g2 g2-h">
      <div class="ch"><label for="dv-repas">Repas d’un invité</label>
        <label class="in-eur"><span class="sr">Prix</span>
          <input id="dv-repas" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai">Par repas. La ligne hors liste la plus fréquente.</p></div>
      <div class="ch"><label for="dv-sup">Supplément de chambre</label>
        <label class="in-eur"><span class="sr">Prix par mois</span>
          <input id="dv-sup" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai">Par mois. Chambre «&nbsp;confort&nbsp;», «&nbsp;prestige&nbsp;», terrasse, surface.</p></div>
    </div>
  </div>
</details>

<!-- ---------- Étape 3 ---------- -->
<details class="et et-d" data-et="3">
  <summary><h2><span class="n">3</span><span class="t">Les clauses qui coûtent cher plus tard</span></h2>
    <span class="et-c" id="dv-c3">0 sur 3 renseignées</span></summary>
  <div class="et-in">
    <p class="et-i">Elles ne changent pas le prix affiché, mais elles changent la dépense de l’année.
    Cherchez-les dans les articles du contrat de séjour.</p>
    <div class="g2 g2-h">
      <div class="ch"><label for="dv-resa">Chambre réservée pendant une absence</label>
        <label class="in-eur"><span class="sr">Montant par jour</span>
          <input id="dv-resa" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai">Par jour. Ce que vous payez si la personne est hospitalisée ou part quelques jours.</p></div>
      <div class="ch"><label for="dv-caution">Dépôt de garantie</label>
        <label class="in-eur"><span class="sr">Montant</span>
          <input id="dv-caution" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
        <p class="ai" id="dv-caution-a">Versé une seule fois, rendu au départ.</p></div>
    </div>
    <div class="ch"><label for="dv-deces">Facturation après un décès</label>
      <div class="mt"><input id="dv-deces" type="number" min="0" max="60" step="1" inputmode="numeric" placeholder="0" class="in-jours">
        <span class="un">jours facturés</span></div>
      <p class="ai" id="dv-deces-a">La loi plafonne à 6 jours.</p></div>
  </div>
</details>
</form>

<!-- ============ LE RÉSULTAT ============ -->
<section id="dv-sortie">
  <h2><span class="n">4</span><span class="t">Ce que ça donne</span></h2>
  <div id="dv-vide" class="dv-vide">
    <p><b>Saisissez le prix d’hébergement d’au moins un devis</b> pour voir le total apparaître ici.</p>
  </div>
  <div id="dv-res" hidden></div>
  <div id="dv-alerte"></div>
</section>

<div class="dv-fin">
  <a class="btn" href="/">Estimer le reste à charge avec vos revenus</a>
  <button type="button" id="dv-print" class="btn-sec">Imprimer pour le rendez-vous</button>
  <button type="button" id="dv-raz" class="lien">Tout effacer</button>
</div>

<p class="f-src">Cette page ne reçoit aucun document et n’envoie rien&nbsp;: tout est calculé dans votre
navigateur, et votre saisie ne quitte pas votre appareil. Les montants affichés sont ceux que vous
recopiez&nbsp;; ils n’engagent que votre devis. Un devis est une proposition&nbsp;: le prix réellement dû
est celui du contrat de séjour, fixé à la signature. <a href="/notre-methodologie.html">Notre méthodologie</a>.</p>
'''

STYLE = r'''
/* ===== Comparer vos devis — styles propres à la page ===== */
/* #layout est un conteneur flex avec overflow-x:clip. Sans min-width:0, son
   enfant grandit jusqu'à la largeur de son contenu — ici le tableau comparatif,
   large de 34rem — et le débordement est CLIPPÉ au lieu de défiler : sur mobile
   la moitié droite de la page disparaissait sans qu'aucune barre n'apparaisse. */
.page,#layout main{max-width:min(72rem,100%);width:100%;margin-inline:auto;min-width:0}
.lead{font-size:1.05rem;color:var(--mut);max-width:76ch;margin-inline:auto;text-align:center}

/* --- les trois promesses, en tête --- */
.dv-promesse{margin:1.6rem auto 0;display:grid;gap:.9rem 1.4rem;
  grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.dv-promesse>div{background:var(--surf);border:1px solid var(--bd2);border-radius:var(--r2);
  padding:.9rem 1.1rem;box-shadow:0 4px 12px rgba(var(--om),.05)}
.dv-promesse b{display:block;font-family:Poppins,Inter,sans-serif;font-size:.95rem}
.dv-promesse span{display:block;margin-top:.25rem;font-size:.85rem;color:var(--mut);line-height:1.5}

/* --- barre d'onglets : un onglet par devis --- */
.dv-barre{position:sticky;top:0;z-index:30;margin-top:2.2rem;padding:.6rem 0;
  background:var(--pg);display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;
  border-bottom:1px solid var(--bd2)}
.dv-onglets{display:flex;gap:.4rem;flex-wrap:wrap;flex:1 1 auto;min-width:0}
.dv-o{display:inline-flex;align-items:center;gap:.5rem;border:1.5px solid var(--bd);
  background:var(--surf);color:var(--mut);border-radius:999px;padding:.45rem .5rem .45rem .95rem;
  font:inherit;font-size:.88rem;font-weight:600;cursor:pointer;
  transition:border-color .14s,color .14s,background .14s,box-shadow .14s}
.dv-o:hover{border-color:var(--bl-t);color:var(--bl-t)}
.dv-o[aria-selected="true"]{background:var(--ti-bl);border-color:var(--bl);color:var(--bl-t);
  box-shadow:0 2px 10px rgba(37,72,255,.14)}
.dv-o .t{font-variant-numeric:tabular-nums;font-weight:400;color:var(--mut2);font-size:.82rem}
.dv-o[aria-selected="true"] .t{color:var(--bl-t)}
.dv-x{border:0;background:none;color:var(--mut2);font:inherit;font-size:1rem;line-height:1;
  cursor:pointer;padding:.15rem .35rem;border-radius:999px}
.dv-x:hover{background:var(--ti-ro);color:var(--sur-ro)}
.dv-add{border:1.5px dashed var(--bd);background:none;color:var(--mut);border-radius:999px;
  padding:.45rem 1rem;font:inherit;font-size:.86rem;font-weight:600;cursor:pointer;
  transition:border-color .14s,color .14s}
.dv-add:hover{border-color:var(--bl-t);color:var(--bl-t)}
.dv-add[disabled]{opacity:.45;cursor:not-allowed}

/* --- les étapes --- */
.et{margin-top:2.4rem;background:var(--surf);border:1px solid var(--bd2);border-radius:var(--r);
  padding:1.6rem;box-shadow:0 4px 12px rgba(var(--om),.05)}
.et>h2,.et summary h2{margin:0}
.et-i{margin-top:.5rem;color:var(--mut);font-size:.92rem;max-width:78ch}
.et-d summary{list-style:none;cursor:pointer;display:flex;gap:1rem;align-items:center;
  justify-content:space-between;flex-wrap:wrap}
.et-d summary::-webkit-details-marker{display:none}
.et-d summary::after{content:"";width:.6rem;height:.6rem;flex:0 0 auto;margin-left:auto;
  border-right:2px solid var(--mut2);border-bottom:2px solid var(--mut2);
  transform:rotate(45deg);transition:transform .18s ease-out}
.et-d[open] summary::after{transform:rotate(-135deg)}
.et-c{font-size:.82rem;color:var(--mut2);font-variant-numeric:tabular-nums;
  background:var(--bg);border-radius:999px;padding:.2rem .7rem}
.et-in{margin-top:1.2rem}

/* --- champs --- */
.ch{margin-top:1.3rem;min-width:0}
.ch>label,.ch .cle-h label{display:block;font-size:.92rem;font-weight:600;color:var(--ink);margin-bottom:.4rem}
.ch input[type=text],.ch input[type=date],.ch input[type=number],.ch select{
  width:100%;border:1.5px solid var(--bd);border-radius:var(--r2);background:var(--surf);
  padding:.65rem .85rem;font:inherit;font-size:1rem;color:inherit}
.ch input:focus,.ch select:focus{outline:none;border-color:var(--bl-t);box-shadow:0 0 0 4px rgba(37,72,255,.14)}
.ai{margin-top:.4rem;font-size:.82rem;color:var(--mut);line-height:1.5}
.ai.warn{color:var(--sur-or)}
.ai.bad{color:var(--sur-ro);font-weight:600}
.g2{display:grid;gap:1rem 1.4rem;grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));align-items:start}
.g2-h{margin-top:1.3rem}
.g2 .ch{margin-top:0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.in-eur{position:relative;display:block}
.in-eur::after{content:"€";position:absolute;right:.85rem;top:50%;transform:translateY(-50%);
  color:var(--mut2);font-weight:600;pointer-events:none}
.in-eur input{padding-right:2rem!important}
.mt{display:flex;gap:.7rem;align-items:center;flex-wrap:wrap}
.mt .in-eur{flex:1 1 9rem}
.in-jours{max-width:7rem}
.un{font-size:.9rem;color:var(--mut)}
.ch-gros input{font-size:1.15rem;font-weight:600}
.ch-bloc{margin-top:1.3rem}

/* --- interrupteurs segmentés --- */
.seg{display:inline-flex;background:var(--bg);border:1px solid var(--bd2);border-radius:999px;padding:.2rem;gap:.15rem;flex-wrap:wrap}
.seg button{border:0;background:none;color:var(--mut);font:inherit;font-size:.85rem;font-weight:600;
  padding:.4rem .95rem;border-radius:999px;cursor:pointer;white-space:nowrap;flex:0 0 auto;
  transition:background .14s,color .14s,box-shadow .14s}
.seg button:hover{color:var(--ink)}
.seg button.on{background:var(--surf);color:var(--bl-t);box-shadow:0 1px 4px rgba(var(--om),.12)}
.seg button:focus-visible{outline:2px solid var(--bl-t);outline-offset:2px}
.seg-p{flex:0 0 auto}
/* la question décisive : trois grandes cartes, pas trois petites pastilles */
.ch-cle{background:var(--ti-bl2);border:1.5px solid var(--bd-bl);border-radius:var(--r2);padding:1.2rem}
.cle-h{display:flex;gap:.9rem;align-items:flex-start}
.cle-p{flex:0 0 auto;width:2rem;height:2rem;border-radius:999px;background:var(--bl);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-weight:700}
.seg-v{display:grid;gap:.6rem;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));
  background:none;border:0;padding:0;margin-top:1rem;width:100%}
.seg-v button{background:var(--surf);border:1.5px solid var(--bd);border-radius:var(--r2);
  padding:.8rem .9rem;text-align:left;display:block}
.seg-v button b{display:block;font-family:Poppins,Inter,sans-serif;font-size:.95rem;color:var(--ink)}
.seg-v button span{display:block;margin-top:.2rem;font-size:.8rem;color:var(--mut);font-weight:400;line-height:1.45}
.seg-v button.on{background:var(--ti-bl);border-color:var(--bl);box-shadow:0 4px 14px rgba(37,72,255,.16)}
.seg-v button.on b{color:var(--bl-t)}

/* --- prestations --- */
.pr-grille{margin-top:1.1rem;display:grid;gap:.7rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
/* Nom au-dessus, choix en dessous sur toute la largeur. Côte à côte, les trois
   libellés se tronquaient et le nom de la prestation passait sur trois lignes. */
.pr-l{background:var(--bg);border:1px solid var(--bd2);border-radius:var(--r2);padding:.8rem .9rem;
  display:grid;gap:.6rem;grid-template-columns:minmax(0,1fr);align-content:space-between;
  transition:border-color .14s,background .14s}
/* hauteur réservée au nom : sans elle, les interrupteurs des cartes voisines
   ne s'alignent pas dès qu'un libellé passe sur deux lignes. */
.pr-n{min-height:3.2em}
.pr-l:hover{border-color:var(--bd-bl2)}
.pr-l.set{background:var(--surf);border-color:var(--bd-bl2)}
.pr-n b{display:block;font-size:.92rem}
.pr-n span{display:block;font-size:.78rem;color:var(--mut2);margin-top:.1rem}
.pr-l .seg{width:100%;display:flex}
.pr-l .seg button{flex:1 1 0;padding:.4rem .5rem;font-size:.82rem;text-align:center}
.pr-l .seg button[data-v="sus"].on{color:var(--sur-or)}
.pr-l .seg button[data-v="incl"].on{color:var(--sur-ve)}
.pr-p{grid-column:1/-1;display:flex;gap:.6rem;align-items:center}
.pr-p .in-eur{flex:1 1 7rem}
.pr-p select{flex:0 0 auto;width:auto;border:1.5px solid var(--bd);border-radius:var(--r2);
  background:var(--surf);padding:.5rem 2rem .5rem .7rem;font:inherit;font-size:.85rem;color:inherit}

/* --- socle --- */
.so-t{margin-top:2rem;font-size:.98rem}
.so-grille{margin-top:.8rem;display:grid;gap:.6rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.so-l{background:var(--ti-ve);border:1px solid var(--bd2);border-radius:var(--r2);padding:.7rem .9rem}
.so-l b{display:block;font-size:.88rem;color:var(--sur-ve)}
.so-l span{display:block;margin-top:.2rem;font-size:.8rem;color:var(--txt2);line-height:1.5}
.so-a{margin-top:.7rem}

/* --- notes --- */
.dv-note{margin:0 0 1.1rem;border-radius:var(--r2);padding:.9rem 1.1rem;font-size:.88rem;line-height:1.55}
.dv-note b{display:block;font-family:Poppins,Inter,sans-serif;margin-bottom:.2rem}
.dv-note-bl{background:var(--ti-bl);color:var(--sur-bl)}
.dv-note-or{background:var(--ti-or);color:var(--sur-or)}
.dv-note-ro{background:var(--ti-ro);color:var(--sur-ro)}

/* --- sortie --- */
#dv-sortie{margin-top:2.4rem}
.dv-vide{margin-top:1rem;background:var(--bg);border:1px dashed var(--bd);border-radius:var(--r);
  padding:2.2rem 1.2rem;text-align:center;color:var(--mut)}
.dv-tot{margin-top:1.2rem;display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.dv-c{background:var(--surf);border:1px solid var(--bd2);border-radius:var(--r);padding:1.2rem;
  box-shadow:0 4px 12px rgba(var(--om),.05);transition:transform .16s ease-out,box-shadow .16s ease-out,border-color .16s}
@media (hover:hover){.dv-c:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(var(--om),.10)}}
.dv-c.min{border-color:var(--vert);box-shadow:0 0 0 2px rgba(15,138,95,.18),0 8px 20px rgba(var(--om),.08)}
.dv-c-h{display:flex;gap:.6rem;align-items:baseline;justify-content:space-between}
.dv-c-n{font-family:Poppins,Inter,sans-serif;font-weight:700;font-size:1rem;min-width:0;overflow-wrap:anywhere}
.dv-c-b{font-size:.72rem;font-weight:700;border-radius:999px;padding:.15rem .6rem;white-space:nowrap;
  background:var(--ti-ve);color:var(--sur-ve)}
.dv-m{margin-top:.6rem;font-family:Poppins,Inter,sans-serif;font-weight:700;
  font-size:clamp(1.6rem,4vw,2.1rem);line-height:1.1;font-variant-numeric:tabular-nums}
.dv-m small{display:block;font-size:.78rem;font-weight:600;color:var(--mut2);margin-top:.15rem}
.dv-d{margin-top:.5rem;font-size:.82rem;font-weight:600}
.dv-d.plus{color:var(--sur-ro)}
.dv-d.egal{color:var(--mut2)}
.dv-l{margin-top:.9rem;border-top:1px solid var(--bd2);padding-top:.7rem;display:grid;gap:.3rem;font-size:.85rem}
.dv-l div{display:flex;justify-content:space-between;gap:1rem}
.dv-l .k{color:var(--mut)}
.dv-l .v{font-variant-numeric:tabular-nums;white-space:nowrap}
.dv-l .v.nd{color:var(--mut2);font-style:italic}

/* --- tableau comparatif --- */
.dv-tab-w{margin-top:1.6rem;overflow-x:auto;min-width:0;max-width:100%}
.dv-tab{border-collapse:collapse;width:100%;min-width:34rem;font-size:.88rem}
.dv-tab th,.dv-tab td{padding:.55rem .8rem;border-bottom:1px solid var(--bd2);text-align:right;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.dv-tab th:first-child,.dv-tab td:first-child{text-align:left;white-space:normal;color:var(--mut)}
.dv-tab thead th{font-size:.82rem;color:var(--ink);border-bottom:2px solid var(--bd)}
.dv-tab tr.tot td{font-weight:700;border-top:2px solid var(--bd);border-bottom:0;font-size:.95rem}
.dv-tab td.nd{color:var(--mut2);font-style:italic;font-weight:400}
.dv-tab td.best{color:var(--sur-ve);font-weight:700}

.dv-fin{margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:center;justify-content:center}
.f-src{margin-top:2.4rem;max-width:78ch;margin-inline:auto}

@media (max-width:640px){
  .et{padding:1.1rem}
  .dv-barre{position:static}
}
@media print{
  .dv-barre,.dv-fin,.dv-promesse,#dv-vide,.et-d summary::after{display:none!important}
  .et-d[open] .et-in{display:block}
  .et{break-inside:avoid;box-shadow:none;border:1px solid #ddd}
}
'''

SCRIPT = r'''
(function () {
  'use strict';
  // Base de conversion : 365/12. Un mensuel « base 30 » et un mensuel « base 31 »
  // diffèrent de 3,3 % — un écart né du seul choix de la base, pas des tarifs.
  var JOURS = 365 / 12;
  var FORFAIT_2026 = 6.16;   // participation forfaitaire, territoires en fusion
  var MAX = 3;
  var CLES_PRESTA = ['hyg','tel','ent','sor','tv','net','coi','est','ped'];

  var $ = function (id) { return document.getElementById(id); };
  var eur = function (n) {
    return n.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' €';
  };
  var eur2 = function (n) {
    return n.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
  };
  var esc = function (t) {
    return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) {
      return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
  };
  var num = function (v) { var n = parseFloat(String(v).replace(',', '.')); return isFinite(n) && n >= 0 ? n : null; };

  function devisVide(i) {
    var d = { nom: '', cp: '', fin: '', reg: '', decl: null, declMaj: '',
              date: '', sejour: 'perm', chambre: 'cs',
              heb: null, hebU: 'j', incl: 'nsp', gir: null, talon: null, forf: null,
              repas: null, sup: null, resa: null, caution: null, deces: null, p: {} };
    CLES_PRESTA.forEach(function (k) { d.p[k] = { e: 'nd', v: null, u: 'm' }; });
    d.__n = i;
    return d;
  }

  var etat = { liste: [devisVide(1)], actif: 0 };

  /* ---------- Persistance : uniquement sur cet appareil, jamais ailleurs ---------- */
  var CLE = 'me_devis_v1';
  function sauve() {
    try { localStorage.setItem(CLE, JSON.stringify({ liste: etat.liste, actif: etat.actif })); } catch (e) {}
  }
  function relit() {
    try {
      var d = JSON.parse(localStorage.getItem(CLE) || 'null');
      if (d && Array.isArray(d.liste) && d.liste.length) {
        // On repart d'un devis vide et on recopie les clés connues : un ancien
        // format en mémoire ne doit pas casser la page.
        etat.liste = d.liste.slice(0, MAX).map(function (x, i) {
          var v = devisVide(i + 1);
          Object.keys(v).forEach(function (k) { if (k !== 'p' && x[k] !== undefined) v[k] = x[k]; });
          if (x.p) CLES_PRESTA.forEach(function (k) { if (x.p[k]) v.p[k] = x.p[k]; });
          return v;
        });
        etat.actif = Math.min(d.actif || 0, etat.liste.length - 1);
      }
    } catch (e) {}
  }

  /* ---------- Régime de financement : déduit du territoire, jamais des tarifs ---------- */
  var depsCharges = {};
  function depsPourCp(cp) {
    var p = String(cp || '');
    if (p.indexOf('97') === 0 || p.indexOf('98') === 0) return [p.slice(0, 3)];
    if (p.indexOf('20') === 0) return ['2A', '2B'];
    return [p.slice(0, 2)];
  }
  function chargeDep(dep, apres) {
    if (depsCharges[dep]) { apres(depsCharges[dep]); return; }
    var s = document.createElement('script');
    s.src = '/data/dep/ehpad-' + dep + '.js';
    s.onload = function () { apres(depsCharges[dep] || []); };
    s.onerror = function () { depsCharges[dep] = []; apres([]); };
    document.head.appendChild(s);
  }
  // Les fichiers appellent ME.dep(code, lignes).
  window.ME = window.ME || {};
  window.ME.dep = function (code, lignes) { depsCharges[code] = lignes || []; };
  // Colonnes utiles du format compact (voir contrat_donnees.json).
  var C = { fin: 0, nom: 1, cp: 2, ville: 3, p: 6, t56: 11, maj: 12, reg: 45 };

  /* ---------- Calcul ---------- */
  function parJour(v, u) { return v == null ? null : (u === 'm' ? v / JOURS : v); }
  function parMois(v, u) { return v == null ? null : (u === 'm' ? v : v * JOURS); }

  function calcule(d) {
    var r = { heb: null, dep: null, sus: 0, susNd: 0, total: null, incertain: false, manque: [] };
    var hebJ = parJour(d.heb, d.hebU);
    if (hebJ == null) { r.manque.push('le prix de l’hébergement'); return r; }

    var exp = d.reg === 'exp';
    var depJ = exp ? (d.forf != null ? d.forf : FORFAIT_2026)
                   : (d.talon != null ? d.talon : null);

    if (d.incl === 'oui') {
      // Le devis annonce un prix tout compris : la dépendance est déjà dedans.
      r.heb = hebJ * JOURS;
      r.dep = 0;
      r.inclus = true;
    } else if (d.incl === 'non') {
      r.heb = hebJ * JOURS;
      r.dep = depJ != null ? depJ * JOURS : null;
      if (depJ == null) r.manque.push('le tarif GIR 5-6');
    } else {
      // « Je ne sais pas » : on calcule les deux bornes plutôt que d'en choisir une.
      r.heb = hebJ * JOURS;
      r.dep = depJ != null ? depJ * JOURS : null;
      r.incertain = true;
      if (depJ == null) r.manque.push('le tarif GIR 5-6');
    }

    CLES_PRESTA.forEach(function (k) {
      var p = d.p[k];
      if (p.e !== 'sus') return;
      if (p.v == null) { r.susNd++; return; }
      r.sus += (p.u === 'j') ? p.v * JOURS : (p.u === 'm' ? p.v : 0); // « à l'unité » : non mensualisable
    });
    if (d.sup != null) r.sus += d.sup;

    var base = r.heb + (r.dep || 0) + r.sus;
    r.total = base;
    if (r.incertain && r.dep) { r.bas = r.heb + r.sus; r.haut = base; }
    return r;
  }

  /* ---------- Rendu des onglets ---------- */
  function rendOnglets() {
    var h = etat.liste.map(function (d, i) {
      var c = calcule(d);
      var t = c.total != null ? eur(Math.round(c.total)) : 'à remplir';
      return '<button type="button" class="dv-o" role="tab" data-i="' + i + '"'
        + ' aria-selected="' + (i === etat.actif) + '">'
        + '<span>' + esc(d.nom || ('Devis ' + (i + 1))) + '</span>'
        + '<span class="t">' + t + '</span>'
        + (etat.liste.length > 1 ? '<span class="dv-x" role="button" tabindex="0" data-sup="' + i + '" aria-label="Retirer ce devis">×</span>' : '')
        + '</button>';
    }).join('');
    $('dv-onglets').innerHTML = h;
    $('dv-add').disabled = etat.liste.length >= MAX;
  }

  /* ---------- Rendu du formulaire depuis l'état ---------- */
  function segChoisi(root, champ, val) {
    root.querySelectorAll('[data-f="' + champ + '"]').forEach(function (b) {
      var on = b.getAttribute('data-v') === val;
      b.classList.toggle('on', on);
      b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
  }

  function rendForm() {
    var d = etat.liste[etat.actif];
    $('dv-nom').value = d.nom; $('dv-cp').value = d.cp; $('dv-date').value = d.date;
    $('dv-heb').value = d.heb == null ? '' : d.heb;
    $('dv-gir').value = d.gir == null ? '' : d.gir;
    $('dv-talon').value = d.talon == null ? '' : d.talon;
    $('dv-forf').value = d.forf == null ? FORFAIT_2026 : d.forf;
    $('dv-repas').value = d.repas == null ? '' : d.repas;
    $('dv-sup').value = d.sup == null ? '' : d.sup;
    $('dv-resa').value = d.resa == null ? '' : d.resa;
    $('dv-caution').value = d.caution == null ? '' : d.caution;
    $('dv-deces').value = d.deces == null ? '' : d.deces;
    var f = $('dv-form');
    segChoisi(f, 'sejour', d.sejour); segChoisi(f, 'chambre', d.chambre);
    segChoisi(f, 'hebU', d.hebU); segChoisi(f, 'incl', d.incl);

    CLES_PRESTA.forEach(function (k) {
      var l = f.querySelector('.pr-l[data-p="' + k + '"]');
      var p = d.p[k];
      l.querySelectorAll('.seg button').forEach(function (b) {
        var on = b.getAttribute('data-v') === p.e;
        b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false');
      });
      l.classList.toggle('set', p.e !== 'nd');
      l.querySelector('.pr-p').hidden = p.e !== 'sus';
      l.querySelector('.pr-p input').value = p.v == null ? '' : p.v;
      l.querySelector('.pr-p select').value = p.u;
    });

    var exp = d.reg === 'exp';
    $('dv-dep-cl').hidden = exp;
    $('dv-dep-exp').hidden = !exp;
    majCompteurs(d);
    majAides(d);
  }

  function majCompteurs(d) {
    var n2 = CLES_PRESTA.filter(function (k) { return d.p[k].e !== 'nd'; }).length;
    $('dv-c2').textContent = n2 + ' sur 9 renseignées';
    var n3 = ['resa', 'caution', 'deces'].filter(function (k) { return d[k] != null; }).length;
    $('dv-c3').textContent = n3 + ' sur 3 renseignées';
  }

  // Aides contextuelles qui réagissent à la saisie : elles disent ce qui cloche
  // au moment où ça cloche, pas dans un message d'erreur à la fin.
  function majAides(d) {
    var a = $('dv-date-a'), an = new Date().getFullYear();
    if (d.date) {
      var y = +d.date.slice(0, 4);
      if (y < an) { a.className = 'ai warn';
        a.innerHTML = 'Ce devis date de ' + y + '. Les tarifs ont été revalorisés au 1<sup>er</sup> janvier : demandez-en un à jour.'; }
      else { a.className = 'ai'; a.innerHTML = 'Les tarifs changent au 1<sup>er</sup> janvier.'; }
    } else { a.className = 'ai'; a.innerHTML = 'Les tarifs changent au 1<sup>er</sup> janvier.'; }

    var c = $('dv-caution-a');
    var hebM = parMois(d.heb, d.hebU);
    if (d.caution != null && hebM && d.caution > hebM * 1.02) {
      c.className = 'ai bad';
      c.textContent = 'Ce montant dépasse un mois d’hébergement (' + eur(Math.round(hebM))
        + '). La loi plafonne le dépôt de garantie à un mois : à faire corriger.';
    } else { c.className = 'ai'; c.textContent = 'Versé une seule fois, rendu au départ.'; }

    var de = $('dv-deces-a');
    if (d.deces != null && d.deces > 6) {
      de.className = 'ai bad';
      de.textContent = d.deces + ' jours dépassent le plafond légal de 6 jours. À faire corriger.';
    } else { de.className = 'ai'; de.textContent = 'La loi plafonne à 6 jours.'; }
  }

  /* ---------- Recherche de l'établissement ---------- */
  function majEtab(d) {
    var deps = d.cp.length === 5 ? depsPourCp(d.cp) : [];
    if (!deps.length) { $('dv-etab-ch').hidden = true; d.reg = ''; d.fin = ''; d.decl = null; rendForm(); return; }
    var restants = deps.length, trouves = [];
    deps.forEach(function (dep) {
      chargeDep(dep, function (lignes) {
        trouves = trouves.concat((lignes || []).filter(function (l) { return String(l[C.cp]) === d.cp; }));
        if (--restants) return;
        var sel = $('dv-etab');
        if (!trouves.length) {
          $('dv-etab-ch').hidden = true;
          $('dv-cp-a').className = 'ai';
          $('dv-cp-a').textContent = 'Aucun établissement connu à ce code postal. La comparaison reste possible.';
          d.reg = ''; rendForm(); majSortie(); return;
        }
        trouves.sort(function (a, b) { return String(a[C.nom]).localeCompare(String(b[C.nom]), 'fr'); });
        sel.innerHTML = '<option value="">Choisir dans la liste…</option>'
          + trouves.map(function (l) {
              return '<option value="' + esc(l[C.fin]) + '">' + esc(l[C.nom]) + '</option>'; }).join('');
        sel.value = d.fin || '';
        $('dv-etab-ch').hidden = false;
        // Le régime vaut pour le territoire : on le prend dès qu'on a des
        // établissements à ce code postal, même sans en avoir choisi un.
        appliqueEtab(d, trouves, d.fin);
      });
    });
  }

  function appliqueEtab(d, lignes, fin) {
    var l = fin ? lignes.filter(function (x) { return String(x[C.fin]) === String(fin); })[0] : null;
    var ref = l || lignes[0];
    d.reg = ref ? String(ref[C.reg] || '') : '';
    if (l) { d.fin = String(l[C.fin]); d.decl = l[C.p]; d.declMaj = String(l[C.maj] || '');
             if (d.talon == null && l[C.t56] != null) d.talon = l[C.t56]; }
    else { d.fin = ''; d.decl = null; d.declMaj = ''; }
    var a = $('dv-cp-a');
    if (d.reg === 'exp') { a.className = 'ai'; a.innerHTML = 'Territoire où les financements soins et dépendance sont fusionnés&nbsp;: la grille GIR n’y existe plus.'; }
    else if (d.reg) { a.className = 'ai'; a.textContent = 'Régime de droit commun : tarif dépendance selon le GIR.'; }
    rendForm(); majSortie(); sauve();
  }

  /* ---------- Sortie ---------- */
  function ligne(k, v, nd) {
    return '<div><span class="k">' + k + '</span><span class="v' + (nd ? ' nd' : '') + '">' + v + '</span></div>';
  }

  function majSortie() {
    var res = etat.liste.map(calcule);
    var utiles = res.filter(function (r) { return r.total != null; });
    $('dv-vide').hidden = utiles.length > 0;
    $('dv-res').hidden = utiles.length === 0;
    if (!utiles.length) { $('dv-alerte').innerHTML = ''; rendOnglets(); return; }

    var mini = Math.min.apply(null, utiles.map(function (r) { return r.total; }));

    var cartes = etat.liste.map(function (d, i) {
      var r = res[i];
      if (r.total == null) {
        return '<div class="dv-c"><div class="dv-c-h"><span class="dv-c-n">'
          + esc(d.nom || ('Devis ' + (i + 1))) + '</span></div>'
          + '<p class="ai" style="margin-top:.8rem">Il manque ' + r.manque.join(' et ') + '.</p></div>';
      }
      var best = r.total === mini && utiles.length > 1;
      var ec = r.total - mini;
      var diff = utiles.length < 2 ? ''
        : (best ? '<p class="dv-d">Le moins cher des devis saisis</p>'
                : '<p class="dv-d plus">+ ' + eur(Math.round(ec)) + ' par mois, soit ' + eur(Math.round(ec * 12)) + ' sur un an</p>');
      var det = ligne('Hébergement', eur2(r.heb))
        + (r.inclus ? ligne('Dépendance', 'comprise dans le prix')
                    : ligne('Dépendance à charge', r.dep == null ? 'non indiquée' : eur2(r.dep), r.dep == null))
        + ligne('Prestations en plus', r.sus ? eur2(r.sus) : (r.susNd ? r.susNd + ' sans prix' : 'aucune déclarée'), !r.sus);
      return '<div class="dv-c' + (best ? ' min' : '') + '">'
        + '<div class="dv-c-h"><span class="dv-c-n">' + esc(d.nom || ('Devis ' + (i + 1))) + '</span>'
        + (best ? '<span class="dv-c-b">le moins cher</span>' : '') + '</div>'
        + '<p class="dv-m">' + eur(Math.round(r.total)) + '<small>par mois, tout compris, avant les aides</small></p>'
        + diff + '<div class="dv-l">' + det + '</div></div>';
    }).join('');

    var lignesTab = [
      ['Hébergement', function (r) { return r.heb; }],
      ['Dépendance à charge', function (r) { return r.inclus ? 0 : r.dep; }],
      ['Prestations en plus', function (r) { return r.sus || 0; },
                              function (r) { return r.sus > 0 || r.susNd > 0; }]
    ];
    var tete = '<tr><th>Poste, par mois</th>' + etat.liste.map(function (d, i) {
      return '<th>' + esc(d.nom || ('Devis ' + (i + 1))) + '</th>'; }).join('') + '</tr>';
    var corps = lignesTab.map(function (L) {
      var vals = res.map(L[1]);
      var dispo = vals.filter(function (v) { return v != null; });
      // Un montant n'est « le moins cher » que s'il est plus bas qu'un autre :
      // surligner en vert des valeurs toutes égales — deux zéros, notamment —
      // ferait passer une absence de déclaration pour un avantage.
      var mn = (dispo.length > 1 && Math.min.apply(null, dispo) < Math.max.apply(null, dispo))
             ? Math.min.apply(null, dispo) : null;
      return '<tr><td>' + L[0] + '</td>' + vals.map(function (v, i) {
        if (v == null) return '<td class="nd">non indiqué</td>';
        if (L[2] && !v && !L[2](res[i])) return '<td class="nd">aucune</td>';
        return '<td' + (mn != null && v === mn ? ' class="best"' : '') + '>' + eur2(v) + '</td>';
      }).join('') + '</tr>';
    }).join('');
    var totaux = '<tr class="tot"><td>Total mensuel</td>' + res.map(function (r) {
      if (r.total == null) return '<td class="nd">—</td>';
      return '<td' + (r.total === mini && utiles.length > 1 ? ' class="best"' : '') + '>' + eur(Math.round(r.total)) + '</td>';
    }).join('') + '</tr>';

    $('dv-res').innerHTML = '<div class="dv-tot">' + cartes + '</div>'
      + '<div class="dv-tab-w"><table class="dv-tab"><thead>' + tete + '</thead><tbody>'
      + corps + totaux + '</tbody></table></div>';

    $('dv-alerte').innerHTML = alertes(res);
    rendOnglets();
  }

  // Ce qui empêche de comparer ces devis-là. Affiché au même niveau que le
  // résultat : un écart entre deux périmètres différents n'est pas un écart de prix.
  function alertes(res) {
    var L = etat.liste, out = [];
    var remplis = L.filter(function (d, i) { return res[i].total != null; });
    if (remplis.length < 2) return '';

    if (L.some(function (d, i) { return res[i].total != null && d.incl === 'nsp'; })) {
      out.push(['or', 'Une réponse manque sur la dépendance',
        'Pour au moins un devis, vous n’avez pas indiqué si le prix comprenait déjà la dépendance. '
        + 'Tant que ce n’est pas tranché, le total peut être surestimé de l’équivalent du tarif GIR 5-6 — '
        + 'de l’ordre de 180 à 200 € par mois.']);
    }
    var regs = {}; remplis.forEach(function (d) { regs[d.reg || 'inconnu'] = 1; });
    if (regs.exp && (regs.classique || regs.inconnu)) {
      out.push(['bl', 'Ces devis ne relèvent pas des mêmes règles',
        'L’un est dans un territoire où soins et dépendance sont fusionnés — participation forfaitaire '
        + 'identique pour tous — et l’autre dans le régime de droit commun, où la dépendance dépend du GIR '
        + 'et des ressources. Les totaux se comparent, pas les lignes de dépendance.']);
    }
    var sej = {}; remplis.forEach(function (d) { sej[d.sejour] = 1; });
    if (sej.perm && sej.temp) {
      out.push(['ro', 'Un séjour définitif face à un séjour temporaire',
        'Les barèmes d’aide ne sont pas les mêmes et l’aide sociale à l’hébergement est souvent refusée '
        + 'en temporaire. Ces deux devis ne répondent pas au même besoin.']);
    }
    var ch = {}; remplis.forEach(function (d) { ch[d.chambre] = 1; });
    if (ch.cs && ch.cd) {
      out.push(['or', 'Une chambre individuelle face à une chambre partagée',
        'L’écart mesuré entre les deux est de 3 à 7 € par jour. Il vient du type de chambre, pas de l’établissement.']);
    }
    var ds = remplis.map(function (d) { return d.date; }).filter(Boolean);
    if (ds.length > 1) {
      var t = ds.map(function (x) { return +new Date(x); });
      if ((Math.max.apply(null, t) - Math.min.apply(null, t)) > 92 * 864e5) {
        out.push(['or', 'Plus de trois mois séparent ces devis',
          'Les tarifs sont revalorisés au 1er janvier, et le prix d’un nouvel entrant est fixé à la signature '
          + 'du contrat. Demandez des devis de la même période.']);
      }
    }
    if (!out.length) {
      out.push(['bl', 'Ces devis sont comparables',
        'Même type de séjour, même type de chambre, mêmes règles de dépendance, dates proches. '
        + 'L’écart affiché est un vrai écart de prix.']);
    }
    return out.map(function (a) {
      return '<div class="dv-note dv-note-' + a[0] + '" style="margin-top:1rem"><b>' + a[1] + '</b>' + a[2] + '</div>';
    }).join('');
  }

  /* ---------- Écoutes ---------- */
  function lie(id, champ, entier) {
    var el = $(id);
    if (!el) return;
    el.addEventListener('input', function () {
      var d = etat.liste[etat.actif];
      d[champ] = el.value === '' ? null : (entier ? Math.round(num(el.value)) : num(el.value));
      majAides(d); majCompteurs(d); majSortie(); sauve();
    });
  }

  function init() {
    relit();

    $('dv-nom').addEventListener('input', function () {
      etat.liste[etat.actif].nom = this.value.slice(0, 60); rendOnglets(); majSortie(); sauve();
    });
    $('dv-date').addEventListener('input', function () {
      var d = etat.liste[etat.actif]; d.date = this.value; majAides(d); sauve();
    });
    $('dv-cp').addEventListener('input', function () {
      var v = this.value.replace(/\D/g, '').slice(0, 5); this.value = v;
      var d = etat.liste[etat.actif]; d.cp = v; d.fin = ''; majEtab(d); sauve();
    });
    $('dv-etab').addEventListener('change', function () {
      var d = etat.liste[etat.actif], deps = depsPourCp(d.cp), tous = [];
      deps.forEach(function (dep) { tous = tous.concat(depsCharges[dep] || []); });
      appliqueEtab(d, tous.filter(function (l) { return String(l[C.cp]) === d.cp; }), this.value);
    });

    ['heb','gir','talon','forf','repas','sup','resa','caution'].forEach(function (k) { lie('dv-' + k, k); });
    lie('dv-deces', 'deces', true);

    // interrupteurs segmentés du formulaire
    $('dv-form').addEventListener('click', function (e) {
      var b = e.target.closest('.seg button'); if (!b) return;
      var d = etat.liste[etat.actif];
      var l = b.closest('.pr-l');
      if (l) {
        var k = l.getAttribute('data-p');
        d.p[k].e = b.getAttribute('data-v');
        if (d.p[k].e !== 'sus') d.p[k].v = null;
        rendForm(); majSortie(); sauve();
        if (d.p[k].e === 'sus') l.querySelector('.pr-p input').focus();
        return;
      }
      var f = b.getAttribute('data-f'); if (!f) return;
      d[f] = b.getAttribute('data-v');
      rendForm(); majSortie(); sauve();
    });
    // prix et unité d'une prestation en sus
    $('dv-form').addEventListener('input', function (e) {
      var l = e.target.closest('.pr-l'); if (!l) return;
      var d = etat.liste[etat.actif], k = l.getAttribute('data-p');
      if (e.target.tagName === 'INPUT') d.p[k].v = e.target.value === '' ? null : num(e.target.value);
      majSortie(); sauve();
    });
    $('dv-form').addEventListener('change', function (e) {
      var l = e.target.closest('.pr-l'); if (!l || e.target.tagName !== 'SELECT') return;
      etat.liste[etat.actif].p[l.getAttribute('data-p')].u = e.target.value;
      majSortie(); sauve();
    });

    // onglets
    $('dv-onglets').addEventListener('click', function (e) {
      var x = e.target.closest('[data-sup]');
      if (x) {
        e.stopPropagation();
        var j = +x.getAttribute('data-sup');
        etat.liste.splice(j, 1);
        if (!etat.liste.length) etat.liste = [devisVide(1)];
        etat.actif = Math.min(etat.actif, etat.liste.length - 1);
        rendOnglets(); rendForm(); majEtab(etat.liste[etat.actif]); majSortie(); sauve();
        return;
      }
      var o = e.target.closest('.dv-o'); if (!o) return;
      etat.actif = +o.getAttribute('data-i');
      rendOnglets(); rendForm(); majEtab(etat.liste[etat.actif]); majSortie(); sauve();
      window.scrollTo({ top: $('dv-form').offsetTop - 80, behavior: 'smooth' });
    });
    $('dv-add').addEventListener('click', function () {
      if (etat.liste.length >= MAX) return;
      etat.liste.push(devisVide(etat.liste.length + 1));
      etat.actif = etat.liste.length - 1;
      rendOnglets(); rendForm(); majSortie(); sauve();
      $('dv-nom').focus();
    });

    $('dv-print').addEventListener('click', function () {
      document.querySelectorAll('.et-d').forEach(function (d) { d.open = true; });
      window.print();
    });
    $('dv-raz').addEventListener('click', function () {
      etat.liste = [devisVide(1)]; etat.actif = 0;
      try { localStorage.removeItem(CLE); } catch (e) {}
      rendOnglets(); rendForm(); $('dv-etab-ch').hidden = true; majSortie();
    });

    rendOnglets(); rendForm(); majSortie();
    if (etat.liste[etat.actif].cp) majEtab(etat.liste[etat.actif]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
'''


def carte_prestation(cle, nom, aide):
    return f'''<div class="pr-l" data-p="{cle}">
  <div class="pr-n"><b>{nom}</b><span>{aide}</span></div>
  <div class="seg seg-3" role="radiogroup" aria-label="{nom}">
    <button type="button" data-v="incl" role="radio" aria-checked="false">Incluse</button>
    <button type="button" data-v="sus" role="radio" aria-checked="false">En plus</button>
    <button type="button" data-v="nd" role="radio" aria-checked="true" class="on">Non dit</button>
  </div>
  <div class="pr-p" hidden>
    <label class="in-eur"><span class="sr">Prix de {nom}</span>
      <input type="number" min="0" step="0.01" inputmode="decimal" placeholder="0"></label>
    <select aria-label="Unité"><option value="m">par mois</option><option value="j">par jour</option><option value="u">à l’unité</option></select>
  </div>
</div>'''


def main():
    import build_pages as bp
    import mesure

    prest_html = '\n'.join(carte_prestation(*p) for p in PRESTATIONS)
    socle_html = '\n'.join(
        f'<div class="so-l"><b>{t}</b><span>{d}</span></div>' for t, d in SOCLE)

    corps = (CORPS
             .replace('{PRESTATIONS}', prest_html)
             .replace('{SOCLE}', socle_html)
             + '<style>' + STYLE + '</style>\n<script>' + SCRIPT + '</script>')

    html = bp.HEAD.format(
        title='Comparer vos devis d’EHPAD, poste par poste | Trouver mon EHPAD',
        desc='Recopiez les lignes de vos devis d’EHPAD : le coût mensuel réel, tout compris, '
             'et ce que chaque établissement inclut ou facture en plus. Gratuit, sans inscription, '
             'rien n’est envoyé.',
        slug=SLUG + '/', robots='index, follow', h1='Comparer vos devis',
        body=corps, font=FONT, css=CSS,
        jsonld=bp.crumb('Comparer vos devis', SLUG + '/'),
        mesure=bp.MESURE)

    os.makedirs(os.path.join(SITE, SLUG), exist_ok=True)
    open(os.path.join(SITE, SLUG, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'page /{SLUG}/ écrite :', len(html.encode()), 'octets ;',
          len(PRESTATIONS), 'prestations de la liste CNSA')


if __name__ == '__main__':
    main()
