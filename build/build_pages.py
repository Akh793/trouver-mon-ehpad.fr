# -*- coding: utf-8 -*-
"""Génère les pages annexes : même gabarit, CSS inliné, aucun JS hors bandeau de consentement."""
import os
import mesure
SITE = '../site'
FONT = open('fontface.css', encoding='utf-8').read()
CSS = open('site.css', encoding='utf-8').read()
MESURE = mesure.extrait()

HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>/* Thème : appliqué avant le premier rendu, sinon la page clignote en blanc. */
(function(){{try{{var k='mon_ehpad_theme',t=localStorage.getItem(k);
if(t!=='dark'&&t!=='light')t=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';
if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}}catch(e){{}}}})();</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://trouver-mon-ehpad.fr/{slug}">
<meta name="robots" content="{robots}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://trouver-mon-ehpad.fr/{slug}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Trouver mon EHPAD">
<meta property="og:image" content="https://trouver-mon-ehpad.fr/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://trouver-mon-ehpad.fr/assets/og-image.png">
<meta name="theme-color" content="#2548FF">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
{jsonld}
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div id="topbar" class="topbar print-hide">
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
<a href="/" class="tb-cta">Calculer<span class="tb-cta-plus">&nbsp;mon reste à charge</span></a>
</div>
</div>
<div class="tb-prog" aria-hidden="true"><i id="tb-prog"></i></div>
</div>
<div id="layout">
<header>
  <div class="head-act"><button type="button" class="tb-icon tb-sw js-theme" role="switch" aria-checked="false" aria-label="Mode sombre" title="Mode sombre : activer ou désactiver"><span class="sw-txt" aria-hidden="true">Sombre</span><span class="sw-piste" aria-hidden="true"><span class="sw-pouce"><svg class="ico-lune" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5a7 7 0 1 0 8.9 8.9Z"/></svg><svg class="ico-soleil" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.6v2M10 16.4v2M2.6 10h-2M19.4 10h-2M4.8 4.8 3.4 3.4M16.6 16.6l-1.4-1.4M15.2 4.8l1.4-1.4M3.4 16.6l1.4-1.4"/></svg></span></span></button></div>
  <p class="fil"><a href="/">Accueil</a> › {h1}</p>
  <h1 style="font-size:clamp(1.8rem,4vw,2.8rem);margin-top:.6rem">{h1}</h1>
</header>
<section class="page">
{body}
</section>
<footer id="site-footer">
  <nav aria-label="Pied de page">
    <a href="/">Accueil</a>
    <a href="/ehpad/">Les EHPAD en France</a>
    <a href="/prix-ehpad/">Prix des EHPAD</a>
    <a href="/aides-ehpad/">Aides financières</a>
    <a href="/guides/">Guides</a>
    <a href="/lexique/">Lexique</a>
    <a href="/notre-methodologie.html">Notre méthodologie</a>
    <a href="/qui-sommes-nous.html">Qui sommes-nous ?</a>
    <a href="/mentions-legales.html">Mentions légales</a>
    <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Mon%20EHPAD%20%E2%80%94%20contact">Nous écrire</a>
  </nav>
  <p>© 2026 Trouver mon EHPAD — gratuit, sans publicité, sans partenariat avec des établissements.</p>
</footer>
</div>
<script src="/assets/pages.js" defer></script>
{mesure}
</body>
</html>
"""

def crumb(name, slug):
    return ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList",'
            '"itemListElement":[{"@type":"ListItem","position":1,"name":"Accueil","item":"https://trouver-mon-ehpad.fr/"},'
            '{"@type":"ListItem","position":2,"name":"%s","item":"https://trouver-mon-ehpad.fr/%s"}]}</script>' % (name, slug))

PAGES = [
{
 'file': 'notre-methodologie.html', 'slug': 'notre-methodologie.html',
 'title': 'Méthodologie : comment le reste à charge est calculé',
 'desc': "Sources croisées, formule de l'APA en établissement, règles de l'aide sociale, méthode de l'évolution des prix : ce qui est vérifié, déduit ou refusé.",
 'robots': 'index, follow', 'h1': 'Notre méthodologie',
 'body': """
<p>Ce site affiche de l’argent que des familles vont réellement dépenser. Il n’a donc le droit ni d’arrondir une règle, ni de combler un trou de données par une valeur vraisemblable. Cette page dit exactement d’où vient chaque chiffre, ce qui est vérifié, ce qui est déduit, et ce que nous ne calculons pas. <b>Version 2.0, vérifiée le 11 septembre 2026.</b></p>

<h2>1. Trois niveaux de fiabilité, affichés partout</h2>
<ul>
<li><b>✅ vérifié</b> — la donnée vient d’une base publique ou d’un texte officiel, avec sa date : prix CNSA, note d’évaluation de la Haute Autorité de santé, inspection Alim’confiance, seuils de l’APA, mode de fixation tarifaire FINESS.</li>
<li><b>⚠️ déduit</b> — la donnée est reconstruite à partir d’une autre, selon une règle écrite ci-dessous : statut juridique déduit du code FINESS, position géographique recalculée par géocodage, taux d’occupation repris du segment auquel l’établissement appartient.</li>
<li><b>❌ non trouvé</b> — la donnée n’existe pas publiquement. Nous l’écrivons au lieu de la remplacer : places réellement disponibles dans tel établissement, barème de l’obligation alimentaire, taux d’encadrement par établissement, capacité à jour.</li>
</ul>

<h2>2. La chaîne de croisement</h2>
<p>Le pivot est le numéro FINESS géographique de l’établissement. Il relie l’identité et l’adresse (FINESS+ Structures, Agence du numérique en santé), les places installées et les unités spécialisées (FINESS+ Activités), les documents de contrôle publiés par l’ARS quand ils portent ce numéro, les prix et tarifs dépendance (CNSA), la note d’évaluation (Haute Autorité de santé). Le SIRET relie les inspections d’hygiène (Alim’confiance), complété par un rapprochement SIREN + commune lorsque le SIRET diffère. Le code commune INSEE relie enfin la grille de densité et le recensement de la population (INSEE), les indicateurs départementaux (DREES) et la pratique départementale de l’aide sociale à l’hébergement.</p>
<p>Périmètre au 29 septembre 2026 : <b>7 415 EHPAD ouverts</b> selon le répertoire FINESS+. Parmi eux, 5 791 déclarent un prix à la CNSA, 4 813 ont une évaluation publiée par la HAS, 1 011 sont appariés à une inspection d’hygiène, 7 255 ont un historique de prix exploitable, 7 350 ont une capacité connue. Les établissements sans prix déclaré <b>restent affichés</b>, avec la mention « prix non déclaré » : les masquer reviendrait à récompenser l’opacité. 67 établissements sans coordonnées connues n’apparaissent pas sur la carte.</p>

<h2>3. Le calcul du reste à charge, ligne par ligne</h2>
<p>Les prix CNSA sont journaliers. Nous les multiplions par <b>30,5 jours</b>, moyenne d’un mois, et nous l’affichons — la CNSA communique parfois sur 30 jours, l’écart est d’environ 1,7 %.</p>
<ol>
<li><b>Hébergement</b> = prix journalier de la chambre (seule ou double, au choix) × 30,5, multiplié par deux si les deux membres du couple sont hébergés.</li>
<li><b>Dépendance</b> = tarif journalier du GIR retenu × 30,5, également doublé le cas échéant.</li>
<li><b>APA en établissement</b> — formule recopiée du code source d’OpenFisca-France (variable <code>apa_etablissement</code>), pas de mémoire, puis <b>vérifiée à 0,00 € près contre l’API de calcul officielle sur cinq cas</b>. Le résident paie au minimum le tarif GIR 5-6. Jusqu’à <b>2 869,55 €</b> de ressources mensuelles, il ne paie que ce tarif. Entre 2 869,55 € et <b>4 414,70 €</b>, sa participation augmente linéairement, avec une pente de 80 %. Au-delà, elle est plafonnée au tarif GIR 5-6 augmenté de 80 % de l’écart avec son propre tarif. En couple, les ressources du ménage sont divisées par deux. L’APA n’est pas versée si son montant est inférieur à trois fois le Smic horaire brut. Ces seuils dérivent de la majoration pour tierce personne, 1 298,44 € depuis le 1<sup>er</sup> avril 2026 (2,21 et 3,40 fois ce montant). Le 29/09/2026, le portail officiel des personnes âgées et OpenFisca affichaient encore les seuils calculés sur la valeur 2025 (2 846,77 € et 4 379,64 €)&nbsp;: nous appliquons la valeur en vigueur.</li>
<li><b>Ressources prises en compte</b> — retraites et pensions, plus les « autres revenus » saisis séparément (loyers perçus, rentes, revenus de placements). Le département les intègre dans l’assiette de l’aide sociale, et ils entrent dans l’assiette de l’APA. Les séparer permet de voir ce qu’ils changent.</li>
<li><b>Aide au logement</b> — non simulée. Elle dépend du conventionnement de l’établissement, information absente des données ouvertes. Le champ prévu permet de saisir le montant déjà notifié par la CAF ou la MSA ; à défaut, il vaut zéro et le reste à charge affiché est donc <i>prudent</i>, c’est-à-dire plutôt majoré.</li>
<li><b>Réduction d’impôt</b> — 25 % des frais d’hébergement et de dépendance restant à charge, dans la limite de 10 000 € de dépenses <b>par an et par personne hébergée</b> — deux plafonds quand les deux conjoints sont en établissement —, soit 2 500 € au maximum par personne, et seulement si le parent est imposable. Nous affichons « jusqu’à » : le montant exact dépend de son impôt.</li>
</ol>
<p><b>Couleur du point sur la carte</b> : verte si le reste à charge tient dans les ressources du parent, une fois mis de côté le minimum que l’aide sociale lui laisserait (10 % de ses ressources, jamais moins de 125 €) ; orange si l’épargne saisie couvre le trou pendant plus de cinq ans ; rouge sinon — c’est le signal que l’aide sociale ou la famille devront intervenir.</p>

<h2>4. Ce qui est déduit, et par quelle règle</h2>
<h3>Habilitation à l’aide sociale — trois états, plus deux</h3>
<p>La version 1 déduisait l’habilitation du tarif « aide sociale » déclaré à la CNSA, et la surestimait de 270 établissements. La version 2 part du <b>libellé officiel du mode de fixation tarifaire</b> publié dans FINESS, qui dit explicitement « habilité aide sociale » ou « non habilité aide sociale » : les codes 40, 41, 44, 45, 50 et 56 correspondent à une habilitation, les codes 42, 43, 46, 47, 51 et 55 à une absence d’habilitation. Résultat : <b>6 081 habilités, 1 142 non habilités</b>, et <b>194 « à confirmer »</b> — les établissements que FINESS dit non habilités mais qui déclarent malgré tout un tarif « aide sociale » à la CNSA, ce qui correspond le plus souvent à une habilitation partielle, sur un nombre limité de lits. La fiche le dit et invite à poser la question à l’établissement. Vingt-neuf établissements sans libellé FINESS gardent la déduction de la version 1, étiquetée comme telle.</p>
<h3>Statut juridique</h3>
<p>Le statut en clair vient du fichier CNSA 2020 ou de la HAS. Pour les 806 établissements absents des deux, il est déduit du code de statut juridique FINESS de la personne morale gestionnaire, par une table construite sur les établissements où le code et le statut en clair coexistent, et retenue seulement pour les codes dont la concordance dépasse 95 % sur au moins 10 établissements. Huit établissements restent sans statut : la fiche l’indique.</p>
<h3>Position sur la carte</h3>
<p>5 330 établissements ont des coordonnées dans FINESS. 1 910 ont été géocodés avec la Base adresse nationale, 110 repris de la HAS. Pour 151 d’entre eux, le géocodage n’a atteint que la commune : la fiche affiche alors « position approximative : centre de la commune ».</p>
<h3>Qualité : ce que publie la HAS</h3>
<p>La note d’évaluation A à D, la date, l’organisme évaluateur (choisi et rémunéré par l’établissement — nous le précisons), la moyenne des objectifs sur 100 et les quatre cotations de chapitre viennent du jeu « Résultats des évaluations ESSMS ». La version 1 affichait un indicateur non documenté ; la version 2 affiche <b>le nombre de critères impératifs atteints sur 18</b>, variable documentée dans le dictionnaire du jeu de données.</p>
<h3>Prestations incluses ou facturées en sus</h3>
<p>Le fichier CNSA contient onze indicateurs de prestations incluses et onze de prestations facturées en sus, mais le dictionnaire des variables (version 26, février 2026) ne dit pas à quelle prestation correspond chaque indicateur. Nous affichons donc <b>leur nombre</b>, jamais un libellé inventé, ainsi que le prix du linge et les textes libres saisis par l’établissement quand ils existent.</p>

<h2>5. L’évolution du prix de la chambre</h2>
<p>Les fichiers annuels de prix de la CNSA sont archivés depuis 2018. En les fusionnant sur le numéro FINESS, on obtient pour <b>7 255 établissements</b> une série du prix journalier d’une chambre seule, de 2018 à 2025, et pour chacun l’évolution totale, l’évolution annualisée et la courbe affichée sur sa fiche. Un établissement qui n’a pas déclaré une année laisse un trou : la courbe ne le relie pas, et l’évolution est calculée entre la première et la dernière année réellement déclarées, toutes deux affichées.</p>
<p>La référence de comparaison est l’indice des prix à la consommation de l’INSEE (ensemble des ménages, moyenne annuelle), soit <b>+17,2 % de 2018 à 2025</b>. Le prix médian d’une chambre seule est passé de 60,22 € à 73,41 € par jour, soit +20,5 % pour les établissements présents aux deux dates : <b>65 % des établissements ont augmenté plus vite que le coût de la vie</b>, et environ 2,5 % ont baissé leur prix. Le détail par année figure sur la page d’accueil. Nous affichons l’écart à l’inflation, jamais un jugement sur l’établissement : une hausse peut financer une rénovation ou du personnel supplémentaire.</p>

<h2>6. Les places disponibles</h2>
<p><b>Aucune base publique ne publie les places réellement disponibles.</b> ViaTrajectoire détient l’information et la réserve aux professionnels ; le tableau de bord de la performance médico-sociale n’est pas ouvert. Le répertoire FINESS+ donne, depuis septembre 2026, les places <b>installées</b> de chaque établissement (hébergement permanent, unité protégée Alzheimer, hébergement temporaire, accueil de jour)&nbsp;: une place installée n’est pas une place libre.</p>
<p>Nous n’affichons donc aucune estimation de places libres&nbsp;: une moyenne ne dit rien d’un établissement un jour donné. Le taux d’occupation moyen des EHPAD de même statut et de même densité de commune (enquête EHPA 2023 de la DREES) reste affiché comme un repère sectoriel, présenté comme tel. Le délai réel d’entrée est documenté au niveau national par la DREES : <b>55 % des personnes entrées en 2023 ont attendu un mois ou moins</b> après le dépôt du dossier.</p>

<h2>7. L’aide sociale à l’hébergement, l’obligation alimentaire et la famille</h2>
<p>Règles nationales appliquées : le résident conserve au moins 10 % de ses ressources et jamais moins de 125 € par mois ; le conjoint resté à domicile conserve au moins 1 043,59 € par mois ; l’aide versée est récupérable sur la succession, sur les donations consenties dans les dix ans précédant la demande <b>comme après elle</b>, et en cas de retour à meilleure fortune ; les sommes versées par les enfants au titre de l’obligation alimentaire ne le sont pas. Depuis la <b>loi du 8 avril 2024</b>, les petits-enfants ne sont plus sollicités au titre de l’obligation alimentaire lorsqu’une aide sociale à l’hébergement est demandée pour leurs grands-parents.</p>
<p>Ce qui relève du département est affiché comme tel : recours sur succession, personnes sollicitées au titre de l’obligation alimentaire, prise en charge du GIR 5-6, charges déductibles. Ces informations viennent de l’enquête Aide sociale de la DREES et portent sur <b>2018</b> — c’est la donnée la plus récente publiée. Nous les présentons comme « pratique déclarée en 2018 », jamais comme la règle d’aujourd’hui : le règlement départemental d’aide sociale en vigueur fait foi. Dans le Rhône, la Métropole de Lyon exerce les compétences départementales : le site distingue les deux, commune par commune. En Corse, la collectivité unique remplace les deux départements.</p>
<p><b>Nous n’affichons aucun montant imposé d’obligation alimentaire</b> : il n’existe aucun barème national. Le conseil départemental, et à défaut le juge aux affaires familiales, fixe la part de chaque enfant. La seule référence chiffrée publiée est la participation moyenne constatée par la DREES, 270 € par mois fin 2023, sur environ 115 900 bénéficiaires de l’ASH dont un tiers a au moins un obligé alimentaire.</p>
<p>Le bloc « si les enfants complètent » répond à une question que les simulateurs ignorent : <i>combien chacun</i>. Il divise à <b>parts égales</b> ce que les ressources du parent ne couvrent pas — hypothèse de travail, affichée comme telle, car le département tient compte des revenus de chacun — puis applique la déduction fiscale : la pension alimentaire versée à un ascendant dans le besoin est déductible du revenu imposable <b>sans plafond</b>, sur justificatifs, y compris lorsqu’elle est versée directement à l’établissement. Le coût réel dépend donc de la tranche marginale d’imposition de chaque enfant, que vous choisissez. Le parent doit déclarer la somme reçue.</p>

<h2>8. Ce que ce site ne fera pas</h2>
<ul>
<li>Afficher un nombre de places libres dans tel établissement, ou un délai d’attente individuel : ces données ne sont publiées nulle part. Ce que nous affichons est un taux de segment et un rythme de rotation, présentés comme tels.</li>
<li>Recopier le taux d’encadrement, l’absentéisme ou la rotation du personnel affichés depuis août 2026 sur le portail officiel : ils ne sont pas en données ouvertes, nous ne pourrions ni les dater ni les mettre à jour. Chaque fiche renvoie vers la fiche officielle.</li>
<li>Calculer l’impôt du parent ou de ses enfants : nous demandons la tranche, nous ne la devinons pas à partir de données que le site ne collecte pas.</li>
<li>Publier des avis de familles : modérer des avis portant sur des établissements accueillant des personnes vulnérables demande des moyens qu’un site gratuit n’a pas.</li>
<li>Vendre quoi que ce soit, ni orienter vers des établissements partenaires. L’article L. 554-2 du code de la sécurité sociale interdit de facturer l’aide à l’obtention d’une prestation sociale ; et un modèle rémunéré par les établissements orienterait mécaniquement vers le privé commercial — l’inverse de ce que fait la carte de l’habilitation à l’aide sociale.</li>
</ul>

<h2>9. Les pages par territoire et par établissement</h2>
<p>Chaque région, chaque département, chaque commune d’au moins deux établissements et chaque établissement documenté ont leur page. Les chiffres qui y figurent sont recalculés à chaque mise à jour des données, jamais saisis à la main.</p>
<ul>
<li><b>Le tarif médian</b> est la médiane des tarifs journaliers d’hébergement en chambre seule déclarés à la CNSA, multipliée par 30,5 jours. Nous retenons la médiane et non la moyenne : quelques établissements très chers déforment la moyenne. Le nombre d’établissements sur lequel porte le calcul est toujours affiché.</li>
<li><b>Les comparaisons</b> (« X % moins cher que la médiane de la ville ») ne sont écrites que si la médiane de référence repose sur au moins trois établissements. Sinon, la comparaison est faite au niveau du département.</li>
<li><b>Les quartiles</b> ne sont affichés qu’à partir de cinq établissements, l’évolution des prix qu’à partir de cinq séries complètes.</li>
<li><b>Une commune d’un seul établissement n’a pas de page</b> : elle ferait doublon avec la fiche de l’établissement. L’adresse redirige vers cette fiche.</li>
<li><b>Un établissement sans tarif déclaré ni évaluation publiée n’a pas de fiche</b> : il n’y aurait rien à y lire. Il reste visible dans le calculateur et dans les listes, avec la mention « prix non déclaré ».</li>
<li><b>Aucun classement « meilleur EHPAD »</b> n’est publié : aucune donnée publique ne permet de le fonder. Les seuls classements du site portent sur le tarif déclaré, et le critère est écrit en toutes lettres.</li>
</ul>

<h2>10. Mise à jour</h2>
<p>Le fichier de prix de la CNSA est annoncé mensuel ; au 11 septembre 2026, le dernier disponible portait sur janvier 2026. Chaque fiche affiche la date de mise à jour déclarée par l’établissement lui-même : la date est une donnée, pas un défaut, et une déclaration de plus de douze mois est signalée. Les évaluations de la HAS sont régénérées quotidiennement, les inspections Alim’confiance également. Les règles nationales (APA, réduction d’impôt, ASH, obligation alimentaire) ont été vérifiées le 11 septembre 2026.</p>
<p>Un chiffre vous paraît faux ? <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Correction">Écrivez-nous</a> avec le numéro FINESS : une correction documentée est traitée en priorité.</p>
"""},
{
 'file': 'qui-sommes-nous.html', 'slug': 'qui-sommes-nous.html',
 'title': 'Qui sommes-nous ? | Trouver mon EHPAD',
 'desc': "Un outil gratuit, sans publicité et sans partenariat avec des établissements, pour répondre à la seule question que les familles se posent : qui paie quoi.",
 'robots': 'index, follow', 'h1': 'Qui sommes-nous ?',
 'body': """
<p>Trouver mon EHPAD est un outil indépendant, gratuit et sans publicité. Il répond à une question précise, que ni les annuaires ni le portail officiel ne traitent complètement : <b>combien votre parent paiera réellement dans tel établissement, et qui paiera le reste</b>.</p>

<h2 id="editeur">Qui l’édite</h2>
<p><b>David Rival</b>, éditeur et directeur de la publication. Juriste de formation (master 2 en droit des affaires), il conçoit des outils numériques et a construit ce site seul, sans financement ni partenariat, à partir des données publiques. Il est responsable de chaque page publiée, y compris des fiches d’établissement produites automatiquement.</p>
<p>Son rôle : choisir les sources, valider les règles de calcul et les guides, les confronter aux sources officielles (la formule de l’allocation personnalisée d’autonomie est contrôlée à 0,00 € près contre OpenFisca, le moteur de calcul socio-fiscal ouvert de l’État) et corriger les erreurs signalées. Ce qu’il ne fait pas : visiter les établissements. Chaque règle renvoie à sa source officielle, pour que vous puissiez la vérifier.</p>

<h2>Pourquoi ce site</h2>
<p>Trouver un EHPAD n’est pas le problème : les annuaires existent, et le portail officiel de la CNSA en est un bon. Comprendre la facture, si. Le prix affiché est un prix « à partir de », hors aides. Entre ce prix et ce que la famille paie, il y a l’APA, l’aide au logement, la réduction d’impôt, parfois l’aide sociale à l’hébergement, l’obligation alimentaire des enfants et le recours sur succession. Personne ne pose cet enchaînement sur une carte, à hauteur d’une famille donnée. C’est tout ce que fait ce site.</p>

<h2>Comment il est financé</h2>
<p>Il ne l’est pas. Pas d’abonnement, pas de mise en relation payante, aucun partenariat avec des établissements. Les plateformes d’orientation qui existent sont, de leur propre aveu, rémunérées par les résidences partenaires : ce modèle oriente structurellement vers le privé commercial, alors qu’un tiers des questions de financement se règle dans des établissements habilités à l’aide sociale, majoritairement publics et associatifs. Facturer une famille pour l’aider à obtenir l’APA ou l’ASH est par ailleurs interdit (article L. 554-2 du code de la sécurité sociale).</p>

<h2>Ce que nous ne savons pas</h2>
<p>Beaucoup de choses, et elles sont écrites en toutes lettres sur la page d’accueil et dans <a href="/notre-methodologie.html">la méthodologie</a> : les places réellement libres dans tel établissement, le délai que vous attendrez, le montant exact de l’aide au logement, la part que votre département demandera aux enfants. Ces informations ne sont pas publiées. Nous préférons le dire, et donner à la place des moyennes officielles clairement étiquetées comme telles, plutôt que d’afficher un chiffre plausible.</p>

<h2>Vos données</h2>
<p>Le calcul s’exécute dans votre navigateur. Les ressources, l’épargne et le niveau de dépendance de votre parent ne sont ni transmis ni enregistrés sur un serveur ; ils sont seulement conservés sur votre appareil pour que vous retrouviez votre saisie, et le bouton « Effacer mes réponses » les supprime. Le site ne demande ni nom, ni adresse, ni téléphone, et ne crée aucun compte.</p>

<h2>Ce que ce site n’est pas</h2>
<p>Trouver mon EHPAD n’est <b>pas un service public</b> et n’a aucun lien avec une administration, un conseil départemental ou un établissement. C’est un service indépendant, qui réutilise des données publiques et cite leur source à chaque fois. Les décisions officielles — niveau de perte d’autonomie, allocation personnalisée d’autonomie, aide sociale à l’hébergement — relèvent du conseil départemental, et seules ses notifications font foi.</p>
<p>Le site ne vend rien, ne met en relation avec aucun établissement et ne transmet aucune information à des tiers. Il n’affiche ni avis de familles, ni classement « meilleur EHPAD » : aucune donnée publique ne permettrait de les fonder honnêtement.</p>

<h2>Signaler une erreur</h2>
<p>Un tarif qui a changé, une adresse fausse, une habilitation mal reprise : écrivez-nous avec le numéro FINESS de l’établissement, indiqué en bas de chaque fiche. Une correction documentée est traitée en priorité, et la date de dernière vérification figure sur chaque page.</p>

<h2>Nous écrire</h2>
<p>Une erreur, une donnée qui a changé, un établissement dont le prix n’a pas été mis à jour : <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Mon%20EHPAD">contact@trouver-mon-ehpad.fr</a>. Indiquez le numéro FINESS de l’établissement, il figure en bas de chaque fiche.</p>
"""},
{
 'file': 'mentions-legales.html', 'slug': 'mentions-legales.html',
 'title': 'Mentions légales et données personnelles | Trouver mon EHPAD',
 'desc': "Éditeur, hébergeur, licences des données publiques réutilisées, traitement des données personnelles et mesure d'audience.",
 'robots': 'noindex, follow', 'h1': 'Mentions légales',
 'body': """
<h2>Éditeur</h2>
<p>Trouver mon EHPAD est un site édité à titre personnel, sans but lucratif.</p>
<ul>
<li><b>Éditeur et directeur de la publication</b> : David RIVAL</li>
<li><b>Adresse</b> : non publiée — éditeur non professionnel, identité complète communiquée à l’hébergeur</li>
<li><b>Contact</b> : <a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a></li>
</ul>
<p class="fil">Ces trois mentions sont exigées par l’article 6 III de la loi pour la confiance dans l’économie numérique. Un éditeur non professionnel peut ne rendre publics que son nom et son adresse de courrier électronique, à condition d’avoir communiqué son identité complète à l’hébergeur.</p>

<h2>Hébergeur</h2>
<p>Le site est hébergé par <b>GitHub, Inc.</b>, 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis — <a href="https://docs.github.com/fr/pages" target="_blank" rel="noopener">GitHub Pages</a>.</p>
<p>Les pages sont des fichiers statiques : l’hébergeur ne reçoit ni formulaire, ni compte, ni base de données. Les journaux de connexion éventuellement conservés par l’hébergeur relèvent de sa propre politique.</p>

<h2>Données publiques réutilisées</h2>
<p>Ce site réutilise des données publiques : prix et tarifs des EHPAD (CNSA), FINESS+ Structures et FINESS+ Activités (Agence du numérique en santé), résultats d’évaluation des ESSMS (Haute Autorité de santé), Alim’confiance (Direction générale de l’alimentation), indicateurs sociaux départementaux, enquête Aide sociale et enquête EHPA (DREES), grille de densité des communes et recensement de la population 2023 (INSEE), archives annuelles des prix des EHPAD 2018-2025 (CNSA), découpage administratif et Base adresse nationale, fond de plan de la Géoplateforme (IGN), paramètres socio-fiscaux d’OpenFisca-France. Chaque jeu de données est distribué sous sa propre licence, indiquée sur sa fiche de publication ; la Base adresse nationale et les fonds cartographiques de l’IGN ont leurs propres conditions de réutilisation et d’attribution.</p>
<p>Licences relevées sur les fiches de publication : Licence Ouverte 2.0 (Etalab) pour FINESS, la Haute Autorité de santé, la DREES et la Base adresse nationale ; Licence Ouverte pour Alim’confiance et la grille de densité de l’INSEE ; le catalogue Melodi de l’INSEE indique un accès « public » pour le recensement, sans nommer de licence. Les documents de contrôle des ARS ne sont pas repris : le site renvoie vers leur page de publication. <b>Le jeu de données le plus central du site — les prix et tarifs des EHPAD publiés par la CNSA — ne déclare aucune licence</b> sur data.gouv.fr : nous l’écrivons plutôt que de le supposer, et une demande de précision a été adressée à la CNSA.</p>
<p>Le fond de plan provient de la Géoplateforme de l’Institut national de l’information géographique et forestière et porte sa mention d’attribution sur la carte elle-même. Les données cartographiques sont affichées selon les conditions générales d’utilisation de la Géoplateforme.</p>

<h2 id="photos">Photos des établissements</h2>
<p>La vignette de chaque établissement, dans la liste des résultats, provient d’une de ces trois sources, citée sur l’image même&nbsp;:</p>
<ul>
<li><b>Wikimedia Commons</b>&nbsp;: photos reliées à l’établissement par son numéro FINESS dans Wikidata, sous licence libre (Creative Commons BY-SA, BY ou CC0). L’auteur et la licence figurent sur l’image&nbsp;; la liste complète, avec le lien vers chaque fichier, est sur la <a href="/credits-photos.html">page des crédits photo</a>.</li>
<li><b>Panoramax</b>&nbsp;: photos prises depuis la voie publique, sous Licence Ouverte 2.0 ou CC BY-SA 4.0, recadrées dans la direction de l’établissement. Une photo recadrée d’origine CC BY-SA reste sous CC BY-SA 4.0. Chaque photo a été vérifiée à l’œil avant publication.</li>
<li><b>IGN</b>&nbsp;: à défaut de photo, vue aérienne centrée sur l’adresse (BD ORTHO, Licence Ouverte 2.0). C’est une vue du quartier, pas une photo de l’établissement.</li>
</ul>
<p>Aucune image Google n’est utilisée. Un gestionnaire peut envoyer une photo de sa façade dont il détient les droits à <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Photo%20de%20l%E2%80%99%C3%A9tablissement">contact@trouver-mon-ehpad.fr</a>&nbsp;: elle remplacera la vignette. Pour faire retirer une photo, même adresse.</p>

<h2>Propriété intellectuelle</h2>
<p>Les textes, les calculs et la mise en forme de ce site sont l’œuvre de son éditeur. Les données réutilisées appartiennent à leurs producteurs, cités ci-dessus et sur chaque page. Les chiffres agrégés publiés par le site (tarifs médians, baromètre) peuvent être repris librement avec la mention « Données : Trouver mon EHPAD, à partir des tarifs déclarés à la CNSA ».</p>

<h2>Absence de valeur officielle</h2>
<p>Les montants affichés sont des estimations calculées à partir de données publiques et de règles nationales. Ils ne constituent ni une décision, ni un devis, ni un conseil juridique ou fiscal. Le groupe iso-ressources (GIR), l’allocation personnalisée d’autonomie et l’aide sociale à l’hébergement sont notifiés par le conseil départemental ; l’aide au logement par la CAF ou la MSA ; la réduction d’impôt par l’administration fiscale. Seules leurs décisions font foi. Le prix effectivement facturé est celui du contrat de séjour.</p>

<h2 id="donnees">Données personnelles</h2>
<p>Le calculateur fonctionne intégralement dans votre navigateur. Les informations saisies — code postal, niveau de dépendance, ressources, épargne, statut de propriétaire, aide au logement — ne sont transmises à aucun serveur. Elles sont conservées localement sur votre appareil (stockage du navigateur) afin de retrouver votre saisie d’une visite à l’autre, et supprimées par le bouton « Effacer mes réponses ». Aucun compte, aucun nom, aucune adresse, aucun numéro de téléphone n’est demandé. Le site ne réalise aucune mise en relation commerciale et ne transmet rien à des établissements.</p>

<h2 id="cookies">Mesure d’audience et cookies</h2>
<p>Ce site ne dépose aucun cookie de mesure : aucun consentement n’est donc demandé. Pour savoir quelles pages servent, chaque page signale sa consultation à un compteur hébergé chez Cloudflare. Il reçoit l’adresse de la page, sans ses paramètres ni son ancre (qui peuvent contenir votre situation), le site d’où vous venez, un indicateur de navigateur automatisé et un signal d’utilisation réelle (défilement, clic ou dix secondes d’affichage). Sur la page d’accueil s’y ajoutent les étapes atteintes — résultats affichés, budget calculé, fiche ouverte — et le type d’écran, tactile ou non. Aucune réponse au calculateur, aucun montant, aucune adresse IP ni aucun identifiant n’est transmis ou conservé : le compteur ne garde que des totaux par jour et par heure, le pays déduit de la connexion et, pour les visites qui semblent venir d’un robot, le nom du réseau d’hébergement. Il n’écrit rien dans votre navigateur.</p>
<p>Si un outil de mesure déposant des cookies était ajouté un jour, votre accord serait demandé avant tout dépôt, par un bandeau, et vous pourriez le retirer à tout moment.</p>

<h2 id="retours">Page « Vos retours »</h2>
<p>La page <a href="/retours/">Vos retours</a> est la seule du site qui transmette des informations à un serveur. Ce qu’elle enregistre, et rien d’autre :</p>
<ul>
<li><b>Le message</b> que vous écrivez, et le <b>prénom ou pseudonyme</b> si vous en indiquez un. Aucune adresse e-mail n’est demandée : le service ne peut donc pas vous répondre, ni vous reconnaître d’un message à l’autre.</li>
<li>Une <b>empreinte technique de votre adresse IP</b>, transformée par une fonction à sens unique et jamais conservée en clair. Elle sert uniquement à limiter le nombre de messages envoyés depuis un même appareil, et elle est effacée au bout de deux jours.</li>
</ul>
<p><b>Finalité</b> : recueillir les retours des visiteurs pour corriger et améliorer le site, et publier ceux qui peuvent aider d’autres familles. <b>Base légale</b> : l’intérêt légitime de l’éditeur à améliorer son service, et votre démarche volontaire pour la publication.</p>
<p><b>Publication</b> : les messages sont publiés dès leur envoi, sans relecture préalable. Ils n’engagent que leur auteur. L’éditeur agit en qualité d’hébergeur au sens de la loi pour la confiance dans l’économie numérique : il retire promptement tout message signalé qui met en cause nommément un établissement, permet d’identifier une personne ou présente un caractère manifestement illicite. Chaque message porte un lien de signalement, et l’adresse ci-dessous reçoit les demandes de retrait. <b>Conservation</b> : les messages en ligne le restent jusqu’à leur retrait ; les messages retirés sont effacés au bout de trente jours.</p>
<p><b>Sous-traitant</b> : le point de réception et la base de données sont hébergés chez Cloudflare, Inc. Aucune donnée n’est transmise à des établissements, à des annonceurs ou à des tiers commerciaux.</p>
<p><b>Ce qu’il ne faut pas y écrire</b> : cette page est publique. N’y indiquez aucune donnée de santé, aucune ressource, aucun nom de résident, de proche ou de salarié, aucune adresse ni numéro de téléphone. Pour une situation particulière, écrivez à l’adresse ci-dessous.</p>

<h2>Droits</h2>
<p>Le calculateur ne collecte aucune donnée personnelle : les informations que vous y saisissez ne quittent pas votre appareil, et il n’y a donc rien à demander à leur sujet.</p>
<p>Pour un message envoyé sur la page « Vos retours », vous pouvez demander à le consulter, le corriger ou l’effacer. Le service ne conservant aucun moyen de vous identifier, indiquez dans votre demande la date approximative et le contenu du message, pour qu’il puisse être retrouvé. Vous disposez également du droit d’introduire une réclamation auprès de la CNIL. Pour toute question : <a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a>.</p>
"""},
]

NOTFOUND = """
<p>Cette page n’existe pas, ou plus. Voici par où reprendre :</p>
<ul>
<li><a href="/">Le calculateur du reste à charge, sur la carte</a></li>
<li><a href="/ehpad/">Les EHPAD en France</a> — par région, département, ville et établissement</li>
<li><a href="/prix-ehpad/">Le prix des EHPAD</a> et <a href="/prix-ehpad-par-departement/">le classement par département</a></li>
<li><a href="/aides-ehpad/">Les aides pour financer un EHPAD</a></li>
<li><a href="/guides/">Les guides</a> — choisir, visiter, monter un dossier</li>
<li><a href="/notre-methodologie.html">Notre méthodologie</a> · <a href="/qui-sommes-nous.html">Qui sommes-nous ?</a></li>
</ul>
<p>Vous cherchiez un établissement précis ? Le calculateur affiche les EHPAD autour d’un code postal, avec le reste à charge de chacun.</p>
"""

import json as _json
PERSONNE_LD = ('<script type="application/ld+json">' + _json.dumps({
    "@context": "https://schema.org", "@type": "AboutPage", "url": "https://trouver-mon-ehpad.fr/qui-sommes-nous.html",
    "mainEntity": {"@type": "Person", "@id": "https://trouver-mon-ehpad.fr/#editeur", "name": "David Rival",
                   "url": "https://trouver-mon-ehpad.fr/qui-sommes-nous.html#editeur",
                   "jobTitle": "Éditeur de Trouver mon EHPAD",
                   "description": "Juriste de formation (master 2 en droit des affaires), il conçoit des outils numériques et a construit ce site seul, sans financement ni partenariat, à partir des données publiques."}},
    ensure_ascii=False) + '</script>')

# --- page des crédits photo (30/09/2026) : une ligne par photo Wikimedia ou Panoramax publiée
import json as _json
_cr_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photos', 'credits.json')
_cr = _json.load(open(_cr_p, encoding='utf-8')) if os.path.exists(_cr_p) else []
_noms = {e['fin']: e for e in _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'merged_v2.json'), encoding='utf-8'))}
import html as _h
def _ligne(c):
    e = _noms.get(c['fin'], {})
    nom = _h.escape(e.get('nom', c['fin']).title()) + (' (' + _h.escape(e.get('ville', '').title()) + ')' if e.get('ville') else '')
    lic = _h.escape(c.get('licence') or '')
    if c.get('licence_url'): lic = f'<a href="{_h.escape(c["licence_url"])}" rel="nofollow noopener" target="_blank">{lic}</a>'
    aut = _h.escape(c.get('auteur') or '')
    return (f'<tr><td>{nom}</td><td>{_h.escape(c["source"])}</td><td>{aut or "—"}</td><td>{lic}</td>'
            f'<td><a href="{_h.escape(c["lien"])}" rel="nofollow noopener" target="_blank">Voir</a></td></tr>')
if _cr:
    PAGES.append({
     'file': 'credits-photos.html', 'slug': 'credits-photos.html',
     'title': 'Crédits photo | Trouver mon EHPAD',
     'desc': 'Auteur, licence et source de chaque photo d’établissement publiée sur le site.',
     'robots': 'noindex, follow', 'h1': 'Crédits photo',
     'body': f"""<p>{len(_cr)} photos d’établissements sont publiées sous licence libre. Elles sont réutilisées sans modification, sauf le recadrage des photos Panoramax dans la direction de l’établissement. Les autres vignettes sont des vues aériennes de l’IGN (BD ORTHO, Licence Ouverte 2.0). <a href="/mentions-legales.html#photos">Comment les photos sont choisies</a>.</p>
<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Établissement</th><th>Source</th><th>Auteur</th><th>Licence</th><th>Original</th></tr></thead>
<tbody>{''.join(_ligne(c) for c in sorted(_cr, key=lambda c: _noms.get(c['fin'], {}).get('nom', '')))}</tbody></table></div>"""})

for p in PAGES:
    html = HEAD.format(title=p['title'], desc=p['desc'], slug=p['slug'], robots=p['robots'],
                       h1=p['h1'], body=p['body'], font=FONT, css=CSS,
                       jsonld=crumb(p['h1'], p['slug']) + (PERSONNE_LD if p['file'] == 'qui-sommes-nous.html' else ''),
                       mesure=MESURE)
    open(os.path.join(SITE, p['file']), 'w', encoding='utf-8').write(html)

open(os.path.join(SITE, '404.html'), 'w', encoding='utf-8').write(
    HEAD.format(title='Page introuvable | Trouver mon EHPAD', desc='Cette page n’existe pas.', slug='404.html',
                robots='noindex, follow', h1='Page introuvable', body=NOTFOUND, font=FONT, css=CSS, jsonld='', mesure=MESURE))
print('pages annexes générées :', [p['file'] for p in PAGES] + ['404.html'])
