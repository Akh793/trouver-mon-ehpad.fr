/* ---------- Thème clair / sombre et barre de défilement ----------
   Partagé mot pour mot par l'accueil et par les pages de contenu. */
(function () {
  var CLE = 'mon_ehpad_theme', racine = document.documentElement;

  function theme() { return racine.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; }
  function poseTheme(t, memorise) {
    if (t === 'dark') racine.setAttribute('data-theme', 'dark');
    else racine.removeAttribute('data-theme');
    if (memorise) { try { localStorage.setItem(CLE, t); } catch (e) {} }
    // il y a deux boutons : un dans l'en-tête de page, un dans la barre de défilement
    document.querySelectorAll('.js-theme').forEach(function (b) {   // l'icône bascule en CSS
      b.setAttribute('aria-label', t === 'dark' ? 'Repasser au thème clair' : 'Passer au thème sombre');
      b.setAttribute('aria-pressed', String(t === 'dark'));
    });
    try { (window.dataLayer = window.dataLayer || []).push({ event: 'theme_changed', theme: t }); } catch (e) {}
  }

  function pret() {
    poseTheme(theme(), false);              // synchronise l'icône avec ce que l'amorçage a posé
    document.querySelectorAll('.js-theme').forEach(function (b) {
      b.addEventListener('click', function () { poseTheme(theme() === 'dark' ? 'light' : 'dark', true); });
    });

    // tant que l'utilisateur n'a pas tranché, on suit le réglage du système
    try {
      var mq = matchMedia('(prefers-color-scheme:dark)');
      var suit = function (e) { var c = null; try { c = localStorage.getItem(CLE); } catch (x) {}
        if (c !== 'dark' && c !== 'light') poseTheme(e.matches ? 'dark' : 'light', false); };
      if (mq.addEventListener) mq.addEventListener('change', suit);
    } catch (e) {}

    var barre = document.getElementById('topbar');
    if (!barre) return;

    // menu « Naviguer »
    var nav = document.getElementById('tb-nav'), menu = document.getElementById('tb-menu');
    if (nav && menu) {
      var ouvre = function (on) { menu.hidden = !on; nav.setAttribute('aria-expanded', String(on)); };
      nav.addEventListener('click', function (e) { e.stopPropagation(); ouvre(menu.hidden); });
      menu.addEventListener('click', function (e) { if (e.target.closest('a')) ouvre(false); });
      document.addEventListener('click', function () { if (!menu.hidden) ouvre(false); });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !menu.hidden) { ouvre(false); nav.focus(); }
      });
    }

    // apparition et progression : un seul calcul par image, jamais un par événement de défilement
    var jauge = document.getElementById('tb-prog'), enAttente = false, affichee = null, SEUIL = 260;
    function mesure() {
      enAttente = false;
      var y = window.pageYOffset || racine.scrollTop;
      var h = racine.scrollHeight - window.innerHeight;
      var visible = y > SEUIL;
      if (visible !== affichee) {
        affichee = visible;
        barre.classList.toggle('on', visible);
        // la barre de résultats vient coller juste sous celle-ci, jamais dessous
        racine.style.setProperty('--tb-h', visible ? barre.offsetHeight + 'px' : '0px');
      }
      if (jauge) jauge.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, y / h) : 0) + ')';
    }
    window.addEventListener('scroll', function () {
      if (!enAttente) { enAttente = true; requestAnimationFrame(mesure); }
    }, { passive: true });
    window.addEventListener('resize', mesure, { passive: true });
    mesure();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pret); else pret();
})();

/* =====================================================================
   app.js — Moteur de calcul du reste à charge en EHPAD + carte — v2.0
   Tout s'exécute dans le navigateur. Aucune donnée n'est transmise.
   Ordre des colonnes des fichiers data/dep/ehpad-XX.js : voir C ci-dessous
   et MAINTENANCE.md §3.
   ===================================================================== */
(() => {
  'use strict';

  const C = { fin:0, nom:1, cp:2, ville:3, lat:4, lon:5, p:6, pcd:7, pa:8, t12:9, t34:10, t56:11,
    maj:12, temp:13, linge:14, lingeU:15, nIncl:16, nSus:17, inclTxt:18, susTxt:19, ash:20, ashsrc:21,
    statut:22, statutsrc:23, cap:24, p2020:25, hasN:26, hasD:27, hasO:28, hasM:29, hasC:30, hasCI:31,
    alim:32, tel:33, adr:34, pm:35, siren:36, ouv:37, approx:38, mft:39, mftlib:40, tarif:41, pui:42,
    dens:43, occ:44, reg:45 };

  /* ---------- Chargement à la demande, par département (compatible file://) ---------- */
  const EHPAD = {}, COMMUNES = {}, PRIX = {}, pending = {};
  function servir(store, d, key) { (pending[key] || []).forEach((f) => f()); delete pending[key]; }
  window.ME = {
    dep(d, rows) { EHPAD[d] = rows; servir(EHPAD, d, 'e' + d); },
    com(d, rows) { COMMUNES[d] = rows; servir(COMMUNES, d, 'c' + d); },
    prix(d, rows) { PRIX[d] = rows; servir(PRIX, d, 'p' + d); },
  };
  const STORES = { e: EHPAD, c: COMMUNES, p: PRIX };
  const FICHIERS = { e: 'ehpad', c: 'communes', p: 'prix' };
  function loadDep(kind, d) {
    const store = STORES[kind], key = kind + d;
    if (store[d]) return Promise.resolve(store[d]);
    return new Promise((resolve) => {
      const done = () => resolve(store[d] || (kind === 'p' ? {} : []));
      if (pending[key]) { pending[key].push(done); return; }
      pending[key] = [done];
      const s = document.createElement('script');
      s.src = `data/dep/${FICHIERS[kind]}-${d}.js`;
      s.async = true;
      s.onerror = () => { store[d] = kind === 'p' ? {} : []; servir(store, d, key); };
      document.head.appendChild(s);
    });
  }

  /* ---------- Géographie ---------- */
  const rad = (x) => (x * Math.PI) / 180;
  function distKm(a, b, c, d) {
    const dLat = rad(c - a), dLon = rad(d - b);
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a)) * Math.cos(rad(c)) * Math.sin(dLon / 2) ** 2;
    return 2 * 6371 * Math.asin(Math.min(1, Math.sqrt(h)));
  }
  function depsForCp(cp) {
    const p = String(cp || '');
    if (p.startsWith('97') || p.startsWith('98')) return [p.slice(0, 3)];
    if (p.startsWith('20')) return ['2A', '2B'];
    return [p.slice(0, 2)];
  }
  function depDeInsee(insee) {
    const s = String(insee || '');
    if (s.startsWith('97') || s.startsWith('98')) return s.slice(0, 3);
    if (s.startsWith('20')) return +s.slice(0, 3) < 202 ? '2A' : '2B';
    return s.slice(0, 2);
  }
  function depsInRadius(lat, lon, km) {
    const dLat = km / 111, dLon = km / (111 * Math.max(0.2, Math.cos(rad(lat))));
    const box = [lat - dLat, lon - dLon, lat + dLat, lon + dLon], out = [];
    for (const [d, b] of Object.entries(window.ME_BBOX || {}))
      if (b[0] <= box[2] && b[2] >= box[0] && b[1] <= box[3] && b[3] >= box[1]) out.push(d);
    return out;
  }

  /* ---------- État ---------- */
  const state = {
    mode: 'famille',
    cp: '', commune: null, rayon: 20,
    gir: '34',
    revenus: NaN, autres: 0, epargne: NaN, proprietaire: false,
    pourQui: 'proche',         // 'proche' = on cherche pour quelqu'un · 'moi' = pour soi-même
    couple: false, conjointDomicile: false, deuxResidents: false,
    revenusConjoint: 0,        // ressources propres du conjoint, jamais mêlées à celles du résident
    aideLogement: 0, imposable: false,
    // une aide au logement est notifiée POUR UN établissement : elle ne vaut pas partout
    aplPortee: 'cet',        // 'cet' = pour l'établissement indiqué · 'partout' = hypothèse
    aplEtab: null,           // FINESS de l'établissement pour lequel elle est notifiée
    moisAnnee: 12,           // mois passés en établissement sur l'année fiscale
    chambre: 'cs',
    enfants: 0, tmi: 30,
    ashOnly: false, ashConfirmer: true, statuts: { 0: true, 1: true, 2: true },
    hasAB: false, tempOnly: false, prixConnu: false,
    tri: 'rac', priorite: 'rac', besoinAsh: 'nsp', favoris: [], favorisOnly: false,
    compare: [], selection: null, nbAffiches: 15, vue: 'carte', cmpDiff: false, cmpPlus: false,
    demarche: {},              // mode professionnel : { finess: { s: statut, n: note } }
    dossier: null,             // nom de la recherche en cours
  };
  /** Le reste à charge n'est affiché que si les ressources sont connues :
   *  sans elles, on montre le tarif, et on le dit. */
  /* ---------- Pour qui cherche-t-on ? ----------
     Le calcul est rigoureusement le même. Seules les formulations changent, pour que
     la personne qui cherche pour elle-même n'ait pas à traduire chaque phrase. */
  const pourMoi = () => state.pourQui === 'moi';
  const MOTS = {
    proche: {
      sujet: 'votre parent', Sujet: 'Votre parent', possessif: 'ses', Possessif: 'Ses',
      res: 'les ressources de votre parent', resMaj: 'Les ressources de votre parent',
      retraite: 'la retraite de votre parent', il: 'il', y_droit: 'votre parent y a droit',
      autonomie: 'l’autonomie de votre parent', situation: 'la situation de votre parent',
      titre: 'votre parent',
    },
    moi: {
      sujet: 'vous', Sujet: 'Vous', possessif: 'vos', Possessif: 'Vos',
      res: 'vos ressources', resMaj: 'Vos ressources',
      retraite: 'votre retraite', il: 'vous', y_droit: 'vous y avez droit',
      autonomie: 'votre autonomie', situation: 'votre situation',
      titre: 'vous',
    },
  };
  const mot = (k) => MOTS[pourMoi() ? 'moi' : 'proche'][k];
  /* Le calcul démarre dès qu'une ressource est connue, d'où qu'elle vienne. Une personne
     sans retraite mais avec un loyer perçu, une rente ou l'allocation de solidarité aux
     personnes âgées n'est pas une personne sans ressources : elle ne doit pas être renvoyée
     à l'affichage des seuls tarifs. */
  const perso = () => (Number.isFinite(state.revenus) ? state.revenus : 0) + (state.autres || 0) > 0;
  const pro = () => state.mode === 'pro';
  const MAX_SEL = () => (pro() ? 12 : 4);

  /* ---------- Mode professionnel : statuts de démarche ---------- */
  const STATUTS_DEMARCHE = [
    ['a-contacter', 'À contacter'], ['contacte', 'Contacté'],
    ['dossier-a-envoyer', 'Dossier à envoyer'], ['dossier-envoye', 'Dossier envoyé'],
    ['attente', 'En attente'], ['place', 'Place proposée'],
    ['refus', 'Refus'], ['ecarte', 'Écarté'],
  ];
  const LIB_STATUT = (k) => (STATUTS_DEMARCHE.find((x) => x[0] === k) || STATUTS_DEMARCHE[0])[1];
  function dem(fin) {
    if (!state.demarche[fin]) state.demarche[fin] = { s: 'a-contacter', n: '' };
    return state.demarche[fin];
  }
  // en mode professionnel, les mêmes gestes portent un nom distinct dans les statistiques
  const PRO_EVT = { search_started: 'pro_search_started', search_completed: 'pro_search_completed', result_opened: 'pro_result_opened' };
  /** Aucun événement ne contient de nom, de revenu ni d'information de santé : seulement des codes et des compteurs. */
  function evt(nom, extra) {
    try {
      if (pro() && PRO_EVT[nom]) nom = PRO_EVT[nom];
      (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: nom }, extra || {}));
    } catch (e) {}
  }

  /* ---------- Utilitaires ---------- */
  const M = () => META.month;
  /** Nombre de jours de l'année en cours : 366 une année bissextile, 365 sinon.
      Multiplier un montant mensuel par douze reviendrait à compter 30,5 × 12 = 366 jours
      chaque année : un jour de trop sur trois années sur quatre. */
  function joursAnnee(annee) {
    const y = annee || new Date().getFullYear();
    return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 366 : 365;
  }
  const euro = (n) => Math.round(n).toLocaleString('fr-FR') + ' €';
  const euro2 = (n) => n.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
  const nbfr = (n) => Number(n).toLocaleString('fr-FR', { maximumFractionDigits: 2 });
  const pct = (n, d) => (n >= 0 ? '+' : '') + n.toFixed(d === undefined ? 1 : d).replace('.', ',') + ' %';
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const dfr = (d) => (d ? String(d).slice(0, 10).split('-').reverse().join('/') : '');
  const mfr = (m) => { if (!m) return ''; const [y, mo] = String(m).split('-'); return `${mo}/${y}`; };
  const nom = (e) => (e[C.nom] || '').replace(/\s+/g, ' ').trim();
  /** 0478602323 → 04 78 60 23 23 : un numéro se lit par paires, et se compose mieux. */
  const telFr = (t) => String(t || '').replace(/\D/g, '').replace(/(\d\d)(?=\d)/g, '$1 ');
  /** « de Lyon » mais « d’Assieu » : l'élision, sinon la phrase sonne faux. */
  const de = (v) => (/^[aeiouyàâéèêëîïôöûüh]/i.test(v || '') ? 'd’' : 'de ') + v;

  /* ---------- Calcul ---------- */
  function girEffectif(g) { return g === '?' ? '34' : g; }
  function tarifGir(e, gir) {
    const g = girEffectif(gir);
    return g === '12' ? e[C.t12] : g === '34' ? e[C.t34] : e[C.t56];
  }

  /** APA en établissement — formule OpenFisca-France « apa_etablissement ». */
  function apaEtablissement(tarifGirMois, tarif56Mois, revenus, couple) {
    const B = BAREME, base = revenus / (couple ? B.divisionCouple : 1);
    const inf = B.seuilInf * B.mtp, sup = B.seuilSup * B.mtp;
    let participation;
    if (base <= inf) participation = tarif56Mois;
    else if (base <= sup) participation = tarif56Mois + (tarifGirMois - tarif56Mois) * ((base - inf) / (sup - inf)) * B.pente;
    else participation = tarif56Mois + (tarifGirMois - tarif56Mois) * B.pente;
    let apa = Math.max(0, tarifGirMois - participation);
    if (apa < B.seuilVersementSmic * B.smicHoraire) apa = 0;
    return { apa, participation: tarifGirMois - apa };
  }

  /* ---------- Trois notions de ressources, à ne jamais confondre ----------
     personne  : ce que perçoit le résident lui-même. C'est sur elles que porte sa
                 contribution à l'aide sociale (90 %), et son minimum de reste à vivre.
     conjoint  : ce que perçoit son conjoint. Saisi à part, jamais déduit du reste.
     ménage    : la somme des deux. C'est elle, divisée par deux, que le barème de
                 l'APA retient pour un couple — pas les ressources du résident seul. */
  function ressourcesPersonne(s) { return (Number.isFinite(s.revenus) ? s.revenus : 0) + (s.autres || 0); }
  function ressourcesConjoint(s) { return s.couple ? Math.max(0, s.revenusConjoint || 0) : 0; }
  function ressourcesMenage(s) { return ressourcesPersonne(s) + ressourcesConjoint(s); }
  /** Base de ressources du barème APA : le ménage divisé par deux pour un couple. */
  function ressourcesApa(s) {
    return (s.couple || s.deuxResidents) ? ressourcesMenage(s) : ressourcesPersonne(s);
  }
  /** Ressources qui font face à la facture calculée ici : celles des personnes hébergées. */
  function ressourcesTotales(s) { return s.deuxResidents ? ressourcesMenage(s) : ressourcesPersonne(s); }

  /** Reste à charge mensuel d'un établissement pour la situation saisie. */
  /** Avantage fiscal annuel POTENTIEL de la personne hébergée.

      Ce n'est pas une aide : c'est une réduction d'impôt, versée l'année suivante, et
      seulement si la personne paie effectivement de l'impôt. Elle ne doit donc jamais
      diminuer la somme à sortir chaque mois.

      Ce que le calcul applique :
        — assiette : frais d'hébergement et de dépendance restant à charge, APA et aide
          au logement déjà déduites ;
        — plafond de dépenses : 10 000 € par an et PAR PERSONNE hébergée ;
        — taux : 25 %, donc 2 500 € de réduction au maximum et par personne ;
        — prorata : seuls les mois réellement passés en établissement comptent.

      Ce que le calcul NE PEUT PAS savoir, et qu'il annonce :
        — le montant d'impôt réellement dû. Une réduction d'impôt ne peut pas dépasser
          l'impôt à payer, et elle n'est pas restituée. Une personne peu ou non imposable
          n'en tire rien, ou moins que le maximum. */
  function avantageFiscal(fraisJour, s, nbRes) {
    const mois = Math.max(0, Math.min(12, s.moisAnnee == null ? 12 : s.moisAnnee));
    // Le plafond de 10 000 € est annuel et ne se proratise pas en jours mais en
    // durée de séjour : on retient les mois déclarés, faute de dates précises.
    const plafondDepenses = BAREME.irPlafond * nbRes * (mois / 12);
    const plafondReduction = plafondDepenses * BAREME.irTaux;
    // L'assiette, elle, se compte en jours réels : pas de mois moyen multiplié par douze.
    const jours = Math.round(joursAnnee() * (mois / 12));
    const depenses = Math.max(0, fraisJour) * jours;
    const retenues = Math.min(depenses, plafondDepenses);
    const reduction = retenues * BAREME.irTaux;
    return {
      applicable: s.imposable === true,
      moisRetenus: mois,
      joursRetenus: jours,
      depenses,                         // frais engagés sur la période, en jours réels
      retenues,                         // part retenue après plafond
      plafondDepenses,
      plafondReduction,
      reduction: s.imposable ? reduction : 0,
      plafonne: depenses > plafondDepenses + 0.01,
      // le montant d'impôt dû n'est pas demandé : l'avantage reste un maximum théorique
      certitude: s.imposable ? 'potentiel' : 'sans objet',
    };
  }

  function calcule(e, s) {
    const mois = M(), nbRes = s.deuxResidents ? 2 : 1;
    const pj = s.chambre === 'cd' ? (e[C.pcd] || e[C.p]) : (e[C.p] || e[C.pcd]);
    const notes = [];
    if (pj == null) {
      // Le tarif « aide sociale » peut exister sans le tarif ordinaire : c'est une
      // information utile, il ne faut pas présenter l'établissement comme dépourvu de prix.
      const tarifAsh = e[C.pa];
      return {
        prixConnu: false,
        tarifAshSeul: tarifAsh != null ? tarifAsh : null,
        notes: [tarifAsh != null
          ? 'Tarif aide sociale disponible (' + euro2(tarifAsh) + '/jour) ; tarif hors aide sociale non renseigné. '
            + 'Le reste à charge ordinaire ne peut donc pas être calculé : demandez le prix à l’établissement.'
          : 'Cet établissement n’a pas communiqué son prix. Impossible de calculer ce qu’il vous coûterait : appelez-le pour le connaître.'],
      };
    }
    const chambreSupposee = s.chambre === 'cd' && e[C.pcd] == null;
    if (chambreSupposee) notes.push('Cet établissement n’a pas communiqué de prix pour les chambres doubles. Le calcul utilise celui d’une chambre seule — le vrai prix sera sans doute différent.');
    // Un GIR non connu ne devient pas un GIR moyen : il reste un GIR non connu, et le
    // montant qui en découle porte cette réserve partout où il s'affiche.
    const girSuppose = s.gir === '?';
    if (girSuppose) notes.push('Le niveau d’autonomie n’est pas connu. Le calcul retient un niveau moyen (GIR 3-4) pour donner un ordre de grandeur : le montant réel dépendra de l’évaluation faite par le médecin coordonnateur et le département, et il peut s’en écarter sensiblement.');

    const heberg = pj * mois * nbRes;
    const reg = regimeDe(e);

    // ── la part « aide au quotidien » de la facture, selon le régime du territoire
    let dependance = 0, apa = 0, apaConnue = false, pfJour = null, depConnue = false, depDouteuse = false;
    if (reg === 'exp') {
      // Participation forfaitaire nationale : ni GIR, ni condition de ressources.
      // On retient le montant en vigueur, pas celui déclaré à la CNSA, souvent antérieur.
      const pf = participationForfaitaire();
      pfJour = pf.montant;
      dependance = pf.montant * mois * nbRes;
      depConnue = true;
      apaConnue = false;           // l'APA en établissement est supprimée dans ces territoires
      const declare = e[C.t56];
      if (declare != null && Math.abs(declare - pf.montant) > 0.01) {
        notes.push('Cet établissement a déclaré ' + euro2(declare) + ' par jour lors de la dernière publication. '
          + 'Le calcul retient le montant national en vigueur, ' + euro2(pf.montant) + ' — ' + pf.src + '.');
      }
    } else if (reg === 'inconnu') {
      notes.push('Le régime de financement applicable à cet établissement n’a pas pu être établi. '
        + 'La part « aide au quotidien » n’est donc pas calculée : demandez-la à l’établissement.');
    } else {
      const tg = tarifGir(e, s.gir), t56 = e[C.t56];
      if (tg != null && t56 != null) {
        dependance = tg * mois * nbRes;
        depConnue = true;
        // apaEtablissement divise lui-même par deux lorsque le couple est signalé :
        // on lui passe donc le TOTAL du ménage, jamais les ressources du résident seul.
        const r = apaEtablissement(tg * mois, t56 * mois, ressourcesApa(s), s.couple || s.deuxResidents);
        apa = r.apa * nbRes; apaConnue = true;
        if (Math.abs(tg - t56) < 0.01) {
          notes.push('Cet établissement déclare le même tarif quel que soit le niveau d’autonomie, '
            + 'alors qu’il relève du régime de droit commun. L’aide du département ressort donc à zéro ici. '
            + 'Demandez-lui le tarif qui s’appliquera réellement.');
        }
        // Le barème impose t12 ≥ t34 ≥ t56. Un ordre inverse signale une déclaration
        // erronée : le montant calculé ici ne peut pas être tenu pour fiable.
        const t12 = e[C.t12], t34 = e[C.t34];
        if (t12 != null && t34 != null && (t12 < t34 - 0.001 || t34 < t56 - 0.001)) {
          depDouteuse = true;
          notes.push('Les tarifs dépendance déclarés par cet établissement sont dans un ordre impossible '
            + '(' + euro2(t12) + ' / ' + euro2(t34) + ' / ' + euro2(t56) + ' par jour du GIR 1-2 au GIR 5-6, '
            + 'alors que le tarif décroît toujours avec le niveau de dépendance). '
            + 'La part « aide au quotidien » affichée ici n’est donc pas fiable : faites-la confirmer.');
        }
      } else {
        notes.push('Cet établissement n’a pas communiqué le prix de l’aide au quotidien. '
          + 'Seul le logement est calculé ici : la facture réelle sera plus élevée.');
      }
    }

    // ── 1. LA FACTURE : ce que l'établissement réclame chaque mois
    const facture = heberg + dependance;

    // ── 2. LES AIDES, distinguées par leur modalité de versement
    //    apa : versée directement à l'établissement, elle diminue la facture
    //    apl : versée au résident ou à l'établissement selon les cas, mais mensuelle
    const aplSaisi = Math.max(0, s.aideLogement || 0);
    const aplConfirme = s.aplEtab && state.selection && s.aplEtab === e[C.fin];
    // Une aide notifiée pour un établissement ne vaut pas pour les autres.
    const apl = s.aplPortee === 'partout' ? aplSaisi : (aplConfirme ? aplSaisi : 0);
    const aplHypothese = aplSaisi > 0 && !aplConfirme && s.aplPortee === 'partout';

    // ── 3. CE QU'IL FAUT DÉCAISSER CHAQUE MOIS, avant tout effet fiscal
    const decaisse = Math.max(0, facture - apa - apl);

    // ── 4. L'AVANTAGE FISCAL : annuel, différé, et seulement potentiel
    const R = ressourcesTotales(s);
    // Assiette journalière : (facture − aides) ramenée au jour, pour éviter
    // l'arrondi du mois moyen dans un montant annuel.
    const fisc = avantageFiscal((facture - apa - apl) / mois, s, nbRes);
    const ir = 0;                 // ne diminue plus le mensuel : il est sorti du décaissement
    const rac = decaisse;         // « reste à charge » = ce qu'il faut sortir chaque mois
    const gardeMini = Math.max(BAREME.ashResteMiniPct * R, BAREME.ashResteMiniEur * nbRes);
    const reserveConjoint = (s.conjointDomicile && !s.deuxResidents) ? BAREME.ashConjointDomicile : 0;
    // Ce que la personne peut réellement consacrer chaque mois au décaissement.
    const dispo = Math.max(0, R - gardeMini - reserveConjoint);
    const trou = Math.max(0, decaisse - dispo);
    // L'épargne est consommée par le flux de trésorerie, pas par un montant après impôt.
    const moisEpargne = trou > 0 && s.epargne > 0 ? s.epargne / trou : (trou > 0 ? 0 : Infinity);

    let couleur = 'vert';
    if (trou > 0) couleur = moisEpargne >= 60 ? 'orange' : 'rouge';

    let ash = null;
    if (e[C.ash] === 1 || e[C.ash] === 2) {
      const prixAsh = e[C.pa] != null ? e[C.pa] * mois * nbRes : null;
      // Sous aide sociale, l'établissement facture son tarif « aide sociale », pas son tarif
      // commercial. Sans cette ligne, le lecteur ne peut pas rapprocher les montants affichés.
      const prixRetenu = prixAsh != null ? prixAsh : heberg;
      // Le résident contribue à hauteur de 90 % de ses ressources — mais jamais au-delà du prix :
      // on ne paie pas plus que ce qui est facturé.
      const partMax = Math.max(0, R - gardeMini - reserveConjoint);
      const partParent = Math.min(partMax, prixRetenu);
      const garde = Math.max(0, R - partParent - reserveConjoint);
      const reste = Math.max(0, prixRetenu - partParent);
      // L'aide sociale porte sur l'hébergement seul. La part « aide au quotidien »
      // (participation forfaitaire, ou tarif dépendance net d'APA) reste à la charge du
      // résident : elle doit apparaître, sinon le scénario sous-estime la dépense réelle.
      const depReste = depConnue ? Math.max(0, dependance - apa) : null;
      ash = { partParent, gardeMini, garde, reserveConjoint, prixAsh, prixRetenu,
        prixEstime: prixAsh == null, reste, aConfirmer: e[C.ash] === 2,
        depReste, depConnue, reg,
        // ce que la personne sortira réellement chaque mois dans ce scénario
        sortie: partParent + (depReste || 0) };
    }

    // répartition entre les enfants et coût net après impôt
    let famille = null;
    if (s.enfants > 0 && trou > 0) {
      const part = trou / s.enfants;
      // La tranche d'imposition saisie est celle d'UN foyer. L'appliquer à tous les enfants
      // serait une fiction : on la nomme comme une hypothèse, et on ne la soustrait pas.
      famille = {
        total: trou,                       // ce que les ressources ne couvrent pas
        nb: s.enfants,                     // nombre d'enfants saisi
        part,                              // répartition à parts égales : une hypothèse de travail
        tmiHypothese: s.tmi,
        economieSiTmi: part * (s.tmi / 100),   // ce que la déduction ferait gagner à CE foyer-là
        net: part * (1 - s.tmi / 100),
        netTotal: trou * (1 - s.tmi / 100),
      };
    }

    // Aucune extrapolation de places libres : le taux d'occupation est une moyenne de
    // segment issue d'une enquête, il ne dit rien de cet établissement un jour donné.
    // On conserve le fait sectoriel, daté et nommé comme tel.
    const secteur = e[C.occ] != null ? { occ: e[C.occ] } : null;

    // fraîcheur de la déclaration de prix
    let vieux = null;
    if (e[C.maj]) {
      const [y, mo] = String(e[C.maj]).split('-').map(Number);
      const moisEcoules = (new Date().getFullYear() - y) * 12 + (new Date().getMonth() + 1 - mo);
      if (moisEcoules >= 12) vieux = moisEcoules;
    }

    return {
      prixConnu: true, pj, nbRes, reg, pfJour, depConnue, depDouteuse, girSuppose, chambreSupposee,
      heberg, dependance,
      facture,                       // 1. ce que l'établissement facture
      apa, apaConnue, apl, aplHypothese,
      decaisse,                      // 2. ce qu'il faut sortir chaque mois
      fisc,                          // 3. avantage fiscal annuel, potentiel et différé
      rac, total: facture, aides: apa + apl,
      trou,                          // 5. contribution complémentaire nécessaire
      moisEpargne, couleur, ash, famille, secteur, vieux, notes,
    };
  }

  /* ---------- Sélection ---------- */
  async function chercher(s) {
    if (!s.commune) return [];
    const [lat, lon] = [s.commune.lat, s.commune.lon];
    const deps = depsInRadius(lat, lon, s.rayon);
    await Promise.all(deps.map((d) => loadDep('e', d)));
    await Promise.all(deps.map((d) => loadDep('p', d)));
    const out = [];
    for (const d of deps) for (const e of EHPAD[d] || []) {
      if (e[C.lat] == null) continue;
      const dist = distKm(lat, lon, e[C.lat], e[C.lon]);
      if (dist > s.rayon) continue;
      out.push({ e, dist, dep: d, prix: (PRIX[d] || {})[e[C.fin]] || null, r: calcule(e, s) });
    }
    return out;
  }

  function filtre(list, s) {
    return list.filter(({ e, r }) => {
      if (s.ashOnly && !(e[C.ash] === 1 || (s.ashConfirmer && e[C.ash] === 2))) return false;
      if (e[C.statut] != null && !s.statuts[e[C.statut]]) return false;
      if (s.hasAB && !(e[C.hasN] === 'A' || e[C.hasN] === 'B')) return false;
      if (s.tempOnly && e[C.temp] == null) return false;
      if (s.prixConnu && !r.prixConnu) return false;
      if (s.favorisOnly && s.favoris.indexOf(e[C.fin]) < 0) return false;
      return true;
    });
  }

  function trie(list, s) {
    const k = s.tri;
    return [...list].sort((a, b) => {
      if (k === 'dist') return a.dist - b.dist;
      if (k === 'prix') return (a.r.pj ?? 1e9) - (b.r.pj ?? 1e9);
      if (k === 'has') { const o = { A: 0, B: 1, C: 2, D: 3 }; return (o[a.e[C.hasN]] ?? 9) - (o[b.e[C.hasN]] ?? 9) || a.dist - b.dist; }
      // le tri « places libres estimées » a été retiré : aucune source ne donne la disponibilité réelle
      if (k === 'evol') return (a.prix?.e ?? 1e9) - (b.prix?.e ?? 1e9);
      return (a.r.rac ?? 1e9) - (b.r.rac ?? 1e9);
    });
  }

  /* ---------- Carte ---------- */
  /* ---------- Régime de financement de la dépendance ----------
     Dans 23 territoires, l'expérimentation de fusion des financements soins et dépendance
     a remplacé, depuis le 1er juillet 2025, le tarif dépendance par GIR et l'APA en
     établissement par une participation journalière forfaitaire, identique pour tous.
     Le régime vient du territoire d'implantation, jamais des tarifs déclarés :
     REGIMES.note explique pourquoi. */
  const REGIMES = {
    exp: {
      lib: 'Expérimentation de fusion des financements soins et dépendance',
      court: 'participation forfaitaire',
      depuis: '2025-07-01',
      // Montants nationaux, uniformes, par jour. Le dernier applicable fait foi.
      pf: [
        { debut: '2025-07-01', montant: 6.10, src: 'Arrêté du 6 juin 2025 (NOR TSSA2516495A)' },
        { debut: '2026-01-01', montant: 6.16, src: 'Instruction DGCS du 16 juin 2026, annexe 4' },
      ],
      note: 'Le résident ne paie plus un tarif lié à son GIR, ni une participation qui augmente avec ses ressources : une somme forfaitaire par jour, la même pour tous.',
    },
    classique: {
      lib: 'Régime de droit commun',
      court: 'tarif dépendance et APA',
      note: 'Le résident paie au minimum le tarif dépendance GIR 5-6. Au-delà, sa participation augmente avec ses ressources, selon un barème national.',
    },
  };
  /** Participation forfaitaire applicable à une date donnée. */
  function participationForfaitaire(iso) {
    const d = iso || new Date().toISOString().slice(0, 10);
    let r = null;
    REGIMES.exp.pf.forEach((p) => { if (p.debut <= d) r = p; });
    return r;
  }
  const regimeDe = (e) => (e[C.reg] === 'exp' ? 'exp' : e[C.reg] === 'classique' ? 'classique' : 'inconnu');

  const COULEUR = { vert: '#0f8a5f', orange: '#e08a00', rouge: '#d1344b', gris: '#94a3b8', bleu: '#2548FF' };
  let map = null, layer = null, cluster = null, leafletPromise = null;
  function loadScript(src) {
    return new Promise((resolve) => {
      const t = document.createElement('script');
      t.src = src; t.async = true; t.onload = resolve; t.onerror = resolve;
      document.head.appendChild(t);
    });
  }
  function ensureLeaflet() {
    if (window.L) return Promise.resolve();
    if (!leafletPromise) leafletPromise = loadScript('vendor/leaflet.js').then(() => loadScript('vendor/markercluster.js'));
    return leafletPromise;
  }
  function initMap() {
    if (map) return map;
    map = L.map('map', { scrollWheelZoom: false }).setView([46.6, 2.4], 6);
    L.tileLayer('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&STYLE=normal&FORMAT=image/png', {
      maxZoom: 18, minZoom: 5,
      attribution: '© <a href="https://www.ign.fr/" target="_blank" rel="noopener">IGN</a> — Géoplateforme',
    }).on('tileerror', () => { const n = $('tile-warn'); if (n) n.hidden = false; }).addTo(map);
    return map;
  }
  const MARQUEURS = {};
  async function dessineCarte(list, s) {
    await ensureLeaflet();
    if (!window.L) {
      const n = $('tile-warn');
      if (n) { n.hidden = false; n.textContent = 'Carte indisponible : la bibliothèque cartographique n’a pas pu être chargée. La liste reste complète.'; }
      return;
    }
    initMap();
    if (cluster) { map.removeLayer(cluster); cluster = null; }
    if (layer) { map.removeLayer(layer); layer = null; }
    Object.keys(MARQUEURS).forEach((k) => delete MARQUEURS[k]);
    const gros = list.length > 40, p = perso();
    const groupe = gros && window.L.markerClusterGroup
      ? L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 45 }) : L.layerGroup();
    list.forEach((o) => {
      const fin = o.e[C.fin];
      const col = !o.r.prixConnu ? COULEUR.gris : (p ? COULEUR[o.r.couleur] : COULEUR.bleu);
      const m = L.circleMarker([o.e[C.lat], o.e[C.lon]], { radius: 9, color: '#fff', weight: 2, fillColor: col, fillOpacity: .95 });
      m._base = col;
      m.bindTooltip(o.r.prixConnu ? euro(p ? o.r.rac : o.r.total) + '/mois' : 'tarif non déclaré',
        { permanent: !gros, direction: 'top', className: 'me-lbl' });
      m.on('click', () => selectionne(fin, { source: 'carte' }));
      m.on('mouseover', () => survole(fin, true));
      m.on('mouseout', () => survole(fin, false));
      MARQUEURS[fin] = m;
      groupe.addLayer(m);
    });
    const groupes = gros && !!window.L.markerClusterGroup;
    majLegende(p, groupes);
    if (groupes) { cluster = groupe; map.addLayer(cluster); }
    else { layer = groupe; map.addLayer(layer); }
    if (list.length) {
      const b = L.latLngBounds(list.map((o) => [o.e[C.lat], o.e[C.lon]]));
      b.extend([s.commune.lat, s.commune.lon]);
      map.fitBounds(b.pad(0.12));
    } else map.setView([s.commune.lat, s.commune.lon], 11);
    L.circleMarker([s.commune.lat, s.commune.lon], { radius: 6, color: '#2548FF', weight: 3, fillColor: '#fff', fillOpacity: 1 })
      .bindTooltip('Votre point de départ : ' + s.commune.nom, { direction: 'top' }).addTo(map);
    if (state.selection) marqueSelection(state.selection);
    if (!map._zoneBranche) {
      map._zoneBranche = true;
      map.on('moveend', () => {
        if (!state.commune) return;
        const c = map.getCenter();
        const d = distKm(c.lat, c.lng, state.commune.lat, state.commune.lon);
        $('zone-btn').hidden = d < Math.max(2, state.rayon * 0.25);
      });
    }
  }

  /** La légende dit exactement ce que la carte montre : tant que les ressources ne sont pas
      saisies, les points ne portent aucun jugement sur le reste à charge, ils sont bleus. */
  function majLegende(p, groupes) {
    const el = $('legende');
    if (!el) return;
    const pt = (c, t) => `<span><i style="background:${c}"></i> ${t}</span>`;
    el.innerHTML = (p
      ? pt(COULEUR.vert, 'couvert par les ressources')
        + pt(COULEUR.orange, 'tenable avec l’épargne')
        + pt(COULEUR.rouge, 'aide sociale ou famille nécessaires')
        + pt(COULEUR.gris, 'tarif non déclaré')
      : pt(COULEUR.bleu, 'tarif déclaré') + pt(COULEUR.gris, 'tarif non déclaré'))
      + '<span><i class="depart"></i> votre point de départ</span>'
      // les pastilles bleues numérotées ne disent rien du prix : elles comptent des établissements
      + (groupes ? '<span><i class="groupe">2</i> plusieurs établissements au même endroit — le chiffre les compte, zoomez pour les séparer</span>' : '');
  }

  /** Recentrer la recherche sur la zone affichée : on retient la commune la plus proche du centre. */
  async function chercheZone() {
    if (!map) return;
    const c = map.getCenter();
    const deps = depsInRadius(c.lat, c.lng, 25);
    await Promise.all(deps.map((d) => loadDep('c', d)));
    let best = null, bd = 1e9;
    deps.forEach((d) => (COMMUNES[d] || []).forEach((x) => {
      const dd = distKm(c.lat, c.lng, x[2], x[3]);
      if (dd < bd) { bd = dd; best = { cp: x[0], nom: x[1], lat: x[2], lon: x[3], insee: x[4] }; }
    }));
    if (!best) return;
    state.commune = best; state.cp = best.cp; state.nbAffiches = 15;
    cpInput.value = best.cp; $('commune').textContent = best.nom;
    $('zone-btn').hidden = true;
    evt('search_started', { commune: best.insee, rayon: state.rayon, source: 'carte' });
    render();
  }

  /** Survol croisé entre la liste et la carte. */
  function survole(fin, actif) {
    const el = $('item-' + fin);
    if (el) el.classList.toggle('survol', actif);
    const m = MARQUEURS[fin];
    if (m && fin !== state.selection) m.setStyle({ radius: actif ? 12 : 9, weight: actif ? 3 : 2 });
  }
  function marqueSelection(fin) {
    Object.keys(MARQUEURS).forEach((k) => {
      const m = MARQUEURS[k];
      if (k === fin) m.setStyle({ radius: 14, weight: 4, color: '#0f172a' }).bringToFront();
      else m.setStyle({ radius: 9, weight: 2, color: '#fff' });
    });
    const m = MARQUEURS[fin];
    if (m && map) { try { map.panTo(m.getLatLng(), { animate: true }); } catch (e) {} }
  }

  /* ---------- Fragments d'affichage ---------- */
  function badgeHas(e) {
    if (e[C.hasD] && String(e[C.hasD]).slice(0, 10) > new Date().toISOString().slice(0, 10)) {
      return '<span class="badge b-gris">évaluation à venir</span>';
    }
    if (!e[C.hasN]) return '<span class="badge b-gris">qualité non évaluée</span>';
    const cls = { A: 'b-vert', B: 'b-vert', C: 'b-orange', D: 'b-rouge' }[e[C.hasN]];
    return `<span class="badge ${cls}">Qualité ${e[C.hasN]}</span>`;
  }
  function badgeAsh(e) {
    const a = ASH_ETAT[e[C.ash]];
    return a ? `<span class="badge ${a.cls}">${a.txt}</span>` : '<span class="badge b-gris">Habilitation inconnue</span>';
  }

  /** Courbe compacte du prix (SVG inline, sans dépendance). */
  function sparkline(p) {
    const pts = p.p, W = 132, H = 34, pad = 3;
    const vals = pts.map((v, i) => [i, v]).filter((x) => x[1] != null);
    if (vals.length < 2) return '';
    const ys = vals.map((v) => v[1]), min = Math.min(...ys), max = Math.max(...ys), amp = (max - min) || 1;
    const X = (i) => pad + (i / (pts.length - 1)) * (W - 2 * pad);
    const Y = (v) => H - pad - ((v - min) / amp) * (H - 2 * pad);
    // Une année sans déclaration interrompt le tracé : relier deux points distants
    // dessinerait une progression régulière que personne n'a observée.
    let d = '', precedent = null;
    vals.forEach((v) => {
      const suite = precedent !== null && v[0] === precedent + 1;
      d += `${suite ? 'L' : 'M'}${X(v[0]).toFixed(1)},${Y(v[1]).toFixed(1)} `;
      precedent = v[0];
    });
    d = d.trim();
    const last = vals[vals.length - 1];
    const hausse = p.e >= 0;
    return `<svg class="spark" viewBox="0 0 ${W} ${H}" role="img" aria-label="Évolution du prix de ${p.d} à ${p.f} : ${pct(p.e)}">
      <path d="${d}" fill="none" stroke="${hausse ? '#d1344b' : '#0f8a5f'}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="${X(last[0]).toFixed(1)}" cy="${Y(last[1]).toFixed(1)}" r="2.6" fill="${hausse ? '#d1344b' : '#0f8a5f'}"/>
    </svg>`;
  }

  function blocPrix(p) {
    if (!p) return '';
    const vals = p.p.filter((x) => x != null);
    const infl = INFLATION_CUM_2018_2025;
    // Soustraire deux pourcentages donne des POINTS de pourcentage, jamais un pourcentage.
    const ecart = +(p.e - infl).toFixed(1);
    const points = (x) => (x >= 0 ? '+' : '−') + nbfr(Math.abs(x)) + ' point' + (Math.abs(x) >= 2 ? 's' : '');
    const complet = p.d === '2018' && p.f === '2025';
    const compl = complet
      ? `soit <b>${points(ecart)}</b> ${ecart >= 0 ? 'de plus' : 'de moins'} que l’inflation, qui a été de ${pct(infl)} sur la période`
      : `sur une période plus courte que 2018-2025&nbsp;: l’établissement n’a pas déclaré chaque année, la comparaison à l’inflation n’est donc pas faite`;
    const baisse = p.e < 0;
    const manquantes = p.p.length - vals.length;
    return `<div class="prix-box ${baisse ? 'baisse' : ''}">
      <div class="prix-h">${sparkline(p)}
        <div><b class="${baisse ? 'vert' : 'rouge'}">${pct(p.e)}</b> de ${p.d} à ${p.f}
          <span class="muted">(${p.a != null ? pct(p.a, 1) + ' par an' : '—'})</span></div>
      </div>
      <p class="prix-s">${euro2(vals[0])} → ${euro2(vals[vals.length - 1])} par jour${complet ? ' · ' + compl : ''}.</p>
      <p class="prix-n">${nbfr(vals.length)} année${vals.length > 1 ? 's' : ''} déclarée${vals.length > 1 ? 's' : ''} sur ${p.p.length}${manquantes
        ? `&nbsp;: ${manquantes} manquante${manquantes > 1 ? 's' : ''}, et la courbe s’interrompt là où la déclaration manque` : ''}.
        ${complet ? '' : compl.charAt(0).toUpperCase() + compl.slice(1) + '.'}</p>
      <details class="t-det f-hyp"><summary>Ce que cette comparaison suppose</summary>
        <p class="f-note">Que l’objet comparé soit resté le même d’une année sur l’autre&nbsp;: même type de
        chambre, mêmes prestations comprises dans le prix, même périmètre. La source publiée ne permet pas
        de le vérifier&nbsp;: un établissement qui cesse d’inclure l’entretien du linge fait baisser son
        prix affiché sans que rien ne coûte moins cher. Les prix sont déclarés par l’établissement, à des
        dates qui ne sont pas les mêmes pour tous.</p>
      </details>
    </div>`;
  }

  /** Y a-t-il de la place ? Aucune source publique ne le dit. On l'écrit, et on donne
      les questions qui, elles, obtiennent une réponse. */
  function blocDispo(r, e) {
    const tel = e && e[C.tel];
    const occ = r.secteur ? `<p class="muted">Pour situer le secteur, et non cet établissement&nbsp;:
      les EHPAD de même statut et de même type de commune accueillaient
      <b>${nbfr(r.secteur.occ)} résidents pour 100 places</b> lors de l’enquête EHPA 2023 de la DREES.
      Une moyenne nationale de segment ne dit rien du nombre de places libres ici aujourd’hui.</p>` : '';
    return `<div class="dispo-box">
      <b>Y a-t-il de la place&nbsp;?</b>
      <p><b>Disponibilité à confirmer auprès de l’établissement.</b> Les places réellement libres
      ne sont publiées dans aucune base publique&nbsp;: ni leur nombre, ni le délai d’attente.</p>
      <p>Les questions qui obtiennent une réponse utile&nbsp;:</p>
      <ul class="q-app">
        <li>Une place est-elle libre aujourd’hui, et pour quelle date d’entrée&nbsp;?</li>
        <li>S’agit-il d’une place habilitée à l’aide sociale&nbsp;?</li>
        <li>Quelle chambre est proposée, et à quel tarif exact&nbsp;?</li>
        <li>Combien de personnes sont inscrites avant nous&nbsp;?</li>
        <li>Quelles pièces faut-il fournir, et sous quel délai&nbsp;?</li>
      </ul>
      ${tel ? `<p class="q-tel"><a href="tel:${esc(tel)}">Appeler le ${esc(String(tel).replace(/(\d\d)(?=\d)/g, '$1 '))}</a></p>` : ''}
      ${occ}
    </div>`;
  }

  function detailHtml(o, s) {
    const r = o.r, e = o.e;
    if (!r.prixConnu) return `<p class="muted">${esc(r.notes[0])}</p>`;
    const l = (lib, val, cls) => `<div class="ln ${cls || ''}"><span>${lib}</span><b>${val}</b></div>`;
    const n = r.nbRes > 1 ? ' (pour deux résidents)' : '';
    const gir = girEffectif(s.gir) === '12' ? '1-2' : girEffectif(s.gir) === '34' ? '3-4' : '5-6';

    // ── ce que l'établissement facture
    let h = '<h4 class="f-t1">Ce que l’établissement facture</h4>';
    h += l(`Le logement, les repas, le ménage${n}`, euro(r.heberg) + '/mois');
    h += `<p class="f-note">${euro2(r.pj)} par jour × ${String(M()).replace('.', ',')} jours.</p>`;
    if (r.depConnue && r.reg === 'exp') {
      h += l(`L’aide aux gestes du quotidien${n}`, euro(r.dependance) + '/mois');
      h += `<p class="f-note">Se lever, se laver, s’habiller, manger. Dans ce territoire, cette part
        est une <b>participation forfaitaire</b> de ${euro2(r.pfJour)} par jour&nbsp;: la même pour tous,
        quel que soit le niveau d’autonomie et quelles que soient les ressources.</p>`;
      h += l('<b>Total facturé</b>', '<b>' + euro(r.total) + '/mois</b>', 'sstot');
    } else if (r.depConnue) {
      h += l(`L’aide aux gestes du quotidien${n}`, euro(r.dependance) + '/mois');
      h += `<p class="f-note">Se lever, se laver, s’habiller, manger. Le montant dépend du niveau
        d’autonomie&nbsp;: ici le GIR&nbsp;${gir}${s.gir === '?' ? ', retenu faute de mieux' : ''}.</p>`;
      h += l('<b>Total facturé</b>', '<b>' + euro(r.total) + '/mois</b>', 'sstot');
    } else {
      h += l(`L’aide aux gestes du quotidien${n}`, 'non calculée');
      h += `<p class="f-note">Cette part de la facture existe, mais nous ne disposons pas de
        l’information nécessaire pour la chiffrer ici. Le total ci-dessous est donc incomplet.</p>`;
    }

    // ── ce que les aides retirent
    const aides = [];
    if (r.apaConnue && r.apa > 0) aides.push([
      'L’allocation personnalisée d’autonomie (APA)', r.apa,
      'Versée par le département directement à l’établissement. Vous ne la touchez pas&nbsp;: elle vient en déduction de la facture.']);
    if (r.apl > 0) aides.push([
      'L’aide au logement', r.apl,
      'Versée par la caisse d’allocations familiales. Il faut la demander&nbsp;: elle n’est jamais automatique.']);


    if (aides.length) {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      aides.forEach(([lib, val, note]) => {
        h += l('− ' + lib, '− ' + euro(val) + '/mois', 'moins');
        h += `<p class="f-note">${note}</p>`;
      });
    } else if (r.reg === 'exp') {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      h += `<p class="f-note">Aucune. Dans ce territoire, l’APA en établissement est <b>supprimée</b>
        depuis le 1<sup>er</sup> juillet 2025&nbsp;: il n’y a plus d’aide à déduire, parce qu’il n’y a
        plus de participation à moduler. La participation forfaitaire ci-dessus en tient lieu.
        L’aide au logement, elle, reste due si ${mot('y_droit')}.</p>`;
    } else if (r.apaConnue) {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      h += r.notes.length
        ? '<p class="f-note">Aucune aide n’a pu être déduite, pour la raison suivante&nbsp;:</p>'
        : `<p class="f-note">Aucune aide n’a pu être déduite. Les ressources indiquées dépassent
           les plafonds, ou aucune aide n’a été saisie.</p>`;
    }
    // les avertissements se lisent ici, au moment où ils expliquent quelque chose
    h += r.notes.map((x) => `<p class="warn">${esc(x)}</p>`).join('');

    h += l('<b>Ce qu’il faut sortir chaque mois</b>', '<b>' + euro(r.decaisse) + '/mois</b>', 'tot');
    h += `<p class="f-note">C’est la somme à décaisser, une fois les aides versées à
      l’établissement déduites. Ni l’impôt, ni l’aide sociale ne sont comptés ici.</p>`;

    // Un montant mensuel laisse croire que l'entrée ne coûte rien de plus. Elle coûte.
    h += `<details class="t-det f-hyp"><summary>Ce que ce montant ne comprend pas</summary>
      <ul class="q-app">
        <li><b>Les frais du premier mois</b>&nbsp;: dépôt de garantie, souvent trente jours
            d’hébergement, frais de dossier, préavis du logement quitté, déménagement, mobilier.
            Aucune base ne les publie&nbsp;: demandez-en le détail chiffré avant de signer.</li>
        <li><b>Les dépenses personnelles</b>&nbsp;: mutuelle, coiffeur, pédicure, téléphone,
            télévision, protections non comprises, transports. Elles se règlent sur ce qui reste.</li>
        <li><b>Les prestations facturées en supplément</b>&nbsp;: ${e[C.nSus]
            ? nbfr(e[C.nSus]) + ' sont déclarées en supplément par cet établissement'
            : 'cet établissement n’en a déclaré aucune, ce qui ne veut pas dire qu’il n’en facture pas'}.</li>
      </ul></details>`;

    // L'avantage fiscal : annuel, différé, conditionnel — donc présenté à part.
    if (r.fisc && r.fisc.applicable && r.fisc.reduction > 0) {
      h += '<h4 class="f-t1">Et l’année suivante, l’impôt</h4>';
      h += l('Réduction d’impôt, au maximum', euro(r.fisc.reduction) + '/an');
      h += `<p class="f-note">25&nbsp;% des frais restants, dans la limite de
        ${euro(r.fisc.plafondDepenses)} de dépenses${r.fisc.moisRetenus < 12
          ? ' pour ' + r.fisc.moisRetenus + ' mois de séjour' : ' par an'}${r.nbRes > 1 ? ' et par personne hébergée' : ''}.
        ${r.fisc.plafonne ? 'Les frais dépassent ce plafond&nbsp;: le surplus ne donne droit à rien. ' : ''}
        C’est un <b>maximum</b>&nbsp;: une réduction d’impôt ne peut pas dépasser l’impôt réellement dû,
        et elle n’est pas remboursée. Elle arrive l’année suivante, jamais chaque mois.</p>`;
    } else if (r.fisc && !r.fisc.applicable) {
      h += `<p class="f-note">Une réduction d’impôt de 25&nbsp;% existe pour les personnes imposables.
        Indiquez-le dans «&nbsp;Préciser la situation&nbsp;» pour voir ce qu’elle représenterait.</p>`;
    }
    return h;
  }

  function blocFamille(r) {
    const f = r.famille;
    if (!f) return '';
    return `<div class="fam-box">
      <b>Si la famille complète</b>
      <p class="f-note">Ce que ${mot('res')} ne couvrent pas, partagé entre ${pourMoi() ? 'vos' : 'ses'} enfants.</p>
      <div class="ln tot"><span><b>Il manque chaque mois</b></span><b>${euro(f.total)}/mois</b></div>
      <div class="ln"><span>Si la somme est partagée à parts égales entre ${f.nb} enfants</span><b>${euro(f.part)}/mois chacun</b></div>
      <p class="f-note">Le partage à parts égales est une <b>hypothèse de travail</b>, pas une règle.
      Aucun barème national n’existe&nbsp;: le département, ou à défaut le juge aux affaires familiales,
      fixe la part de chacun selon ses revenus et ses charges. Les parts sont souvent inégales.</p>
      <details class="t-det f-hyp"><summary>Et l’effet sur l’impôt de chaque enfant</summary>
        <p class="f-note">La somme versée à un parent dans le besoin se déduit du revenu imposable de
        l’enfant qui la verse, sans plafond, sur justificatifs — y compris s’il règle l’EHPAD
        directement. En contrepartie, le parent doit la déclarer comme un revenu.</p>
        <div class="ln"><span>Pour un enfant dont la tranche serait ${f.tmiHypothese}&nbsp;%</span><b>− ${euro(f.economieSiTmi)}/mois</b></div>
        <p class="f-note">Ce chiffre ne vaut que pour un foyer à cette tranche-là. Chaque enfant a la
        sienne, et l’économie réelle dépend de l’ensemble de sa déclaration. Ce montant ne se soustrait
        pas de ce qu’il faut verser&nbsp;: il arrive l’année suivante, sur son impôt.</p>
      </details>
    </div>`;
  }

  /* ---------- Carte de résultat : lisible en deux secondes ---------- */
  function res(o, s, rang) {
    const e = o.e, r = o.r, fin = e[C.fin], p = perso();
    const sel = state.selection === fin;
    const fav = state.favoris.indexOf(fin) >= 0;
    const cmp = state.compare.indexOf(fin) >= 0;
    let montant, lib, second = '';
    if (!r.prixConnu) { montant = 'Tarif non déclaré'; lib = ''; }
    else if (p) {
      montant = euro(r.rac); lib = 'à financer / mois';
      second = r.aides >= 1
        ? `<span class="tarif">Tarif&nbsp;: ${euro(r.total)} · aides −${euro(r.aides)}</span>`
        : `<span class="tarif">Tarif&nbsp;: ${euro(r.total)} · aucune aide déduite</span>`;
      // Un montant ne doit jamais paraître plus sûr que les données qui le produisent.
      if (!r.depConnue) second += '<span class="tarif t-reserve">hors aide au quotidien, non déclarée</span>';
      else if (r.depDouteuse) second += '<span class="tarif t-reserve">tarifs dépendance à confirmer</span>';
      else if (r.girSuppose) second += '<span class="tarif t-reserve">niveau d’autonomie supposé</span>';
      if (r.chambreSupposee) second += '<span class="tarif t-reserve">tarif de chambre double non déclaré</span>';
    } else {
      montant = euro(r.total); lib = 'tarif / mois';
      second = '<span class="tarif">avant les aides</span>';
    }
    const badges = [];
    if (e[C.ash] === 1) badges.push('<span class="badge b-vert">Aide sociale possible</span>');
    else if (e[C.ash] === 2) badges.push('<span class="badge b-orange">Aide sociale à confirmer</span>');
    if (e[C.statut] != null) badges.push(`<span class="badge b-slate">${esc(STATUTS[e[C.statut]])}</span>`);
    if (e[C.hasN]) badges.push(badgeHas(e));
    return `<article class="res ${r.prixConnu ? '' : 'sansprix'}" id="item-${fin}" role="listitem" tabindex="0"
        data-fin="${fin}" aria-current="${sel}" aria-label="${esc(nom(e))}, ${montant} ${lib}">
      <p class="res-n">${esc(nom(e))}</p>
      <p class="res-l">${esc(e[C.ville])} · ${nbfr(+o.dist.toFixed(1))} km${e[C.cap] ? ' · ' + e[C.cap] + ' places' : ''}</p>
      <div class="res-m" style="color:${r.prixConnu ? (p ? COULEUR[r.couleur] : 'var(--ink)') : 'var(--mut2)'}">
        <b>${montant}</b>${lib ? `<small>${lib}</small>` : ''}${second}
      </div>
      <div class="res-b">${badges.join('')}</div>
      ${rang === 0 ? `<p class="res-pourquoi">${pourquoi(o, s)}</p>` : ''}
      <div class="res-act print-hide">
        <button type="button" class="mini2" data-voir="${fin}">Voir la fiche</button>
        <button type="button" class="mini2 ${cmp ? 'on' : ''}" data-cmp="${fin}" aria-pressed="${cmp}">${libCmp(cmp)}</button>
        <button type="button" class="mini2 fav ${fav ? 'on' : ''}" data-fav="${fin}" aria-pressed="${fav}" title="Garder pour plus tard">${fav ? '♥ Gardé' : '♡ Garder'}</button>
        ${e[C.tel] ? `<a class="mini2 res-tel" data-tel href="tel:${esc(String(e[C.tel]).replace(/\D/g, ''))}"
             title="Seul l’établissement peut dire si une place est libre">☎ ${esc(telFr(e[C.tel]))}</a>` : ''}
        ${pro() ? `<span class="res-fin" title="Identifiant national de l’établissement, utilisé par les administrations et les professionnels">FINESS ${esc(fin)}</span>` : ''}
      </div>
      ${pro() && cmp ? `<p class="res-dem">${demLigne(fin)}</p>` : ''}
    </article>`;
  }

  const libCmp = (on) => (pro() ? (on ? '✓ Ajouté aux démarches' : 'Ajouter aux démarches') : (on ? '✓ Comparé' : 'Comparer'));
  const demLigne = (fin) => {
    const d = dem(fin);
    return `Démarche&nbsp;: <b>${esc(LIB_STATUT(d.s))}</b>${d.n ? ' · ' + esc(d.n) : ''}`;
  };
  /** Ajoute, met à jour ou retire la ligne d'état sur une carte, sans refaire toute la liste. */
  function majDemCarte(carte) {
    const fin = carte.dataset.fin, on = state.compare.indexOf(fin) >= 0;
    let l = carte.querySelector('.res-dem');
    if (!pro() || !on) { if (l) l.remove(); return; }
    if (!l) { l = document.createElement('p'); l.className = 'res-dem'; carte.appendChild(l); }
    l.innerHTML = demLigne(fin);
  }

  /** Pourquoi cet établissement arrive en tête — jamais un score opaque. */
  function pourquoi(o, s) {
    const raisons = [];
    if (s.tri === 'rac' && o.r.prixConnu) raisons.push(perso() ? 'le reste à charge le plus bas de la sélection' : 'le tarif le plus bas de la sélection');
    if (s.tri === 'dist') raisons.push('le plus proche de votre point de départ');
    if (s.tri === 'prix' && o.r.prixConnu) raisons.push('le tarif affiché le plus bas');
    if (s.tri === 'has' && o.e[C.hasN]) raisons.push('la meilleure évaluation officielle de la sélection');

    if (s.tri === 'evol' && o.prix) raisons.push('le tarif qui a le moins augmenté depuis ' + o.prix.d);
    if (o.e[C.ash] === 1 && s.ashOnly) raisons.push('habilité à l’aide sociale');
    if (o.dist < 5) raisons.push('à ' + nbfr(+o.dist.toFixed(1)) + ' km');
    return 'En tête parce que : ' + (raisons.slice(0, 3).join(' · ') || 'il correspond à vos critères');
  }

  /** Mode professionnel : ce qui est réellement vérifiable, coché ou non. */
  function compatibilites(o, s) {
    const l = [];
    const r = o.r;
    if (perso() && r.prixConnu) {
      const tenable = r.trou <= 0;
      l.push([tenable, tenable ? 'compatible avec les ressources indiquées'
        : `${euro(r.trou)}/mois au-delà des ressources indiquées`]);
    }
    if (o.e[C.ash] === 1) l.push([true, 'habilité à l’aide sociale à l’hébergement']);
    else if (o.e[C.ash] === 2) l.push([null, 'habilitation à l’aide sociale à confirmer auprès de l’établissement']);
    else if (o.e[C.ash] === 0) l.push([false, 'non habilité à l’aide sociale à l’hébergement']);
    l.push([true, `à ${nbfr(+o.dist.toFixed(1))} km de la zone recherchée`]);
    const avec = dernier.filter((x) => x.r.prixConnu);
    if (r.prixConnu && avec.length >= 5) {
      const med = avec.map((x) => x.r.total).sort((a, b) => a - b)[Math.floor(avec.length / 2)];
      l.push([r.total <= med, r.total <= med ? 'tarif inférieur ou égal à la médiane de la sélection'
        : 'tarif supérieur à la médiane de la sélection']);
    }
    if (o.e[C.temp] != null) l.push([true, 'propose de l’accueil temporaire']);
    return `<ul class="compat">${l.map(([ok, t]) =>
      `<li class="${ok === true ? 'oui' : ok === false ? 'non' : 'inc'}"><i>${ok === true ? '✓' : ok === false ? '·' : '?'}</i>${esc(t)}</li>`).join('')}</ul>`;
  }

  /* ---------- Fiche : l'essentiel d'abord, le détail à la demande ---------- */
  const ONGLETS = [['ess', 'Essentiel'], ['prix', 'Prix & aides'], ['etab', 'L’établissement'], ['qual', 'Qualité']];
  let ongletActif = 'ess';

  function ficheHtml(o, s) {
    const e = o.e, r = o.r, p = perso();
    const gros = !r.prixConnu ? 'Tarif non déclaré' : euro(p ? r.rac : r.total);
    const lib = !r.prixConnu ? 'l’établissement ne l’a pas communiqué à la CNSA'
      : (p ? 'à payer chaque mois, une fois les aides déduites' : 'prix affiché, avant les aides');
    return `<div class="f-top">
        <div><h3>${esc(nom(e))}</h3><p class="f-loc">${esc(e[C.ville])} · ${nbfr(+o.dist.toFixed(1))} km de votre point de départ</p></div>
        <button type="button" class="f-close" data-fermer aria-label="Fermer la fiche">×</button>
      </div>
      <div class="f-prix">
        <div class="gros" style="color:${r.prixConnu ? (p ? COULEUR[r.couleur] : 'var(--ink)') : 'var(--mut2)'}">${gros}</div>
        <p class="lib">${lib}</p>
        ${r.prixConnu && p ? (r.aides >= 1
          ? `<p class="ctx">L’établissement facture ${euro(r.total)} · les aides en retirent ${euro(r.aides)}</p>`
          : r.reg === 'exp'
            ? `<p class="ctx">L’établissement facture ${euro(r.total)}. Dans ce territoire, l’APA en établissement
               n’existe plus&nbsp;: elle est remplacée par la participation forfaitaire déjà comprise dans ce montant.</p>`
            : `<p class="ctx">L’établissement facture ${euro(r.total)}, et aucune aide n’a pu être déduite${r.notes.length ? ' — la raison est expliquée dans l’onglet «&nbsp;Prix &amp; aides&nbsp;»' : ''}.</p>`) : ''}
        ${r.prixConnu && !p ? `<p class="ctx">Indiquez ${mot('retraite')}, en haut de page, pour voir ce qui resterait vraiment à payer.</p>` : ''}
        ${ecartMediane(o)}
      </div>
      <div class="f-faits">
        ${fait(e[C.cap] ? e[C.cap] : '—', e[C.cap] ? 'places dans l’établissement' : 'nombre de places non publié')}
        ${fait(e[C.ash] === 1 ? 'Oui' : e[C.ash] === 2 ? 'À vérifier' : e[C.ash] === 0 ? 'Non' : '—',
               'accepte l’aide sociale du département')}
        ${fait(e[C.statut] != null ? STATUTS[e[C.statut]] : '—', 'qui gère l’établissement')}
        ${fait(e[C.hasN] || '—', e[C.hasN] ? 'note officielle de qualité, de A à D' : 'pas encore évalué')}
      </div>
      <div class="f-cta print-hide">
        ${p ? '<button type="button" class="btn" data-modif>Modifier ma situation</button>'
            : '<button type="button" class="btn" data-modif>Estimer mon reste à charge</button>'}
        <button type="button" class="cta-s mini2" data-cmp="${e[C.fin]}">${libCmp(state.compare.indexOf(e[C.fin]) >= 0)}</button>
        <button type="button" class="cta-s mini2 fav" data-fav="${e[C.fin]}">${state.favoris.indexOf(e[C.fin]) >= 0 ? '♥ Gardé' : '♡ Garder'}</button>
      </div>
      <div class="f-onglets" role="tablist">
        ${ONGLETS.map(([k, t]) => `<button type="button" role="tab" data-onglet="${k}" aria-selected="${k === ongletActif}">${t}</button>`).join('')}
      </div>
      <div class="f-panneau" role="tabpanel">${ongletHtml(ongletActif, o, s)}</div>`;
  }

  function fait(val, lib) { return `<div><b>${esc(val)}</b><span>${esc(lib)}</span></div>`; }

  /** Une phrase, en français, sur ce que ce reste à charge veut dire pour cette famille.
      Aucun chiffre n'y est inventé : tout vient du calcul déjà affiché. */
  function resumeSimple(o) {
    const r = o.r, dispo = state.revenus + (state.autres || 0);
    if (r.rac <= dispo) {
      return `${mot('resMaj')} (${euro(dispo)}/mois) couvrent cette somme.`;
    }
    const manque = r.rac - dispo;
    if (state.epargne > 0 && r.moisEpargne !== Infinity && r.moisEpargne >= 12) {
      return `Il manque ${euro(manque)} chaque mois. L’épargne déclarée y pourvoirait environ
        ${Math.floor(r.moisEpargne)} mois.`;
    }
    return `Il manque ${euro(manque)} chaque mois : au-delà ${pourMoi() ? 'de vos ressources' : 'des ressources de votre parent'}.
      Les pistes — famille, aide sociale — sont détaillées dans l’onglet « Prix &amp; aides ».`;
  }

  /** Situer le tarif dans son contexte local — seulement si le calcul est fiable. */
  function ecartMediane(o) {
    if (!o.r.prixConnu) return '';
    const avec = dernier.filter((x) => x.r.prixConnu);
    if (avec.length < 5) return '';
    const med = avec.map((x) => x.r.total).sort((a, b) => a - b)[Math.floor(avec.length / 2)];
    const d = o.r.total - med;
    if (Math.abs(d) < 20) return '<p class="ctx">Tarif proche de la médiane de votre sélection.</p>';
    return `<p class="ctx">${euro(Math.abs(d))} ${d < 0 ? 'sous' : 'au-dessus de'} la médiane des ${avec.length} établissements de votre sélection.</p>`;
  }

  function ongletHtml(k, o, s) {
    const e = o.e, r = o.r;
    if (k === 'prix') {
      return `${detailHtml(o, s)}
        ${blocFamille(r)}
        ${r.ash ? `<div class="scenario"><b>Et si les ressources ne suffisent pas&nbsp;?</b>
            <p class="f-note">Le département peut payer la différence. C’est l’aide sociale à
            l’hébergement. Elle n’est possible que dans un établissement habilité — celui-ci l’est.</p>
            ${r.ash.aConfirmer ? '<p class="warn">Habilitation à vérifier : le répertoire officiel indique « non habilité », alors que l’établissement déclare un tarif « aide sociale ». Appelez-le pour savoir si une place habilitée est libre.</p>' : ''}
            <div class="ln"><span>Prix facturé dans ce cadre</span><b>${euro(r.ash.prixRetenu)}/mois</b></div>
            <p class="f-note">${r.ash.prixEstime
              ? 'Cet établissement n’a pas communiqué son tarif «&nbsp;aide sociale&nbsp;». Le calcul retient son tarif d’hébergement habituel : le vrai montant, fixé par le département, sera souvent plus bas.'
              : `Ce n’est pas le tarif affiché plus haut&nbsp;: sous aide sociale, le prix est fixé par le département${r.ash.prixRetenu < r.heberg ? `, ici ${euro(r.heberg - r.ash.prixRetenu)} de moins par mois que le tarif habituel` : ''}.`}</p>
            <div class="ln"><span>${mot('Sujet')} verse${pourMoi() ? 'z' : ''} sur ${pourMoi() ? 'vos' : 'ses'} propres ressources</span><b>− ${euro(r.ash.partParent)}/mois</b></div>
            <p class="f-note">${r.ash.reste > 0
              ? `Le département prend 90&nbsp;% de ses ressources, en lui laissant au minimum ${euro(BAREME.ashResteMiniEur)} par mois${r.ash.gardeMini <= BAREME.ashResteMiniEur * r.nbRes + 0.01 ? '&nbsp;— c’est ce plancher qui s’applique ici' : ''}.`
              : 'Il ne verse que le prix facturé&nbsp;: la règle des 90&nbsp;% est un plafond, pas un forfait.'}</p>
            <div class="ln"><span>Il lui resterait, après l’hébergement</span><b>${euro(r.ash.garde)}/mois</b></div>
            ${r.ash.depConnue && r.ash.depReste > 0
              ? `<div class="ln"><span>Mais l’aide aux gestes du quotidien reste due</span><b>− ${euro(r.ash.depReste)}/mois</b></div>
                 <p class="f-note">L’aide sociale ne couvre que l’hébergement. ${r.ash.reg === 'exp'
                   ? 'La participation forfaitaire, elle, reste à sa charge.'
                   : 'Le tarif dépendance restant après APA, lui, reste à sa charge.'}</p>
                 <div class="ln tot"><span><b>Pour ses dépenses personnelles, il resterait</b></span><b>${euro(Math.max(0, r.ash.garde - r.ash.depReste))}/mois</b></div>
                 ${r.ash.garde - r.ash.depReste < 0
                   ? `<p class="att">Ce reste à vivre est <b>négatif</b> de ${euro(r.ash.depReste - r.ash.garde)} par mois&nbsp;:
                      ${mot('res')} ne suffisent pas à couvrir cette part une fois la
                      contribution à l’hébergement versée. Le département apprécie ces situations au cas par cas
                      — c’est un point à soulever explicitement lors de la demande.</p>`
                   : ''}`
              : r.ash.depConnue
                ? ''
                : `<p class="f-note">La part «&nbsp;aide au quotidien&nbsp;» n’a pas pu être chiffrée&nbsp;:
                   elle se retranchera de ce montant, car l’aide sociale ne couvre que l’hébergement.</p>`}
            ${r.ash.reserveConjoint ? `<div class="ln"><span>Son conjoint resté à domicile garde</span><b>${euro(r.ash.reserveConjoint)}/mois</b></div>` : ''}
            <div class="ln tot"><span><b>Le département avance</b></span><b>${euro(r.ash.reste)}/mois</b></div>
            ${r.ash.reste > 0
              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour, à raison de
                 <b>${euro((r.ash.reste / M()) * joursAnnee())} par an</b> au rythme actuel. Le département peut en
                 demander tout ou partie&nbsp;: aux enfants au titre de l’obligation alimentaire pendant
                 le séjour, et à la succession ensuite.</p>
                 <p class="att">Ce n’est pas une créance calculable d’avance. Elle dépend de la durée réelle
                 du séjour, de l’évolution des tarifs et des ressources, des montants que le département
                 fixera, et de ce que comportera la succession. Nous ne projetons donc aucun total.</p>`
              : `<p class="f-note">Au tarif retenu, ${mot('res')} couvrent le prix&nbsp;:
                 le département n’aurait rien à avancer, donc rien à récupérer. L’aide sociale garde
                 un intérêt&nbsp;: elle ouvre l’accès au tarif habilité, souvent inférieur.</p>`}
            <p class="att">Le département peut aussi demander une participation aux enfants, et aux
            gendres et belles-filles. Aucun barème national n’existe&nbsp;: c’est lui, ou le juge, qui
            fixe les montants. <a href="/aides-ehpad/aide-sociale-hebergement/">Ce qu’il faut savoir avant de demander l’aide sociale</a></p>
            <details class="t-det f-hyp"><summary>Ce que ce scénario suppose</summary>
              <ul class="q-app">
                <li>Que l’aide sociale soit <b>accordée</b>&nbsp;: elle ne l’est pas de droit. Le département
                    vérifie les ressources, l’épargne, le patrimoine et la résidence.</li>
                <li>Qu’une <b>place habilitée</b> soit libre. L’habilitation de l’établissement ne garantit
                    pas que la place proposée le soit.</li>
                <li>${r.ash.prixEstime
                    ? 'Que le tarif aide sociale, <b>non communiqué</b> par cet établissement, soit proche de son tarif habituel. Le département fixe le vrai montant.'
                    : 'Que le tarif aide sociale déclaré reste celui qui sera appliqué.'}</li>
                <li>Que les ressources saisies correspondent à celles que le département retiendra&nbsp;:
                    ses règles ne recouvrent pas exactement la notion courante de revenu.</li>
              </ul>
              <p class="f-note">Ce calcul n’est pas une notification d’aide sociale. Seul le département
              en délivre une, après instruction du dossier.</p>
            </details>
          </div>` : ''}
        ${e[C.temp] != null ? `<h4 class="f-t1">Si le séjour est temporaire</h4>
          <div class="ln"><span>Tarif d’hébergement temporaire déclaré</span><b>${euro2(e[C.temp])}/jour</b></div>
          <p class="f-note">Les montants calculés sur cette page portent tous sur un
          <b>hébergement permanent</b>. L’hébergement temporaire est un autre régime&nbsp;: son tarif
          est distinct, l’APA y obéit à d’autres règles, l’aide sociale à l’hébergement n’y est pas
          acquise, et il est exclu de l’expérimentation de fusion des financements. Nous ne le
          calculons pas&nbsp;: demandez à l’établissement le coût d’un séjour temporaire, et au
          département les aides mobilisables pour cette formule.</p>` : ''}
        ${o.prix ? '<h4>L’évolution du tarif</h4>' + blocPrix(o.prix) : ''}
        <p class="f-src">Tarifs déclarés par l’établissement à la Caisse nationale de solidarité pour l’autonomie${e[C.maj] ? ', mis à jour ' + mfr(e[C.maj]) : ''}.</p>`;
    }
    if (k === 'etab') {
      const chips = [];
      if (e[C.temp] != null) chips.push(`<span class="chip">Accueil temporaire : ${euro2(e[C.temp])}/jour</span>`);
      if (e[C.linge] != null) chips.push(`<span class="chip">Linge facturé ${euro2(e[C.linge])}${e[C.lingeU] ? ' / ' + esc(e[C.lingeU]) : ''}</span>`);
      if (e[C.nIncl] || e[C.nSus]) chips.push(`<span class="chip">${e[C.nIncl] || 0} prestation(s) comprise(s) · ${e[C.nSus] || 0} en sus</span>`);
      if (e[C.tarif]) chips.push(`<span class="chip">${e[C.tarif] === 'G' ? 'Tarif global de soins' : e[C.tarif] === 'P' ? 'Tarif partiel de soins' : 'Petite unité de vie'}${e[C.pui] ? ' · pharmacie interne' : ''}</span>`);
      if (e[C.approx]) chips.push('<span class="chip chip-warn">position approximative : centre de la commune</span>');
      if (r.vieux) chips.push(`<span class="chip chip-warn">tarif déclaré il y a ${r.vieux} mois : demandez celui du jour</span>`);
      return `<div class="ln"><span>Adresse</span><b style="white-space:normal;text-align:right">${esc(e[C.adr] || 'Non publiée')}<br>${esc(e[C.cp])} ${esc(e[C.ville])}</b></div>
        <div class="ln"><span>Téléphone</span><b>${e[C.tel] ? `<a href="tel:${esc(e[C.tel])}">${esc(e[C.tel].replace(/(\d\d)(?=\d)/g, '$1 '))}</a>` : 'Non publié'}</b></div>
        <div class="ln"><span>Gestionnaire</span><b style="white-space:normal;text-align:right">${esc(e[C.pm] || 'Non publié')}</b></div>
        <div class="ln"><span>Ouvert depuis</span><b>${esc(e[C.ouv] || 'Non publié')}</b></div>
        <div class="ln"><span title="Identifiant national de l’établissement, utilisé par les administrations et les professionnels">Numéro FINESS</span><b>${esc(e[C.fin])}</b></div>
        ${blocDispo(r, e)}
        <div class="chips">${chips.join('')}</div>
        <div class="liens">
          <a href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-ehpad-et-maisons-de-retraite" target="_blank" rel="noopener">Fiche officielle (encadrement, absentéisme)</a>
          ${e[C.siren] ? `<a href="https://annuaire-entreprises.data.gouv.fr/entreprise/${esc(e[C.siren])}" target="_blank" rel="noopener">Qui gère cet établissement</a>` : ''}
          <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(nom(e) + ' ' + (e[C.cp] || '') + ' ' + (e[C.ville] || ''))}" target="_blank" rel="noopener">Itinéraire</a>
        </div>`;
    }
    if (k === 'qual') {
      const hasFutur = e[C.hasD] && String(e[C.hasD]).slice(0, 10) > new Date().toISOString().slice(0, 10);
      return `${hasFutur ? `<p class="warn">La date d’évaluation publiée par la Haute Autorité de santé
          (${dfr(e[C.hasD])}) est postérieure à aujourd’hui. Il s’agit d’une visite programmée, ou d’une
          erreur de saisie à la source&nbsp;: le résultat ci-dessous ne peut pas être lu comme une
          évaluation déjà rendue.</p>` : ''}
        <div class="ln"><span>Évaluation officielle</span><b>${e[C.hasN] || 'non publiée'}</b></div>
        ${e[C.hasD] ? `<div class="ln"><span>Date de l’évaluation</span><b>${dfr(e[C.hasD])}</b></div>` : ''}
        ${e[C.hasCI] != null ? `<div class="ln"><span>Critères impératifs atteints</span><b>${e[C.hasCI]} / 18</b></div>` : ''}
        ${e[C.hasM] != null ? `<div class="ln"><span>Moyenne des objectifs</span><b>${String(e[C.hasM]).replace('.', ',')} / 100</b></div>` : ''}
        ${Array.isArray(e[C.hasC]) && e[C.hasC][0] != null ? HAS_CHAPITRES.map((c, i) => `<div class="ln"><span>${esc(c)}</span><b>${String(e[C.hasC][i]).replace('.', ',')} / 4</b></div>`).join('') : ''}
        ${e[C.hasO] ? `<p class="muted" style="font-size:.78rem;margin-top:.5rem">Organisme évaluateur : ${esc(e[C.hasO])} — choisi et rémunéré par l’établissement lui-même.</p>` : ''}
        ${!e[C.hasN] ? '<p class="muted" style="font-size:.82rem;margin-top:.5rem">Aucune évaluation publiée. Cela ne dit rien de la qualité de l’établissement : toutes les évaluations ne sont pas encore réalisées ni publiées.</p>' : ''}
        <h4>Hygiène alimentaire</h4>
        ${e[C.alim] ? `<div class="ln"><span>Dernier contrôle du ${dfr(e[C.alim][1])}</span><b>${esc(e[C.alim][0])}</b></div>${e[C.alim][2] ? `<div class="ln"><span>Suite donnée</span><b>${esc(e[C.alim][2])}</b></div>` : ''}` : '<p class="muted" style="font-size:.82rem">Aucun contrôle publié pour cet établissement.</p>'}
        <p class="f-src">Évaluations : Haute Autorité de santé. Hygiène : Direction générale de l’alimentation.
        ${e[C.ashsrc] ? ' Habilitation à l’aide sociale : ' + esc(ASH_SRC[e[C.ashsrc]]) + '.' : ''}
        ${e[C.statutsrc] ? ' Statut : ' + esc(STATUT_SRC[e[C.statutsrc]]) + '.' : ''}</p>`;
    }
    // onglet « essentiel » : de quoi se faire une opinion en dix secondes
    const l = [];
    if (pro()) l.push(`<h4 style="margin-top:0">Ce qui est vérifiable</h4>${compatibilites(o, s)}`);
    l.push(`<div class="ln"><span>À quelle distance de votre point de départ</span><b>${nbfr(+o.dist.toFixed(1))} km</b></div>`);
    if (r.prixConnu) l.push(`<div class="ln"><span>Prix du logement, par jour</span><b>${euro2(r.pj)}</b></div>`);
    if (r.apaConnue && r.apa > 0) l.push(`<div class="ln"><span>Aide du département versée à l’établissement</span><b>${euro(r.apa)}/mois</b></div>`);
    if (o.prix) l.push(`<div class="ln"><span>De combien le prix a augmenté depuis ${o.prix.d}</span><b class="${o.prix.e < 0 ? 'vert' : 'rouge'}">${pct(o.prix.e)}</b></div>`);
    l.push(`<div class="ln"><span>Aide au quotidien</span><b>${r.reg === 'exp'
      ? 'forfait de ' + euro2(r.pfJour) + '/jour'
      : r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le niveau d’autonomie'}</b></div>`);
    l.push('<p class="f-note">Disponibilité&nbsp;: aucune source publique ne donne les places libres d’un établissement. '
      + 'À demander directement.</p>');
    if (r.moisEpargne !== Infinity && r.trou > 0 && state.epargne > 0)
      l.push(`<div class="ln"><span>Combien de temps l’épargne tiendrait</span><b>${Math.floor(r.moisEpargne)} mois</b></div>`);
    const tete = r.prixConnu && perso()
      ? `<p class="f-resume">${resumeSimple(o)}</p>` : '';
    return tete + l.join('') +
      r.notes.map((n) => `<p class="warn">${esc(n)}</p>`).join('') +
      (r.ash && r.ash.aConfirmer ? '<p class="warn">L’habilitation à l’aide sociale est à vérifier auprès de l’établissement.</p>' : '') +
      '<p class="f-src">Prix : Caisse nationale de solidarité pour l’autonomie. Identité et habilitation : répertoire FINESS. Évaluation : Haute Autorité de santé. Le détail est dans les autres onglets.</p>';
  }

  /* ---------- Contexte départemental ---------- */
  function contexteDept(dep, insee) {
    let d = (window.ME_DEP || {})[dep];
    if (!d) return '';
    if (dep === '69' && d.ashM && (window.ME_LYONM || []).indexOf(String(insee)) >= 0) d = { ...d, ...d.ashM };
    const p = [];
    if (d.b_places) p.push(`${d.b_places.toLocaleString('fr-FR')} places installées, dont <b>${nbfr(d.b_pct_ash)} % habilitées à l’aide sociale</b>`);
    if (d.b_etp) p.push(`${String(d.b_etp).replace('.', ',')} ETP par résident`);
    if (d.tx_equip) p.push(`${d.tx_equip[1].toFixed(0)} places pour 1 000 personnes de 75 ans et plus (${d.tx_equip[0]})`);
    if (d.ash_places) p.push(`${nbfr(+(d.ash_places[1] * 100).toFixed(1))} % des places occupées par un bénéficiaire de l’ASH (${d.ash_places[0]})`);
    const rec = { 1: 'Toujours', 2: 'Parfois', 3: 'Jamais' }[d.recours];
    const ob = [];
    if (d.obliges[0] === 1) ob.push('les enfants');
    if (d.obliges[1] === 1) ob.push('les gendres et belles-filles');
    if (d.obliges[3] === 1) ob.push('d’autres personnes');
    return `<p><b>${esc(d.nom || 'Département ' + dep)}</b> — ${p.join(' · ')}. <span class="muted">(DREES, données 2023 et 2024)</span></p>
      <p class="muted">Aide sociale à l’hébergement, pratique déclarée au conseil départemental en 2018 :
      ${rec ? `recours sur succession « ${rec} »` : 'recours sur succession non renseigné'}${ob.length ? ` ; obligation alimentaire demandée à ${ob.join(', ')}` : ''}${d.gir56 === 1 ? ' ; les frais de dépendance GIR 5-6 sont pris en charge' : d.gir56 === 0 ? ' ; les frais de dépendance GIR 5-6 ne sont pas pris en charge' : ''}.
      Les petits-enfants ne sont plus sollicités depuis la loi du 8 avril 2024, quelle que soit la pratique déclarée en 2018. Le règlement départemental d’aide sociale en vigueur fait foi.</p>`;
  }

  function recapTexte(s) {
    const gir = s.gir === '?' ? 'niveau d’autonomie inconnu (calcul sur la base du GIR 3-4)' : s.gir === '12' ? 'perte d’autonomie forte (GIR 1-2)' : s.gir === '34' ? 'perte d’autonomie partielle (GIR 3-4)' : 'autonomie relative (GIR 5-6)';
    let t = `Situation retenue : ${gir}, ${euro(ressourcesPersonne(s))} de ressources mensuelles pour la personne hébergée`;
    if (s.couple && ressourcesConjoint(s) > 0) t += `, ${euro(ressourcesConjoint(s))} pour son conjoint`;
    if (s.autres > 0) t += ` (dont ${euro(s.autres)} d’autres revenus)`;
    if (s.deuxResidents) t += ', deux résidents hébergés';
    else if (s.couple) t += ', en couple (ressources divisées par deux pour l’allocation personnalisée d’autonomie)';
    if (s.conjointDomicile) t += `, conjoint resté à domicile (${euro(BAREME.ashConjointDomicile)} réservés)`;
    if (Number.isFinite(s.epargne) && s.epargne > 0) t += `, ${euro(s.epargne)} d’épargne`;
    if (s.proprietaire) t += ', propriétaire de son logement';
    if (s.aideLogement > 0) t += `, aide au logement de ${euro(s.aideLogement)}/mois`;
    t += s.imposable ? ', imposable' : ', non imposable';
    if (s.enfants > 0) t += `, ${s.enfants} enfant${s.enfants > 1 ? 's' : ''} susceptible${s.enfants > 1 ? 's' : ''} de participer (tranche d’imposition ${s.tmi} %)`;
    t += `. Chambre ${s.chambre === 'cd' ? 'double' : 'seule'}, mois de ${String(M()).replace('.', ',')} jours.`;
    return t;
  }

  /* ---------- Comparateur ---------- */
  const CRIT_BASE = ['rac', 'total', 'dist', 'ash', 'cap', 'has'];
  const CRITERES = [
    ['rac', 'Ce qui resterait à financer', (o) => (o.r.prixConnu ? (perso() ? '<b>' + euro(o.r.rac) + '/mois</b>' : 'à calculer') : 'tarif non déclaré')],
    ['total', 'Tarif de l’établissement', (o) => (o.r.prixConnu ? euro(o.r.total) + '/mois' : '—')],
    ['dist', 'Distance', (o) => nbfr(+o.dist.toFixed(1)) + ' km'],
    ['ash', 'Aide sociale à l’hébergement', (o) => (ASH_ETAT[o.e[C.ash]] ? ASH_ETAT[o.e[C.ash]].txt : 'information non disponible')],
    ['cap', 'Capacité (2020)', (o) => (o.e[C.cap] ? o.e[C.cap] + ' places' : 'information non disponible')],
    ['has', 'Évaluation officielle', (o) => (o.e[C.hasN] ? o.e[C.hasN] + (o.e[C.hasD] ? ' — ' + dfr(o.e[C.hasD]) : '') : 'non publiée')],
    ['statut', 'Statut', (o) => (o.e[C.statut] != null ? esc(STATUTS[o.e[C.statut]]) : 'information non disponible')],
    ['pj', 'Tarif journalier', (o) => (o.r.prixConnu ? euro2(o.r.pj) + '/jour' : '—')],
    ['evol', 'Évolution du tarif', (o) => (o.prix ? pct(o.prix.e) + ' depuis ' + o.prix.d : 'information non disponible')],
    ['apa', 'Allocation personnalisée d’autonomie', (o) => (o.r.apaConnue ? euro(o.r.apa) + '/mois' : 'information non disponible')],
    ['ci', 'Critères impératifs atteints', (o) => (o.e[C.hasCI] != null ? o.e[C.hasCI] + ' / 18' : 'information non disponible')],
    ['alim', 'Hygiène alimentaire', (o) => (o.e[C.alim] ? esc(o.e[C.alim][0]) + ' — ' + dfr(o.e[C.alim][1]) : 'aucun contrôle publié')],
    ['reg', 'Aide au quotidien', (o) => (o.r.reg === 'exp' ? 'forfait ' + euro2(o.r.pfJour) + '/jour' : o.r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le GIR')],
    ['soins', 'Financement des soins', (o) => (o.e[C.tarif] === 'G' ? 'tarif global' : o.e[C.tarif] === 'P' ? 'tarif partiel' : o.e[C.tarif] === 'V' ? 'petite unité de vie' : 'information non disponible')],
    ['maj', 'Tarif mis à jour', (o) => mfr(o.e[C.maj]) || 'information non disponible'],
    ['tel', 'Téléphone', (o) => esc(o.e[C.tel] || 'non publié')],
    ['fin', 'Numéro FINESS', (o) => esc(o.e[C.fin])],
  ];
  function comparHtml() {
    if (pro()) return demarchesHtml();
    const sel = state.compare.map((f) => dernier.find((o) => o.e[C.fin] === f)).filter(Boolean);
    if (!sel.length) return '<p class="muted">Sélectionnez des établissements avec le bouton « Comparer » pour les mettre côte à côte.</p>';
    const crit = CRITERES.filter((c) => state.cmpPlus || CRIT_BASE.indexOf(c[0]) >= 0);
    const lignes = crit.map(([k, lib, fn]) => {
      const vals = sel.map(fn);
      if (state.cmpDiff && sel.length > 1 && vals.every((v) => v === vals[0])) return '';
      return `<tr><th>${lib}</th>${vals.map((v) => `<td>${v}</td>`).join('')}</tr>`;
    }).filter(Boolean);
    return `<table class="cmp">
      <tr><th></th>${sel.map((o) => `<td><b>${esc(nom(o.e))}</b><br><span class="muted">${esc(o.e[C.ville])}</span> <button type="button" class="x" data-del="${o.e[C.fin]}" aria-label="Retirer ${esc(nom(o.e))} de la comparaison">×</button></td>`).join('')}</tr>
      ${lignes.join('') || '<tr><th>Aucune différence</th><td colspan="' + sel.length + '">Ces établissements ne se distinguent sur aucun des critères affichés.</td></tr>'}
    </table>`;
  }

  /** Mode professionnel : la liste de démarches, avec l'état de chacune. */
  function demarchesHtml() {
    const sel = state.compare.map((f) => dernier.find((o) => o.e[C.fin] === f)).filter(Boolean);
    if (!sel.length) return '<p class="muted">Ajoutez des établissements depuis la liste des résultats, avec le bouton « Ajouter aux démarches ».</p>';
    const p = perso();
    return `<table class="dem-t">
      <thead><tr><th>Établissement</th><th class="num">${p ? 'Reste à charge' : 'Tarif'}</th><th class="num">Distance</th>
      <th>Aide sociale</th><th>Contact</th><th>Où en suis-je&nbsp;?</th><th></th></tr></thead>
      <tbody>${sel.map((o) => {
      const e = o.e, fin = e[C.fin], d = dem(fin);
      return `<tr id="dem-${fin}">
        <td data-l="Établissement"><b>${esc(nom(e))}</b><br><span class="muted">${esc(e[C.ville])}</span>
          <span class="finess" title="Identifiant national de l’établissement">FINESS ${esc(fin)}</span></td>
        <td class="num" data-l="Montant">${o.r.prixConnu ? euro(p ? o.r.rac : o.r.total) + '/mois' : '<span class="non">non déclaré</span>'}</td>
        <td class="num" data-l="Distance">${nbfr(+o.dist.toFixed(1))} km</td>
        <td data-l="Aide sociale">${ASH_ETAT[e[C.ash]] ? ASH_ETAT[e[C.ash]].txt : 'non publiée'}</td>
        <td data-l="Contact">${e[C.tel] ? `<a href="tel:${esc(e[C.tel])}">${esc(e[C.tel].replace(/(\d\d)(?=\d)/g, '$1 '))}</a>` : '<span class="non">non publié</span>'}</td>
        <td data-l="Où en suis-je ?">
          <select class="dem-s" data-statut="${fin}" aria-label="État de la démarche pour ${esc(nom(e))}">
            ${STATUTS_DEMARCHE.map(([k, t]) => `<option value="${k}"${d.s === k ? ' selected' : ''}>${t}</option>`).join('')}
          </select>
          <input class="dem-n" data-note="${fin}" value="${esc(d.n)}" maxlength="140"
            placeholder="Note : appelé le 11/09, rappeler lundi" aria-label="Note pour ${esc(nom(e))}">
        </td>
        <td class="dem-x"><button type="button" class="x" data-del="${fin}" aria-label="Retirer ${esc(nom(e))} de la liste">×</button></td>
      </tr>`;
    }).join('')}</tbody></table>
    <p class="fld-h" style="margin-top:.8rem">Les états et les notes restent sur cet appareil, dans ce navigateur. Ils ne sont ni transmis, ni sauvegardés ailleurs&nbsp;: vider le cache les efface. N’y écrivez aucune donnée nominative.</p>`;
  }

  /** Export CSV de la seule liste de démarches, états et notes compris. */
  function exportDemarches() {
    const sel = state.compare.map((f) => dernier.find((o) => o.e[C.fin] === f)).filter(Boolean);
    if (!sel.length) return;
    const head = ['finess', 'nom', 'adresse', 'cp', 'commune', 'telephone', 'distance_km',
      'tarif_mois', 'reste_a_charge_mois', 'habilitation_ash', 'statut_etablissement', 'note_has',
      'etat_demarche', 'note'];
    const lignes = sel.map((o) => {
      const e = o.e, d = dem(e[C.fin]);
      return [e[C.fin], nom(e), e[C.adr] || '', e[C.cp], e[C.ville], e[C.tel] || '', o.dist.toFixed(1),
        o.r.prixConnu ? Math.round(o.r.total) : '', o.r.prixConnu && perso() ? Math.round(o.r.rac) : '',
        ASH_ETAT[e[C.ash]] ? ASH_ETAT[e[C.ash]].txt : 'non publiée',
        e[C.statut] != null ? STATUTS[e[C.statut]] : '', e[C.hasN] || '',
        LIB_STATUT(d.s), d.n];
    });
    telecharge([head, ...lignes], `demarches-${state.dossier ? state.dossier.replace(/[^\w-]+/g, '-') : 'ehpad'}.csv`);
    evt('pro_export_csv', { total: sel.length, type: 'demarches' });
  }

  /** Neutralise l'injection de formule : un tableur exécute toute cellule commençant
      par =, +, - ou @, ainsi que par une tabulation ou un retour chariot. Le préfixe
      apostrophe force l'interprétation en texte, sans changer ce que l'utilisateur lit. */
  function celluleCsv(v) {
    let t = v === null || v === undefined ? '' : String(v);
    if (/^[=+\-@\t\r]/.test(t)) t = "'" + t;
    return '"' + t.replace(/"/g, '""') + '"';
  }
  /** En-tête de provenance : un export daté, versionné et rejouable. */
  function enteteExport() {
    const s = state;
    return [
      ['# trouver-mon-ehpad.fr — export du ' + new Date().toLocaleString('fr-FR')],
      ['# Données : version ' + META.version + ', barèmes vérifiés le ' + dfr(META.lastVerified)
        + (window.COUVERTURE ? ', couverture mesurée le ' + dfr(window.COUVERTURE.date) : '')],
      ['# Recherche : ' + (s.commune ? s.commune.nom + ' (' + s.commune.cp + ')' : s.cp || 'non précisée')
        + ', rayon ' + s.rayon + ' km, tri « ' + s.tri + ' »'],
      ['# Montants calculés avec un mois moyen de ' + String(M()).replace('.', ',') + ' jours. '
        + 'Ils dépendent de la situation saisie et ne valent pas devis.'],
      [''],
    ];
  }
  function telecharge(lignes, nomFichier) {
    const csv = enteteExport().concat(lignes)
      .map((l) => l.map(celluleCsv).join(';')).join('\r\n');
    const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url; a.download = nomFichier;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  /* ---------- Feuille de route ---------- */
  function routeHtml(list, s) {
    const keys = ['gir', 'apa', 'via', 'apl'];
    const habilites = list.filter((o) => o.e[C.ash] === 1 || o.e[C.ash] === 2).length;
    const rouge = list.filter((o) => o.r.prixConnu && o.r.couleur === 'rouge').length;
    if (habilites && (rouge > 0 || s.ashOnly)) keys.push('ash');
    if (s.imposable || s.enfants > 0) keys.push('impot');
    keys.push('contrat');
    if (s.proprietaire) keys.push('logement');
    if (s.mode === 'pro') keys.push('pro');
    return keys.map((k, i) => {
      const rm = ROADMAPS[k];
      return `<article class="step">
        <div class="step-h"><span class="n">${i + 1}</span><h3>${esc(rm.title)}</h3></div>
        <p class="quand">Quand ? ${esc(rm.when)}</p>
        <div class="step-g">
          <div><p class="lbl">Les étapes</p><ol>${rm.steps.map((x) => `<li>${esc(x)}</li>`).join('')}</ol></div>
          <div><p class="lbl">Les pièces à préparer</p><ul>${rm.docs.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>
        </div>
        ${rm.checklist ? `<details class="chk"><summary>Les questions à poser pendant la visite (à imprimer)</summary><ul>${rm.checklist.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></details>` : ''}
        ${rm.warnings.length ? `<div class="piege">${rm.warnings.map(esc).join('<br>')}</div>` : ''}
      </article>`;
    }).join('');
  }

  /* ---------- Partage ---------- */
  /* Ce qui décrit la RECHERCHE : où, dans quel rayon, avec quels filtres.
     Rien ici ne renseigne sur l'argent ni sur la santé de qui que ce soit. */
  const PARTAGE_RECHERCHE = ['mode', 'pourQui', 'cp', 'rayon', 'chambre', 'tri',
    'ashOnly', 'hasAB', 'tempOnly', 'prixConnu'];
  /* Ce qui décrit la SITUATION : ressources, épargne, fiscalité, niveau d'autonomie.
     Un GIR est une donnée de santé. Ces champs ne partent que sur demande explicite. */
  const PARTAGE_SITUATION = ['gir', 'revenus', 'autres', 'epargne', 'proprietaire', 'couple',
    'conjointDomicile', 'deuxResidents', 'revenusConjoint', 'aideLogement', 'imposable', 'enfants', 'tmi'];
  const PARTAGE = PARTAGE_RECHERCHE.concat(PARTAGE_SITUATION);   // lecture d'un lien : on accepte tout
  /** @param {boolean} avecSituation joindre la situation financière et le GIR.
      Le lien n'est pas chiffré : son contenu est lisible par quiconque le reçoit. */
  function lienPartage(avecSituation) {
    const o = {};
    const champs = avecSituation ? PARTAGE : PARTAGE_RECHERCHE;
    champs.forEach((k) => { const v = state[k]; if (v !== null && v !== undefined && !(typeof v === 'number' && !Number.isFinite(v))) o[k] = v; });
    if (state.commune) o.i = state.commune.insee;
    const s = btoa(unescape(encodeURIComponent(JSON.stringify(o))));
    return location.origin + location.pathname + '#s=' + s;
  }
  let cible = null;                 // établissement à mettre en avant après le premier rendu
  async function litHash() {
    const m = /#s=([^&]+)/.exec(location.hash || '');
    if (!m) return false;
    try {
      const o = JSON.parse(decodeURIComponent(escape(atob(m[1]))));
      PARTAGE.forEach((k) => { if (k in o) state[k] = o[k]; });
      // « f » : arrivée depuis la fiche d'un établissement — il est mis en comparaison et mis en avant.
      if (o.f) { state.compare = [String(o.f)]; cible = String(o.f); }
      if (o.cp) {
        const list = await chercheCommunes(o.cp);
        state.commune = (o.i && list.find((c) => c.insee === o.i)) || list[0] || null;
      }
      return true;
    } catch (e) { return false; }
  }

  /* ---------- Rendu principal ---------- */
  let dernier = [];
  let derniereCle = '';

  function cleResultat(s) {
    return [s.commune && s.commune.insee, s.rayon, s.tri, s.ashOnly, s.ashConfirmer, s.hasAB, s.tempOnly,
      s.prixConnu, s.favorisOnly, s.statuts[0], s.statuts[1], s.statuts[2]].join('|');
  }

  async function render() {
    sauve();
    const s = state;
    majUI();
    const pret = !!s.commune;
    $('resultats').hidden = !pret; $('vide').hidden = pret;
    document.body.classList.toggle('explore', pret);
    $('route-wrap').hidden = !pret; $('route-vide').hidden = pret;
    if (!pret) return;

    const t0 = performance.now();
    $('liste').setAttribute('aria-busy', 'true');
    const brut = await chercher(s);
    const list = trie(filtre(brut, s), s);
    const cle = cleResultat(s);
    if (cle !== derniereCle) {
      state.nbAffiches = 15; derniereCle = cle;
      evt('search_completed', { commune: s.commune.insee, rayon: s.rayon, resultats: list.length });
    }
    dernier = list;

    majSegVue();
    const p = perso();
    const avecPrix = list.filter((o) => o.r.prixConnu);
    const val = (o) => (p ? o.r.rac : o.r.total);
    const med = avecPrix.length ? avecPrix.map(val).sort((a, b) => a - b)[Math.floor(avecPrix.length / 2)] : null;
    const mini = avecPrix.length ? Math.min(...avecPrix.map(val)) : null;
    const maxi = avecPrix.length ? Math.max(...avecPrix.map(val)) : null;
    const rouges = p ? avecPrix.filter((o) => o.r.couleur === 'rouge').length : 0;

    $('res-titre').textContent = `${list.length} EHPAD à ${s.rayon} km ${de(s.commune.nom)}`;
    $('res-chiffre').textContent = med != null ? euro(med) : '—';
    $('res-sous').innerHTML = med == null
      ? 'aucun établissement de cette sélection n’a déclaré son tarif'
      : p
        ? `reste à charge médian pour ${mot('titre')} · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois${rouges ? ` · <b>${rouges}</b> hors de portée sans aide sociale ni aide de la famille` : ''}`
        : `tarif médian, avant les aides · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois · <b>indiquez ${mot('retraite')}</b> pour voir ce qui resterait à payer`;
    $('res-recap').textContent = recapTexte(s);
    $('action-rouge').hidden = !(rouges > 0 && !s.ashOnly);
    $('barre-n').textContent = list.length
      ? `${list.length} établissement${list.length > 1 ? 's' : ''}${list.length > state.nbAffiches ? ` · ${Math.min(state.nbAffiches, list.length)} affichés` : ''}`
      : 'aucun résultat';

    dessineCarte(list, s);
    majListe(list, s);
    majChips();
    $('contexte').innerHTML = contexteDept(depDeInsee(s.commune.insee), s.commune.insee);
    $('route').innerHTML = routeHtml(list, s);
    majCompare();
    if (state.selection && !list.some((o) => o.e[C.fin] === state.selection)) ferme();
    else if (state.selection) majFiche();
    $('perf').textContent = (performance.now() - t0).toFixed(0) + ' ms';
    $('export-btn').hidden = s.mode !== 'pro';
  }

  function majListe(list, s) {
    const n = $('liste');
    if (!list.length) { n.innerHTML = videHtml(s); n.setAttribute('aria-busy', 'false'); $('plus-btn').hidden = true; return; }
    const vus = list.slice(0, state.nbAffiches);
    n.innerHTML = vus.map((o, i) => res(o, s, i)).join('');
    n.setAttribute('aria-busy', 'false');
    const reste = list.length - vus.length;
    const b = $('plus-btn');
    b.hidden = reste <= 0;
    if (reste > 0) b.textContent = `Afficher ${Math.min(15, reste)} établissement${Math.min(15, reste) > 1 ? 's' : ''} de plus (${reste} restant${reste > 1 ? 's' : ''})`;
  }

  /** État vide : on propose une sortie, jamais un cul-de-sac. */
  function videHtml(s) {
    const sorties = [];
    if (s.rayon < 60) sorties.push(`<button type="button" class="mini2" data-sortie="rayon">Élargir à ${s.rayon < 20 ? 20 : s.rayon < 40 ? 40 : 60} km</button>`);
    if (s.ashOnly) sorties.push('<button type="button" class="mini2" data-sortie="ash">Ne plus exiger l’aide sociale</button>');
    if (s.hasAB) sorties.push('<button type="button" class="mini2" data-sortie="has">Ne plus exiger une évaluation A ou B</button>');
    if (s.tempOnly) sorties.push('<button type="button" class="mini2" data-sortie="temp">Ne plus exiger l’accueil temporaire</button>');
    if (s.favorisOnly) sorties.push('<button type="button" class="mini2" data-sortie="fav">Afficher tous les établissements</button>');
    if (s.prixConnu) sorties.push('<button type="button" class="mini2" data-sortie="prix">Afficher aussi ceux sans tarif déclaré</button>');
    sorties.push('<button type="button" class="mini2" data-sortie="tout">Retirer tous les filtres</button>');
    return `<div class="vide"><p class="v-t">Aucun établissement ne correspond à ces critères</p>
      <p class="v-s">Voici comment élargir la recherche&nbsp;:</p>
      <div class="res-act" style="justify-content:center;flex-wrap:wrap">${sorties.join('')}</div></div>`;
  }

  function majChips() {
    const c = [];
    if (state.ashOnly) c.push(['ash', 'Aide sociale exigée']);
    if (!state.statuts[0]) c.push(['statut0', 'Sans le public']);
    if (!state.statuts[1]) c.push(['statut1', 'Sans l’associatif']);
    if (!state.statuts[2]) c.push(['statut2', 'Sans le privé commercial']);
    if (state.hasAB) c.push(['has', 'Évaluation A ou B']);
    if (state.tempOnly) c.push(['temp', 'Accueil temporaire']);
    if (state.prixConnu) c.push(['prix', 'Tarif déclaré seulement']);
    if (state.favorisOnly) c.push(['fav', 'Mes établissements gardés']);
    $('chips-actifs').innerHTML = c.map(([k, t]) => `<button type="button" data-sortie="${k}">${t} ×</button>`).join('');
    const fb = $('fav-btn');
    fb.hidden = !state.favoris.length;
    $('fav-n').textContent = state.favoris.length;
    fb.classList.toggle('on', state.favorisOnly);
    fb.setAttribute('aria-pressed', String(state.favorisOnly));
    fb.setAttribute('aria-label', state.favorisOnly ? 'Afficher tous les établissements' : 'Afficher seulement les établissements gardés');
    const n = $('filtres-n');
    n.hidden = !c.length; n.textContent = c.length;
  }

  /* ---------- Sélection d'un établissement ---------- */
  function selectionne(fin, opts) {
    opts = opts || {};
    const o = dernier.find((x) => x.e[C.fin] === fin);
    if (!o) return;
    const nouveau = state.selection !== fin;
    state.selection = fin;
    vue('fiche');
    majFiche();
    document.querySelectorAll('.res').forEach((el) => el.setAttribute('aria-current', String(el.dataset.fin === fin)));
    marqueSelection(fin);
    document.body.classList.add('sheet');
    if (nouveau && opts.push !== false) {
      try { history.pushState({ e: fin }, '', '#e=' + fin); } catch (e) {}
    }
    if (nouveau) evt('result_opened', { ehpad: fin, source: opts.source || 'liste' });
    sauve();
  }

  function ferme(opts) {
    state.selection = null;
    $('pan-fiche').hidden = true;
    $('pan-fiche').classList.remove('plein');
    document.body.classList.remove('sheet');
    document.querySelectorAll('.res').forEach((el) => el.setAttribute('aria-current', 'false'));
    Object.keys(MARQUEURS).forEach((k) => MARQUEURS[k].setStyle({ radius: 9, weight: 2, color: '#fff' }));
    vue('carte');
    majCompare();
    if (!(opts && opts.push === false) && /#e=/.test(location.hash)) {
      try { history.pushState({}, '', location.pathname + location.search); } catch (e) {}
    }
    sauve();
  }

  function majFiche() {
    const o = dernier.find((x) => x.e[C.fin] === state.selection);
    if (!o) { $('pan-fiche').hidden = true; return; }
    $('pan-fiche').hidden = false;
    $('fiche').innerHTML = ficheHtml(o, state);
    $('fiche').scrollTop = 0;
  }

  function vue(v) {
    state.vue = v;
    $('atelier').dataset.vue = v;
    const fiche = v === 'fiche' && state.selection;
    $('pan-carte').hidden = !!fiche && window.matchMedia('(min-width:1040px)').matches;
    $('pan-fiche').hidden = !fiche;
    majSegVue();
    if (v === 'carte' && map) setTimeout(() => map.invalidateSize(), 60);
  }
  /** Le bouton allumé est celui du panneau réellement affiché — y compris au premier rendu,
      où personne n'avait encore cliqué et où les deux boutons restaient éteints. */
  function majSegVue() {
    const v = state.vue === 'fiche' && state.selection ? 'fiche' : 'carte';
    document.querySelectorAll('[data-vue-seg] button').forEach((b) => {
      const on = b.dataset.vue === v;
      b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
    });
  }

  /* ---------- Comparateur : barre et tiroir ---------- */
  function majCompare() {
    const n = state.compare.length, p = pro();
    $('cmp-barre').hidden = !n || !!state.selection && !window.matchMedia('(min-width:1040px)').matches;
    $('cmp-n').textContent = p
      ? (n === 1 ? '1 établissement dans ma liste' : `${n} établissements dans ma liste`)
      : (n === 1 ? '1 établissement sélectionné' : `${n} établissements sélectionnés`);
    $('cmp-ouvrir').textContent = p ? 'Voir mes démarches' : 'Comparer';
    $('cmp-titre').textContent = p ? 'Ma liste de démarches' : 'Ma comparaison';
    $('cmp-export').hidden = !p;
    $('cmp-plus').hidden = p;
    document.querySelector('#cmp-diff').closest('.chk-l').hidden = p;
    if (!$('cmp-drawer').hidden) $('comparaison').innerHTML = comparHtml();
    document.querySelectorAll('[data-cmp]').forEach((b) => {
      const on = state.compare.indexOf(b.dataset.cmp) >= 0;
      b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
      if (b.classList.contains('mini2')) b.textContent = libCmp(on);
    });
    document.querySelectorAll('#liste .res').forEach(majDemCarte);
  }
  function bascule(fin) {
    const i = state.compare.indexOf(fin);
    if (i >= 0) state.compare.splice(i, 1);
    else {
      if (state.compare.length >= MAX_SEL()) state.compare.shift();
      state.compare.push(fin);
      if (pro()) { dem(fin); evt('pro_add_to_action_list', { ehpad: fin, total: state.compare.length }); }
      else evt('ehpad_compared', { ehpad: fin, total: state.compare.length });
    }
    majCompare();
    if (state.selection === fin) majFiche();
    sauve();
  }
  function basculeFav(fin) {
    const i = state.favoris.indexOf(fin);
    if (i >= 0) state.favoris.splice(i, 1);
    else { state.favoris.push(fin); evt('favorite_added', { ehpad: fin }); }
    document.querySelectorAll('[data-fav="' + fin + '"]').forEach((b) => {
      const on = state.favoris.indexOf(fin) >= 0;
      b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
      b.textContent = on ? '♥ Gardé' : '♡ Garder';
    });
    majChips();
    sauve();
  }

  /* ---------- Export CSV ---------- */
  function exportCsv() {
    const head = ['finess', 'nom', 'adresse', 'cp', 'commune', 'telephone', 'distance_km', 'prix_heberg_jour',
      'date_maj_prix', 'evolution_prix_%', 'habilitation_ash', 'statut', 'tarif_soins', 'note_has',
      'criteres_imperatifs_18', 'hygiene', 'a_decaisser_mois', 'apa_mois', 'occupation_moyenne_du_segment_%',
      'regime_dependance'];
    const lignes = dernier.map((o) => [o.e[C.fin], nom(o.e), o.e[C.adr] || '', o.e[C.cp], o.e[C.ville], o.e[C.tel] || '',
      o.dist.toFixed(1), o.r.pj ?? '', o.e[C.maj] || '', o.prix ? o.prix.e : '',
      ASH_ETAT[o.e[C.ash]] ? ASH_ETAT[o.e[C.ash]].txt : 'inconnu',
      o.e[C.statut] != null ? STATUTS[o.e[C.statut]] : '', o.e[C.tarif] || '', o.e[C.hasN] || '',
      o.e[C.hasCI] != null ? o.e[C.hasCI] : '', o.e[C.alim] ? o.e[C.alim][0] : '',
      o.r.prixConnu ? Math.round(o.r.decaisse) : '', o.r.apaConnue ? Math.round(o.r.apa) : '',
      o.r.secteur ? o.r.secteur.occ : '', o.r.reg]);
    telecharge([head, ...lignes], `ehpad-${state.commune ? state.commune.cp : 'selection'}-${state.rayon}km.csv`);
  }

  /* ---------- Autocomplétion ---------- */
  const cpInput = $('cp'), dd = $('cp-dd');
  async function chercheCommunes(v) {
    const deps = depsForCp(v);
    await Promise.all(deps.map((d) => loadDep('c', d)));
    const out = [];
    for (const d of deps) for (const c of COMMUNES[d] || []) if (c[0] === v) out.push({ cp: c[0], nom: c[1], lat: c[2], lon: c[3], insee: c[4] });
    return out;
  }
  function montre(list) {
    if (!list.length) { dd.hidden = true; return; }
    dd.innerHTML = list.map((c, i) => `<button type="button" data-i="${i}">${esc(c.nom)} <span class="muted">${c.cp}</span></button>`).join('');
    dd.hidden = false; dd._list = list;
  }
  cpInput.addEventListener('input', async () => {
    const v = cpInput.value.replace(/\D/g, '').slice(0, 5);
    cpInput.value = v; state.cp = v; state.commune = null; $('commune').textContent = '';
    if (v.length === 5) {
      const list = await chercheCommunes(v);
      if (list.length === 1) { state.commune = list[0]; dd.hidden = true; $('commune').textContent = list[0].nom; }
      else if (list.length) { $('commune').textContent = 'Choisissez votre commune ↓'; montre(list); }
      else { $('commune').textContent = 'Code postal inconnu'; dd.hidden = true; }
    } else dd.hidden = true;
    render();
  });
  dd.addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    state.commune = dd._list[+b.dataset.i]; dd.hidden = true; $('commune').textContent = state.commune.nom; render();
  });
  document.addEventListener('click', (e) => { if (!dd.contains(e.target) && e.target !== cpInput) dd.hidden = true; });

  /* ---------- Persistance ---------- */
  const KEY = 'mon_ehpad_state_v2';
  function sauve() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function charge() {
    try {
      const raw = localStorage.getItem(KEY); if (!raw) return false;
      const s = JSON.parse(raw); if (!s || typeof s !== 'object') return false;
      for (const k of Object.keys(state)) if (k in s && k !== 'commune') state[k] = s[k];
      state.commune = s.commune && s.commune.lat ? s.commune : null;
      return true;
    } catch (e) { return false; }
  }


  /* ---------- Mode professionnel : les recherches enregistrées ---------- */
  /* Tout reste dans ce navigateur. On n'enregistre ni ressources, ni identité :
     la zone, la distance, les critères de recherche et la liste de démarches, rien d'autre. */
  const KEY_DOS = 'mon_ehpad_dossiers_v1';
  const DOSSIER_CLES = ['cp', 'commune', 'rayon', 'gir', 'chambre', 'besoinAsh', 'ashConfirmer',
    'hasAB', 'tempOnly', 'prixConnu', 'statuts', 'priorite', 'tri', 'favoris'];
  const MAX_DOS = 20;

  function litDossiers() {
    try {
      const l = JSON.parse(localStorage.getItem(KEY_DOS) || '[]');
      return Array.isArray(l) ? l : [];
    } catch (e) { return []; }
  }
  function ecritDossiers(l) {
    try { localStorage.setItem(KEY_DOS, JSON.stringify(l.slice(0, MAX_DOS))); return true; } catch (e) { return false; }
  }
  /** « Dossier 001 », « Dossier 002 »… : un repère de travail, jamais le nom d'une personne. */
  function nomParDefaut(l) {
    let n = 1;
    const pris = new Set(l.map((d) => d.nom));
    while (pris.has('Dossier ' + String(n).padStart(3, '0'))) n++;
    return 'Dossier ' + String(n).padStart(3, '0');
  }
  function majDossiers() {
    const l = litDossiers(), box = $('dossiers-liste');
    if (!box) return;
    $('dossiers-n').textContent = l.length
      ? (l.length === 1 ? '1 recherche sur cet appareil' : `${l.length} recherches sur cet appareil`)
      : 'aucune recherche enregistrée';
    box.innerHTML = l.length ? l.map((d) => `<div class="dos">
        <div>
          <p class="dos-n">${esc(d.nom)}</p>
          <p class="dos-m">${esc(d.zone || 'zone non précisée')} · ${d.n || 0} démarche${(d.n || 0) > 1 ? 's' : ''} · ${esc(d.date || '')}</p>
        </div>
        <div class="dos-a">
          <button type="button" class="mini2" data-dos-ouvre="${esc(d.id)}">Reprendre</button>
          <button type="button" class="lien" data-dos-supp="${esc(d.id)}">Supprimer</button>
        </div>
      </div>`).join('')
      : '<p class="vide">Aucune recherche enregistrée sur cet appareil. Enregistrez la recherche en cours pour la retrouver plus tard — sur ce navigateur uniquement.</p>';
    const champ = $('dossier-nom');
    if (champ && !champ.value) champ.placeholder = nomParDefaut(l);
  }
  function majLigneDossier() {
    const el = $('pro-dossier');
    if (el) el.textContent = state.dossier ? `Recherche en cours : « ${state.dossier} ».` : 'Aucune recherche enregistrée ouverte.';
  }
  function enregistreDossier() {
    const champ = $('dossier-nom'), l = litDossiers();
    const nomD = (champ.value || '').trim() || nomParDefaut(l);
    const etat = {};
    DOSSIER_CLES.forEach((k) => (etat[k] = state[k]));
    const i = l.findIndex((d) => d.nom === nomD);
    const enr = {
      id: (i >= 0 ? l[i].id : 'd' + Date.now().toString(36)),
      nom: nomD,
      zone: state.commune ? state.commune.nom + ' · ' + state.rayon + ' km' : '',
      n: state.compare.length,
      date: new Date().toLocaleDateString('fr-FR'),
      etat, compare: state.compare.slice(), demarche: JSON.parse(JSON.stringify(state.demarche)),
    };
    if (i >= 0) l[i] = enr; else l.unshift(enr);
    if (!ecritDossiers(l)) {
      $('dossiers-n').textContent = 'enregistrement impossible : le stockage de ce navigateur est plein ou désactivé';
      return;
    }
    state.dossier = nomD;
    champ.value = '';
    majDossiers(); majLigneDossier(); sauve();
    evt('pro_research_saved', { demarches: enr.n, remplace: i >= 0 });
  }
  async function ouvreDossier(id) {
    const d = litDossiers().find((x) => x.id === id);
    if (!d) return;
    Object.keys(d.etat || {}).forEach((k) => { if (k in state) state[k] = d.etat[k]; });
    state.gir = String(state.gir);
    state.compare = Array.isArray(d.compare) ? d.compare.slice() : [];
    state.demarche = d.demarche && typeof d.demarche === 'object' ? d.demarche : {};
    state.dossier = d.nom;
    state.selection = null; state.nbAffiches = 15;
    if (state.commune) { cpInput.value = state.commune.cp; $('commune').textContent = state.commune.nom; }
    else if (state.cp) cpInput.value = state.cp;
    $('rayon').value = String(state.rayon);
    if ($('rayon2')) $('rayon2').value = String(state.rayon);
    ouvreDrawer('drawer-dossiers', false);
    majLigneDossier();
    evt('pro_research_reopened', { demarches: state.compare.length });
    await render();
    majCompare();
    $('bande-carte').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function supprimeDossier(id) {
    const l = litDossiers(), d = l.find((x) => x.id === id);
    ecritDossiers(l.filter((x) => x.id !== id));
    if (d && state.dossier === d.nom) { state.dossier = null; majLigneDossier(); sauve(); }
    majDossiers();
  }

  /** Bascule famille ↔ professionnel. Rien n'est perdu : les deux parcours partagent les mêmes calculs. */
  function passeEnPro(on, source) {
    if (state.mode === (on ? 'pro' : 'famille')) return;
    state.mode = on ? 'pro' : 'famille';
    if (!on) { state.dossier = null; }
    if (on) evt('pro_landing_view', { source: source || 'lien' });
    if (state.compare.length > MAX_SEL()) state.compare = state.compare.slice(-MAX_SEL());
    majLigneDossier(); majCompare(); sauve();
    render();
  }

  /* ---------- Interface ---------- */
  /** Deux réponses ne peuvent pas coexister : on les remet d’accord avant tout calcul. */
  function normalise() {
    if (!state.couple) { state.deuxResidents = false; state.conjointDomicile = false; }
    if (state.deuxResidents) state.conjointDomicile = false;
    state.ashOnly = state.besoinAsh === 'oui';
    if (state.priorite === 'ash') { state.tri = 'rac'; state.besoinAsh = 'oui'; state.ashOnly = true; }
    else if (state.priorite) state.tri = state.priorite;
  }

  /* Le titre parle à celui qui est là : une famille, ou un professionnel qui accompagne.
     Le HTML livré porte la version famille — c'est elle qui est indexée. */
  // pas de <br> forcé ici : la coupure dépend de la largeur, « text-wrap:balance » équilibre les lignes
  const H1_PRO = 'Trouvez les EHPAD <em class="bl">adaptés</em> aux personnes que vous <em class="co">accompagnez</em>.';
  const SUB_PRO = 'Identifiez rapidement les établissements compatibles avec le budget, la localisation et les aides disponibles, puis constituez votre liste de démarches.<br><span class="sub2">Les calculs sont ceux du parcours famille&nbsp;: reste à charge réel, APA, aide sociale à l’hébergement, habilitation, évolution du prix depuis 2018.</span>';
  const h1El = document.querySelector('header h1'), subEl = document.querySelector('header .sub');
  const H1_FAM = h1El ? h1El.innerHTML : '', SUB_FAM = subEl ? subEl.innerHTML : '';
  function majTitre() {
    if (!h1El || !subEl) return;
    const p = state.mode === 'pro';
    const h = p ? H1_PRO : H1_FAM, b = p ? SUB_PRO : SUB_FAM;
    h1El.classList.toggle('h1-pro', p);   // le titre professionnel est plus long : un cran plus petit
    if (h1El.innerHTML !== h) h1El.innerHTML = h;
    if (subEl.innerHTML !== b) subEl.innerHTML = b;
  }

  function majUI() {
    normalise();
    const fd = $('fld-deuxres'), fc = $('fld-conjoint');
    if (fd) fd.hidden = !state.couple;
    if (fc) fc.hidden = !state.couple || state.deuxResidents;
    const frc = $('fld-revconj');
    if (frc) frc.hidden = !state.couple;
    document.querySelectorAll('[data-mode]').forEach((el) => { el.hidden = el.dataset.mode !== state.mode; });
    $('bande-situation').classList.toggle('pro', state.mode === 'pro');
    majTitre();
    document.querySelectorAll('[data-seg]').forEach((seg) => {
      const [key, liste] = seg.dataset.seg.split(':');
      const vals = liste.split(',');
      seg.querySelectorAll('button').forEach((b, i) => {
        const on = state[key] === cast(vals[i]);
        b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
      });
    });
    majPourQui();
    $('gir-aide').hidden = state.gir !== '?';
    $('fam-detail').hidden = !(state.enfants > 0);
    $('ash-aide').hidden = state.besoinAsh !== 'nsp';
    $('tri').value = state.tri;
    if ($('rayon2')) $('rayon2').value = String(state.rayon);
    $('rayon').value = String(state.rayon);
    document.querySelectorAll('[data-check]').forEach((el) => {
      const k = el.dataset.check;
      el.checked = k.startsWith('statut') ? !!state.statuts[+k.slice(6)] : !!state[k];
    });
  }

  // jamais de conversion numérique : « 12 » est un code de GIR, pas un nombre
  const cast = (v) => (v === 'true' ? true : v === 'false' ? false : v);
  const CLES_FILTRE = { besoinAsh: 1, priorite: 1 };
  document.querySelectorAll('[data-seg]').forEach((seg) => {
    const [key, liste] = seg.dataset.seg.split(':');
    const vals = liste.split(',');
    seg.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      state[key] = cast(vals[[...seg.querySelectorAll('button')].indexOf(b)]);
      if (CLES_FILTRE[key]) { state.nbAffiches = 15; evt('filters_applied', { critere: key, valeur: String(state[key]) }); }
      render();
    });
  });
  const num = (id, key, def) => $(id).addEventListener('input', (e) => {
    const v = parseFloat(String(e.target.value).replace(/[\s ]/g, '').replace(',', '.'));
    state[key] = Number.isFinite(v) ? v : (def === undefined ? NaN : def);
    if (key === 'revenus' && perso() && !dejaCalcule) { dejaCalcule = true; evt('calculator_completed', {}); }
    render();
  });
  let dejaCalcule = false;
  num('revenus', 'revenus'); num('autres', 'autres', 0); num('epargne', 'epargne'); num('apl', 'aideLogement', 0);
  if ($('revconj')) num('revconj', 'revenusConjoint', 0);
  ['rayon', 'rayon2', 'tri', 'tmi', 'enfants'].forEach((id) => $(id) && $(id).addEventListener('change', (e) => {
    if (id === 'rayon2') { state.rayon = +e.target.value; state.nbAffiches = 15; render(); return; }
    if (id === 'tri') { state.tri = e.target.value; state.priorite = null; state.nbAffiches = 15; }
    else state[id] = +e.target.value;
    if (id === 'rayon') state.nbAffiches = 15;
    render();
  }));
  document.querySelectorAll('[data-check]').forEach((el) => el.addEventListener('change', () => {
    const k = el.dataset.check;
    if (k.startsWith('statut')) state.statuts[+k.slice(6)] = el.checked;
    else state[k] = el.checked;
    state.nbAffiches = 15;
    evt('filters_applied', { critere: k, valeur: String(el.checked) });
    render();
  }));

  /* ---------- Clics : une seule délégation pour tout l'espace de travail ---------- */
  document.addEventListener('click', (e) => {
    const t = e.target;
    const fermer = t.closest('[data-fermer]');
    if (fermer) { ferme(); return; }
    const cmp = t.closest('[data-cmp]');
    if (cmp) { e.stopPropagation(); bascule(cmp.dataset.cmp); return; }
    const fav = t.closest('[data-fav]');
    if (fav) { e.stopPropagation(); basculeFav(fav.dataset.fav); return; }
    const del = t.closest('[data-del]');
    if (del) { bascule(del.dataset.del); return; }
    const voir = t.closest('[data-voir]');
    if (voir) { e.stopPropagation(); selectionne(voir.dataset.voir); return; }
    const onglet = t.closest('[data-onglet]');
    if (onglet) { ongletActif = onglet.dataset.onglet; majFiche(); return; }
    const modif = t.closest('[data-modif]');
    if (modif) {
      evt('calculator_started', {});
      const p = $('plus-situation'); if (p) p.open = true;
      $('revenus').focus();
      $('bande-situation').scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    const sortie = t.closest('[data-sortie]');
    if (sortie) { elargit(sortie.dataset.sortie); return; }
    // Le lien téléphone vit dans une carte cliquable : sans cette interception,
    // le clic composerait le numéro ET ouvrirait la fiche derrière.
    const tel = t.closest('[data-tel]');
    if (tel) { e.stopPropagation(); evt('tel_clicked', {}); return; }
    const carte = t.closest('.res');
    if (carte) { selectionne(carte.dataset.fin); return; }
  });
  $('liste').addEventListener('keydown', (e) => {
    const c = e.target.closest('.res');
    if (!c) return;
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectionne(c.dataset.fin); }
  });
  $('liste').addEventListener('mouseover', (e) => { const c = e.target.closest('.res'); if (c) survole(c.dataset.fin, true); });
  $('liste').addEventListener('mouseout', (e) => { const c = e.target.closest('.res'); if (c) survole(c.dataset.fin, false); });

  /** Sortir d'une impasse ou retirer un filtre depuis une pastille. */
  function elargit(k) {
    if (k === 'rayon') state.rayon = state.rayon < 20 ? 20 : state.rayon < 40 ? 40 : 60;
    if (k === 'ash') { state.besoinAsh = 'non'; state.ashOnly = false; if (state.priorite === 'ash') state.priorite = null; }
    if (k === 'has') state.hasAB = false;
    if (k === 'temp') state.tempOnly = false;
    if (k === 'fav') state.favorisOnly = false;
    if (k === 'prix') state.prixConnu = false;
    if (k.startsWith('statut')) state.statuts[+k.slice(6)] = true;
    if (k === 'tout') {
      state.besoinAsh = 'nsp'; state.ashOnly = false; state.hasAB = false; state.tempOnly = false;
      state.favorisOnly = false; state.prixConnu = false; state.statuts = { 0: true, 1: true, 2: true };
      if (state.priorite === 'ash') state.priorite = null;
    }
    state.nbAffiches = 15;
    render();
  }

  /* ---------- Boutons de l'espace de travail ---------- */
  $('zone-btn').addEventListener('click', chercheZone);
  $('plus-btn').addEventListener('click', () => {
    state.nbAffiches += 15;
    evt('result_list_more', { affiches: state.nbAffiches });
    majListe(dernier, state);
    $('barre-n').textContent = `${dernier.length} établissements · ${Math.min(state.nbAffiches, dernier.length)} affichés`;
  });
  document.querySelectorAll('[data-vue-seg] button').forEach((b) => b.addEventListener('click', () => {
    if (b.dataset.vue === 'fiche' && !state.selection) {
      if (dernier.length) selectionne(dernier[0].e[C.fin], { source: 'onglet' });
      return;
    }
    vue(b.dataset.vue);
    if (b.dataset.vue === 'carte') evt('map_opened', {});
  }));
  function ouvreDrawer(id, ouvrir) {
    $(id).hidden = !ouvrir;
    document.body.classList.toggle('fige', ouvrir);
    if (ouvrir) { const f = $(id).querySelector('button, input'); if (f) f.focus(); }
  }
  $('fav-btn').addEventListener('click', () => {
    state.favorisOnly = !state.favorisOnly; state.nbAffiches = 15;
    evt('filters_applied', { critere: 'favoris', valeur: String(state.favorisOnly) });
    render();
  });
  $('filtres-btn').addEventListener('click', () => { ouvreDrawer('drawer-filtres', true); $('filtres-btn').setAttribute('aria-expanded', 'true'); });
  $('drawer-close').addEventListener('click', () => { ouvreDrawer('drawer-filtres', false); $('filtres-btn').setAttribute('aria-expanded', 'false'); $('filtres-btn').focus(); });
  $('filtres-ok').addEventListener('click', () => { ouvreDrawer('drawer-filtres', false); $('filtres-btn').setAttribute('aria-expanded', 'false'); });
  $('filtres-reset').addEventListener('click', () => { elargit('tout'); });
  $('drawer-filtres').addEventListener('click', (e) => { if (e.target === $('drawer-filtres')) ouvreDrawer('drawer-filtres', false); });

  $('cmp-ouvrir').addEventListener('click', () => {
    $('comparaison').innerHTML = comparHtml();
    ouvreDrawer('cmp-drawer', true);
    evt('comparison_opened', { total: state.compare.length });
  });
  $('cmp-close').addEventListener('click', () => ouvreDrawer('cmp-drawer', false));
  $('cmp-drawer').addEventListener('click', (e) => { if (e.target === $('cmp-drawer')) ouvreDrawer('cmp-drawer', false); });
  $('cmp-vider').addEventListener('click', () => { state.compare = []; majCompare(); render(); });
  $('cmp-diff').addEventListener('change', (e) => { state.cmpDiff = e.target.checked; $('comparaison').innerHTML = comparHtml(); });
  $('cmp-plus').addEventListener('click', () => {
    state.cmpPlus = !state.cmpPlus;
    $('cmp-plus').textContent = state.cmpPlus ? 'Voir seulement l’essentiel' : 'Voir toutes les caractéristiques';
    $('comparaison').innerHTML = comparHtml();
  });


  /* ---------- Mode professionnel : commandes ---------- */
  $('pro-quitter').addEventListener('click', () => passeEnPro(false));
  $('dossiers-btn').addEventListener('click', () => { majDossiers(); ouvreDrawer('drawer-dossiers', true); });
  $('dossiers-close').addEventListener('click', () => { ouvreDrawer('drawer-dossiers', false); $('dossiers-btn').focus(); });
  $('dossiers-ok').addEventListener('click', () => { ouvreDrawer('drawer-dossiers', false); $('dossiers-btn').focus(); });
  $('drawer-dossiers').addEventListener('click', (e) => { if (e.target === $('drawer-dossiers')) ouvreDrawer('drawer-dossiers', false); });
  $('dossier-enreg').addEventListener('click', enregistreDossier);
  $('dossiers-liste').addEventListener('click', (e) => {
    const o = e.target.closest('[data-dos-ouvre]');
    if (o) { ouvreDossier(o.dataset.dosOuvre); return; }
    const s = e.target.closest('[data-dos-supp]');
    if (s) supprimeDossier(s.dataset.dosSupp);
  });
  $('cmp-export').addEventListener('click', exportDemarches);

  // états et notes de la liste de démarches : écrits dans l'état, puis sur cet appareil uniquement
  $('comparaison').addEventListener('change', (e) => {
    const sel = e.target.closest('[data-statut]');
    if (!sel) return;
    dem(sel.dataset.statut).s = sel.value;
    sauve();
    const c = $('item-' + sel.dataset.statut); if (c) majDemCarte(c);
    if (state.selection === sel.dataset.statut) majFiche();
    evt('pro_action_status_changed', { ehpad: sel.dataset.statut, etat: sel.value });
  });
  $('comparaison').addEventListener('input', (e) => {
    const n = e.target.closest('[data-note]');
    if (!n) return;
    dem(n.dataset.note).n = n.value;
    sauve();
    const c = $('item-' + n.dataset.note); if (c) majDemCarte(c);
  });

  /* ---------- Panneau glissant (mobile) ---------- */
  (function sheet() {
    const el = $('pan-fiche'), poignee = $('sheet-poignee');
    if (!poignee) return;
    const basculePlein = () => el.classList.toggle('plein');
    poignee.addEventListener('click', basculePlein);
    poignee.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); basculePlein(); } });
    let y0 = null;
    poignee.addEventListener('pointerdown', (e) => { y0 = e.clientY; poignee.setPointerCapture(e.pointerId); });
    poignee.addEventListener('pointerup', (e) => {
      if (y0 == null) return;
      const dy = e.clientY - y0; y0 = null;
      if (dy < -40) el.classList.add('plein');
      else if (dy > 40) { if (el.classList.contains('plein')) el.classList.remove('plein'); else ferme(); }
    });
  })();

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (!$('cmp-drawer').hidden) { ouvreDrawer('cmp-drawer', false); return; }
    if (!$('drawer-dossiers').hidden) { ouvreDrawer('drawer-dossiers', false); $('dossiers-btn').focus(); return; }
    if (!$('drawer-filtres').hidden) { ouvreDrawer('drawer-filtres', false); $('filtres-btn').focus(); return; }
    if (state.selection) ferme();
  });
  window.addEventListener('popstate', () => {
    const m = /#e=([0-9A-Za-z]+)/.exec(location.hash || '');
    if (m) selectionne(m[1], { push: false });
    else if (state.selection) ferme({ push: false });
  });

  document.querySelectorAll('[data-print]').forEach((b) => b.addEventListener('click', () => window.print()));
  $('export-btn').addEventListener('click', exportCsv);
  $('reset-btn').addEventListener('click', () => { try { localStorage.removeItem(KEY); } catch (e) {} location.hash = ''; location.reload(); });
  $('share-btn').addEventListener('click', async () => {
    const avec = !!($('share-situation') && $('share-situation').checked);
    const url = lienPartage(avec);
    try { history.replaceState(null, '', url); } catch (e) {}
    let ok = false;
    try { await navigator.clipboard.writeText(url); ok = true; } catch (e) {}
    const quoi = avec
      ? 'Il contient la situation saisie — ressources, épargne, niveau d’autonomie — en clair : '
        + 'l’adresse est encodée, pas chiffrée. Ne l’envoyez qu’à des personnes concernées.'
      : 'Il rouvre la recherche (commune, rayon, filtres) sans aucune information sur les ressources '
        + `ni sur ${mot('autonomie')}.`;
    $('share-msg').textContent = (ok ? 'Lien copié. ' : 'Lien prêt dans la barre d’adresse. ') + quoi;
    $('share-msg').hidden = false;
    setTimeout(() => { $('share-msg').hidden = true; }, 14000);
  });
  $('action-rouge').addEventListener('click', () => {
    state.besoinAsh = 'oui'; state.ashOnly = true; state.nbAffiches = 15;
    evt('filters_applied', { critere: 'besoinAsh', valeur: 'oui' });
    render();
  });
  $('gir-calc').addEventListener('change', () => {
    const n = [...document.querySelectorAll('#gir-calc input:checked')].length;
    state.gir = n >= 3 ? '12' : n >= 1 ? '34' : '56';
    $('gir-res').textContent = `Estimation indicative : niveau d’autonomie GIR ${state.gir === '12' ? '1-2' : state.gir === '34' ? '3-4' : '5-6'}. Seul le niveau notifié par le département fait foi.`;
    render();
  });

  /* ---------- Initialisation ---------- */
  (async function init() {
    const partage = await litHash();
    if (!partage) charge();
    state.gir = String(state.gir);   // un état enregistré par une version antérieure pouvait contenir un nombre
    if (state.tri === 'marge' || state.priorite === 'marge') { state.tri = 'rac'; state.priorite = 'rac'; }   // tri retiré
    // entrée dans l'espace professionnel : depuis /professionnels/ (?pro=1) ou un lien #pro
    const demandePro = /(^|[?&])pro=1(&|$)/.test(location.search) || /(^|#)pro$/.test(location.hash || '');
    if (demandePro && state.mode !== 'pro') {
      state.mode = 'pro';
      evt('pro_landing_view', { source: location.search.indexOf('pro=1') >= 0 ? 'page-pro' : 'lien' });
    } else if (state.mode === 'pro') {
      evt('pro_landing_view', { source: 'reprise' });
    }
    if (state.compare.length > MAX_SEL()) state.compare = state.compare.slice(-MAX_SEL());
    majLigneDossier(); majDossiers();
    if (state.commune) { cpInput.value = state.commune.cp; $('commune').textContent = state.commune.nom; }
    else if (state.cp) cpInput.value = state.cp;
    if (Number.isFinite(state.revenus)) $('revenus').value = state.revenus;
    if (Number.isFinite(state.epargne)) $('epargne').value = state.epargne;
    if (state.autres) $('autres').value = state.autres;
    if (state.aideLogement) $('apl').value = state.aideLogement;
    if (state.revenusConjoint && $('revconj')) $('revconj').value = state.revenusConjoint;
    $('rayon').value = String(state.rayon); $('tri').value = state.tri;
    $('enfants').value = String(state.enfants); $('tmi').value = String(state.tmi);
    state.selection = null;                 // la fiche s'ouvre sur demande, jamais au chargement
    // si une précision a déjà été donnée, le bloc reste ouvert : rien ne se cache derrière un repli
    if (state.autres || state.epargne > 0 || state.aideLogement || state.couple || state.imposable
        || state.enfants > 0 || state.proprietaire || state.revenusConjoint) $('plus-situation').open = true;
    const d = META.lastVerified.split('-').reverse().join('/');
    document.querySelectorAll('.meta-date').forEach((el) => (el.textContent = d));
    $('seuil-inf').textContent = euro2(SEUILS.apaInf);
    $('seuil-sup').textContent = euro2(SEUILS.apaSup);
    $('sources').innerHTML = SOURCES.map((s) => `<article class="src-card">
        <h3>${esc(s.cat)}</h3><p>${esc(s.what)}</p>
        <p class="src-l"><span>Source :</span> <a href="${s.url}" target="_blank" rel="noopener">${esc(s.src)}</a></p>
        ${s.note ? `<p class="src-n">${esc(s.note)}</p>` : ''}
      </article>`).join('');
    $('non-simule').innerHTML = NON_SIMULE.map((x) => `<li><b>${esc(x.t)}</b> — ${esc(x.d)}</li>`).join('');
    majCouverture();
    $('infl-table').innerHTML = Object.keys(INFLATION).map((a) => `<tr><td>${a}</td><td>${pct(INFLATION[a], 1)}</td></tr>`).join('');
    if (state.commune) evt('search_started', { commune: state.commune.insee, rayon: state.rayon });
    await render();
    // arrivée depuis une fiche de ce site, ou retour sur un lien profond
    const m = /#e=([0-9A-Za-z]+)/.exec(location.hash || '');
    const vise = (m && m[1]) || cible;
    if (vise) {
      if (!dernier.some((o) => o.e[C.fin] === vise)) {
        // l'établissement visé est hors du rayon ou masqué par un filtre : on élargit une fois
        state.rayon = Math.max(state.rayon, 40);
        await render();
      }
      selectionne(vise, { push: false, source: 'lien' });
      const el = $('item-' + vise);
      if (el) el.scrollIntoView({ block: 'center' });
    }
  })();

  /** Réécrit les libellés de la page selon la personne concernée. Aucun calcul n'en dépend. */
  function majPourQui() {
    // Le titre change de tournure, pas seulement de mot : « coûtera vraiment à vous »
    // ne se dit pas. Deux phrases complètes, chacune correcte.
    const h1 = $('h1-titre');
    if (h1) {
      h1.innerHTML = pourMoi()
        ? 'Ce que l’EHPAD vous coûtera<br><span class="h1-l2"><em class="bl">vraiment</em>, <em class="co">chaque mois</em></span>'
        : 'Ce que l’EHPAD coûtera<br><span class="h1-l2"><em class="bl">vraiment</em> à <em class="co">votre parent</em></span>';
    }
    const t = {
      'lbl-revenus': pourMoi() ? 'Vos retraites et pensions' : 'Retraites et pensions du parent',
      'lbl-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',
      'nav-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',
      'lbl-gir': pourMoi() ? 'Votre niveau de dépendance (GIR)' : 'Niveau de dépendance (GIR)',
      'lbl-couple': pourMoi() ? 'Vivez-vous en couple ?' : 'Vit-il ou elle en couple ?',
      'lbl-proprio': pourMoi() ? 'Êtes-vous propriétaire de votre logement ?' : 'Est-il ou elle propriétaire de son logement ?',
    };
    Object.keys(t).forEach((id) => { const el = $(id); if (el) el.textContent = t[id]; });
    const v = $('v-s');
    if (v) v.textContent = 'Les établissements autour de vous s’affichent aussitôt. Indiquez ensuite '
      + (pourMoi() ? 'votre retraite' : 'la retraite de votre parent')
      + ' : chaque tarif devient le montant qui resterait réellement à payer.';
  }

  /** Ce que les données ne couvrent pas, dit en clair et recalculé à chaque build.
      Les chiffres viennent de window.COUVERTURE, réécrit par build/split_data_v2.py :
      aucun n'est saisi à la main, aucun ne peut donc se périmer en silence. */
  function majCouverture() {
    const el = $('couverture'), c = window.COUVERTURE;
    if (!el) return;
    if (!c) { el.innerHTML = '<li>Mesure de couverture indisponible pour cette version des données.</li>'; return; }
    const n = c.total, p = (x) => nbfr(+(100 * x / n).toFixed(1)) + ' %';
    const l = [];
    l.push(['Prix d’hébergement', `${nbfr(n - c.prix)} établissements sur ${nbfr(n)} (${p(n - c.prix)}) n’ont déclaré aucun prix. Pour eux, aucun reste à charge n’est calculé.`]);
    l.push(['Tarif de l’aide au quotidien', `${nbfr(n - c.dependance)} établissements (${p(n - c.dependance)}) n’ont pas déclaré de tarif dépendance. Leur facture affichée est incomplète, et le dit.`]);
    l.push(['Évaluation de qualité', `${nbfr(n - c.has)} établissements (${p(n - c.has)}) n’ont pas d’évaluation publiée par la Haute Autorité de santé. Cela ne dit rien de leur qualité.`]);
    l.push(['Nombre de places', `${nbfr(n - c.capacite)} établissements (${p(n - c.capacite)}) n’ont pas de capacité au répertoire.`]);
    l.push(['Emplacement', `${nbfr(n - c.position)} établissements (${p(n - c.position)}) n’ont pas de coordonnées : ils n’apparaissent sur aucune carte et ne ressortent d’aucune recherche par rayon. ${nbfr(c.positionApprochee)} autres sont placés au centre de leur commune, et non à leur adresse.`]);
    l.push(['Places libres', 'Aucune source publique ne publie les places disponibles d’un établissement. Ce site n’en estime aucune.']);
    l.push(['Habilitation à l’aide sociale', `${nbfr(c.ashAConfirmer)} établissements présentent une contradiction entre le répertoire FINESS et leur tarif déclaré : leur habilitation est affichée « à confirmer ».`]);
    l.push(['Régime de financement', `${nbfr(c.exp)} établissements relèvent de l’expérimentation de fusion des financements (participation forfaitaire), ${nbfr(c.classique)} du droit commun${c.regimeInconnu ? `, et ${nbfr(c.regimeInconnu)} n’ont pas pu être tranchés` : ''}.`]);
    el.innerHTML = l.map(([t, d]) => `<li><b>${esc(t)}</b> — ${esc(d)}</li>`).join('')
      + `<li class="muted">Mesuré le ${dfr(c.date)} sur les ${nbfr(n)} établissements servis par ce site.</li>`;
  }

  /* ---------- Tests (console : window.runTests()) ---------- */
  window.runTests = function () {
    const mois = META.month;
    // 46 colonnes depuis l'ajout du régime (C.reg = 45). Sans mention contraire,
    // les cas de test portent sur un établissement de droit commun.
    const mk = (o) => Object.assign(new Array(46).fill(null), { 45: 'classique' }, o);
    const base = { mode: 'famille', gir: '34', revenus: 1500, autres: 0, epargne: 0, couple: false,
      deuxResidents: false, conjointDomicile: false, aideLogement: 0, imposable: false, chambre: 'cs', enfants: 0, tmi: 30,
      aplPortee: 'partout', aplEtab: null, moisAnnee: 12 };
    const E = mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1, 8: 80, 24: 80, 22: 0, 43: 1, 44: 93.24 });
    const cases = [
      ['APA : sous le seuil inférieur → participation = tarif GIR 5-6', () =>
        Math.abs(apaEtablissement(13.86 * mois, 5.89 * mois, 1500, false).participation - 5.89 * mois) < 0.01],
      ['APA : au-dessus du seuil supérieur → t56 + 80 % de l’écart', () =>
        Math.abs(apaEtablissement(13.86 * mois, 5.89 * mois, 6000, false).participation - (5.89 + 0.8 * (13.86 - 5.89)) * mois) < 0.01],
      ['APA : milieu de tranche strictement intermédiaire', () => {
        const r = apaEtablissement(13.86 * mois, 5.89 * mois, (SEUILS.apaInf + SEUILS.apaSup) / 2, false);
        return r.participation > 5.89 * mois && r.participation < (5.89 + 0.8 * (13.86 - 5.89)) * mois;
      }],
      ['APA : couple → ressources divisées par deux', () =>
        Math.abs(apaEtablissement(13.86 * mois, 5.89 * mois, 6000, true).participation
               - apaEtablissement(13.86 * mois, 5.89 * mois, 3000, false).participation) < 0.01],
      ['Seuils officiels 2 846,77 € et 4 379,64 €', () => Math.abs(SEUILS.apaInf - 2846.77) < 0.01 && Math.abs(SEUILS.apaSup - 4379.64) < 0.01],
      ['Reste à charge = hébergement + dépendance − APA', () => Math.abs(calcule(E, { ...base }).rac - (100 + 5.89) * mois) < 1],
      ['Autres revenus : comptés dans les ressources de l’APA', () => {
        const a = calcule(E, { ...base, revenus: 2000, autres: 0 }), b = calcule(E, { ...base, revenus: 2000, autres: 2000 });
        return b.apa < a.apa;
      }],
      ['Réduction d’impôt plafonnée à 2 500 €/an pour un résident', () =>
        Math.abs(calcule(E, { ...base, imposable: true }).fisc.reduction - 0.25 * 10000) < 0.01],
      ['Deux résidents hébergés : double plafond de réduction d’impôt', () =>
        Math.abs(calcule(E, { ...base, imposable: true, deuxResidents: true }).fisc.reduction - 0.25 * 20000) < 0.01],
      ['L’avantage fiscal ne diminue pas la somme à sortir chaque mois', () =>
        calcule(E, { ...base, imposable: true }).decaisse === calcule(E, { ...base, imposable: false }).decaisse],
      ['Aucun montant annuel ne vaut douze mois moyens (30,5 × 12 = 366)', () => {
        const j = joursAnnee();
        return (j === 365 || j === 366) && Math.abs(META.month * 12 - 366) < 0.001;
      }],
      ['Assiette fiscale annuelle comptée en jours réels', () => {
        const f = calcule(E, { ...base, revenus: 6000, imposable: true }).fisc;
        return f.joursRetenus === joursAnnee();
      }],
      ['Séjour de 5 mois : plafond de dépenses proratisé', () => {
        const f = calcule(E, { ...base, imposable: true, moisAnnee: 5 }).fisc;
        return Math.abs(f.plafondDepenses - 10000 * 5 / 12) < 0.01 && f.moisRetenus === 5;
      }],
      ['Frais sous le plafond : la réduction suit les frais, pas le plafond', () => {
        const f = calcule(mk({ 6: 10, 9: 5, 10: 3, 11: 1, 20: 1 }), { ...base, revenus: 6000, imposable: true }).fisc;
        return f.plafonne === false && Math.abs(f.reduction - f.depenses * 0.25) < 0.01;
      }],
      ['Deux résidents : hébergement doublé', () =>
        Math.abs(calcule(E, { ...base, deuxResidents: true }).heberg - 2 * 100 * mois) < 0.01],
      ['Non imposable → aucune réduction d’impôt', () => {
        const f = calcule(E, { ...base }).fisc;
        return f.reduction === 0 && f.applicable === false;
      }],
      ['Aide au logement déduite à l’euro près', () =>
        Math.abs((calcule(E, { ...base }).rac - calcule(E, { ...base, aideLogement: 300 }).rac) - 300) < 0.01],
      ['Conjoint à domicile : 1 043,59 € réservés avant la contribution', () => {
        const a = calcule(E, { ...base, revenus: 3000 }), b = calcule(E, { ...base, revenus: 3000, conjointDomicile: true });
        return Math.abs((b.trou - a.trou) - BAREME.ashConjointDomicile) < 0.01;
      }],
      ['Répartition entre enfants : part égale et coût net après impôt', () => {
        const r = calcule(E, { ...base, revenus: 1000, enfants: 3, tmi: 30 });
        return r.famille && Math.abs(r.famille.part * 3 - r.famille.total) < 0.01
            && Math.abs(r.famille.net - r.famille.part * 0.7) < 0.01;
      }],
      ['Aucun enfant → pas de bloc famille', () => calcule(E, { ...base, revenus: 1000 }).famille === null],
      ['Couple : le barème APA divise les ressources DU MÉNAGE, pas celles du résident seul', () => {
        // Même résident, même établissement. Seules les ressources du conjoint changent.
        const seul = calcule(E, { ...base, revenus: 3000, couple: true, revenusConjoint: 0 });
        const avec = calcule(E, { ...base, revenus: 3000, couple: true, revenusConjoint: 3000 });
        // Un conjoint qui perçoit autant ramène la base à 3 000 € au lieu de 1 500 € :
        // la participation monte, donc l'APA baisse.
        return avec.apa < seul.apa
          && Math.abs(avec.apa - calcule(E, { ...base, revenus: 3000 }).apa) < 0.01;
      }],
      ['Les ressources du conjoint ne sont comptées que si le couple est déclaré', () =>
        Math.abs(calcule(E, { ...base, revenus: 3000, revenusConjoint: 5000 }).apa
               - calcule(E, { ...base, revenus: 3000 }).apa) < 0.01],
      ['Les ressources du conjoint ne financent pas la facture du résident', () => {
        const a = calcule(E, { ...base, revenus: 1200, couple: true, revenusConjoint: 0 });
        const b2 = calcule(E, { ...base, revenus: 1200, couple: true, revenusConjoint: 4000 });
        // seule l'APA bouge ; le trou de trésorerie ne se comble pas avec l'argent du conjoint
        return b2.trou >= a.trou;
      }],
      ['Deux résidents : les ressources des deux font face à la facture des deux', () => {
        const r = calcule(E, { ...base, revenus: 1500, couple: true, deuxResidents: true, revenusConjoint: 1500 });
        const un = calcule(E, { ...base, revenus: 1500 });
        return Math.abs(r.facture - 2 * un.facture) < 0.01;
      }],
      ['GIR inconnu : le montant porte la réserve, il ne la perd pas', () => {
        const r = calcule(E, { ...base, gir: '?' });
        return r.girSuppose === true && r.notes.some((t) => t.indexOf('n’est pas connu') >= 0);
      }],
      ['Chambre double sans tarif déclaré : la substitution est signalée', () => {
        const r = calcule(mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1 }), { ...base, chambre: 'cd' });
        return r.chambreSupposee === true;
      }],
      ['Aucune retraite mais d’autres ressources : le calcul se déclenche quand même', () => {
        const av = { r: state.revenus, a: state.autres };
        state.revenus = 0; state.autres = 1400;
        const ok = perso() === true;
        state.revenus = 0; state.autres = 0;
        const vide = perso() === false;
        state.revenus = av.r; state.autres = av.a;
        return ok && vide;
      }],
      ['Ressources nulles : aucun montant négatif, aucune division par zéro', () => {
        const r = calcule(E, { ...base, revenus: 0, autres: 0 });
        return r.decaisse >= 0 && r.trou >= 0 && Number.isFinite(r.decaisse)
            && (r.moisEpargne === 0 || Number.isFinite(r.moisEpargne));
      }],
      ['Couleurs : vert, orange, rouge', () =>
        calcule(E, { ...base, revenus: 6000 }).couleur === 'vert'
        && calcule(E, { ...base, revenus: 1500, epargne: 400000 }).couleur === 'orange'
        && calcule(E, { ...base, revenus: 1000 }).couleur === 'rouge'],
      ['Aide sociale : la contribution ne dépasse jamais le prix facturé', () => {
        // l'établissement E déclare un tarif aide sociale (colonne pa) de 80 €/jour
        const r = calcule(E, { ...base, revenus: 6000 });
        return r.ash && Math.abs(r.ash.partParent - r.ash.prixRetenu) < 0.01 && r.ash.reste === 0;
      }],
      ['Aide sociale : ce qui reste au résident = ressources − contribution', () => {
        const r = calcule(E, { ...base, revenus: 6000 });
        return r.ash && Math.abs(r.ash.garde - (6000 - r.ash.partParent)) < 0.01;
      }],
      ['Aide sociale : les trois lignes se rejoignent', () => {
        const r = calcule(E, { ...base, revenus: 900 });
        return r.ash && Math.abs(r.ash.partParent + r.ash.reste - r.ash.prixRetenu) < 0.01;
      }],
      ['Scénario ASH : minimum de 125 € conservé', () => {
        const r = calcule(E, { ...base, revenus: 800 });
        return r.ash && Math.abs(r.ash.gardeMini - 125) < 0.01;
      }],
      ['Habilitation « à confirmer » : scénario ASH affiché avec réserve', () => {
        const r = calcule(mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 2 }), { ...base });
        return r.ash && r.ash.aConfirmer === true;
      }],
      ['Non habilité → pas de scénario ASH', () =>
        calcule(mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 0 }), { ...base }).ash === null],
      ['Facture, décaissement et reste à charge sont cohérents', () => {
        const r = calcule(E, { ...base, revenus: 6000, aideLogement: 200 });
        return Math.abs(r.facture - (r.heberg + r.dependance)) < 0.01
            && Math.abs(r.decaisse - (r.facture - r.apa - r.apl)) < 0.01
            && r.rac === r.decaisse && r.total === r.facture;
      }],
      ['Régime expérimental : forfait journalier, aucune APA', () => {
        const X = mk({ 6: 100, 9: 6.10, 10: 6.10, 11: 6.10, 20: 1, 45: 'exp' });
        const r = calcule(X, { ...base });
        const pf = participationForfaitaire();
        return r.reg === 'exp' && r.apa === 0 && r.apaConnue === false
            && Math.abs(r.dependance - pf.montant * mois) < 0.01 && r.pfJour === pf.montant;
      }],
      ['Régime expérimental : le forfait ne dépend ni du GIR ni des ressources', () => {
        const X = mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1, 45: 'exp' });
        const a = calcule(X, { ...base, gir: '12', revenus: 900 });
        const b2 = calcule(X, { ...base, gir: '56', revenus: 9000 });
        return Math.abs(a.dependance - b2.dependance) < 0.01;
      }],
      ['Régime expérimental : un tarif déclaré divergent est signalé, pas retenu', () => {
        const X = mk({ 6: 100, 9: 6.10, 10: 6.10, 11: 6.10, 20: 1, 45: 'exp' });
        const r = calcule(X, { ...base });
        return r.notes.some((t) => t.indexOf('montant national en vigueur') >= 0);
      }],
      ['Régime inconnu : la part « aide au quotidien » n’est pas inventée', () => {
        const X = mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1, 45: null });
        const r = calcule(X, { ...base });
        return r.reg === 'inconnu' && r.dependance === 0 && r.depConnue === false
            && r.notes.some((t) => t.indexOf('régime de financement') >= 0);
      }],
      ['Forfait : le barème est daté et sourcé', () => {
        const a = participationForfaitaire('2025-08-01'), b2 = participationForfaitaire('2026-03-01');
        return a.montant === 6.10 && b2.montant === 6.16 && !!a.src && !!b2.src;
      }],
      ['Aide au logement notifiée pour un autre établissement : non déduite', () => {
        const r = calcule(E, { ...base, aideLogement: 300, aplPortee: 'cet', aplEtab: 'AUTRE' });
        return r.apl === 0;
      }],
      ['Tarif aide sociale seul : l’information est conservée, le calcul ne l’est pas', () => {
        const r = calcule(mk({ 9: 20, 10: 13, 11: 5, 20: 1, 8: 55 }), { ...base });
        return r.prixConnu === false && r.tarifAshSeul === 55;
      }],
      ['Aucune extrapolation de places libres n’est produite', () => {
        const r = calcule(E, { ...base });
        return r.dispoEst === undefined && r.secteur != null && r.secteur.libres100 === undefined;
      }],
      ['Prix non déclaré → pas de calcul', () => calcule(mk({ 9: 20, 10: 13, 11: 5 }), { ...base }).prixConnu === false],
      ['Chambre double : prix distinct', () =>
        Math.abs(calcule(mk({ 6: 100, 7: 80, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1 }), { ...base, chambre: 'cd' }).heberg - 80 * mois) < 0.01],
      ['Fraîcheur : une déclaration de plus de 12 mois est signalée', () =>
        calcule(mk({ 6: 100, 12: '2020-01', 20: 1 }), { ...base }).vieux > 12],
      ['Courbe de prix : SVG produit pour deux points au moins', () =>
        sparkline({ p: [60, null, null, null, null, null, null, 73], e: 21.7, a: 2.9, d: '2018', f: '2025' }).indexOf('<svg') === 0],
      ['Courbe de prix : une année manquante interrompt le tracé', () => {
        const trou = sparkline({ p: [60, null, 73, null, null, null, null, null], e: 21.7, a: 2.9, d: '2018', f: '2020' });
        const suite = sparkline({ p: [60, 73, null, null, null, null, null, null], e: 21.7, a: 2.9, d: '2018', f: '2019' });
        // deux « M » quand il y a une lacune, un seul quand les années se suivent
        return (trou.match(/M/g) || []).length === 2 && (suite.match(/M/g) || []).length === 1;
      }],
      ['Écart à l’inflation exprimé en points, jamais en pourcentage', () => {
        const h = blocPrix({ p: [60, 62, 63, 64, 66, 68, 71, 73], e: 21.7, a: 2.9, d: '2018', f: '2025' });
        return h.indexOf('point') > 0 && h.indexOf('% de plus que l’inflation') < 0;
      }],
      ['Inflation cumulée 2018 → 2025 : +17,2 %', () => Math.abs(INFLATION_CUM_2018_2025 - 17.2) < 0.01],
      ['Lien de partage : la recherche voyage, la situation reste', () => {
        const o = JSON.parse(decodeURIComponent(escape(atob(/#s=(.+)$/.exec(lienPartage(false))[1]))));
        return o.rayon === state.rayon && o.gir === undefined && o.revenus === undefined
            && o.epargne === undefined && o.tmi === undefined;
      }],
      ['Lien de partage étendu : la situation n’y est qu’à la demande', () => {
        const o = JSON.parse(decodeURIComponent(escape(atob(/#s=(.+)$/.exec(lienPartage(true))[1]))));
        return o.gir === state.gir && o.rayon === state.rayon;
      }],
      ['Distance Lyon 3e → Villeurbanne inférieure à 6 km', () => distKm(45.7548, 4.8624, 45.7719, 4.8902) < 6],
      ['Rayon de 40 km autour de Lyon : plusieurs départements chargés', () => depsInRadius(45.75, 4.85, 40).length >= 2],
      ['Codes postaux corses → deux départements', () => depsForCp('20000').length === 2],
      ['Outre-mer → département sur trois chiffres', () => depsForCp('97400')[0] === '974'],
      ['Table départementale : contexte Badiane présent pour le Rhône', () =>
        !!(window.ME_DEP && ME_DEP['69'] && ME_DEP['69'].b_places > 10000)],
      ['Aucun reste à charge négatif', () =>
        calcule(E, { ...base, revenus: 500, aideLogement: 99999, imposable: true }).rac === 0],
      ['Le GIR choisi dans l’interface reste une chaîne (« 12 », pas 12)', () => {
        const seg = document.querySelector('[data-seg^="gir:"]');
        if (!seg) return false;
        const avant = state.gir;
        seg.querySelectorAll('button')[0].click();
        const ok = state.gir === '12' && calcule(E, { ...base, gir: state.gir }).dependance === 21.85 * mois;
        state.gir = avant; majUI();
        return ok;
      }],
      ['Seul en EHPAD : la réserve du conjoint à domicile ne s’applique pas si les deux sont hébergés', () => {
        const a = calcule(E, { ...base, couple: true, conjointDomicile: true, deuxResidents: true });
        const b2 = calcule(E, { ...base, couple: true, conjointDomicile: false, deuxResidents: true });
        return a.ash && b2.ash && a.ash.reserveConjoint === 0 && a.ash.partParent === b2.ash.partParent;
      }],
      ['Combinaisons impossibles remises d’accord : pas de conjoint à domicile sans couple', () => {
        const av = { c: state.couple, d: state.deuxResidents, j: state.conjointDomicile };
        state.couple = false; state.deuxResidents = true; state.conjointDomicile = true;
        normalise();
        const ok = state.deuxResidents === false && state.conjointDomicile === false;
        state.couple = av.c; state.deuxResidents = av.d; state.conjointDomicile = av.j;
        return ok;
      }],
      ['GIR 1-2 coûte plus cher que GIR 5-6 au-dessus du seuil (identique en dessous : l’APA absorbe l’écart)', () =>
        calcule(E, { ...base, revenus: 6000, gir: '12' }).rac > calcule(E, { ...base, revenus: 6000, gir: '56' }).rac
        && calcule(E, { ...base, revenus: 1500, gir: '12' }).rac === calcule(E, { ...base, revenus: 1500, gir: '56' }).rac],
    ];
    let ok = 0;
    for (const [name, fn] of cases) {
      let pass = false; try { pass = !!fn(); } catch (e) { console.error(name, e); }
      ok += pass;
      console[pass ? 'log' : 'error'](`${pass ? '✅' : '❌'} ${name}`);
    }
    console.log(`${ok}/${cases.length} tests OK`);
    return ok === cases.length;
  };
})();
