# -*- coding: utf-8 -*-
"""Le parcours supposait qu'on cherche pour quelqu'un d'autre.

Toute l'interface disait « votre parent ». Une personne qui cherche pour elle-même
devait traduire chaque phrase, et le formulaire lui demandait « la retraite de votre
parent » pour parler de la sienne. Un choix explicite, posé avant la saisie, change
les formulations sans rien changer au calcul.
"""
import io, os, sys

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.template.html')
n = 0


def patch(chemin, paires):
    global n
    s = io.open(chemin, encoding='utf-8').read()
    for a, b in paires:
        if a not in s:
            print('INTROUVABLE dans %s :' % os.path.basename(chemin), a[:110].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(chemin, 'w', encoding='utf-8').write(s)


patch(APP, [
    # ── 1. L'état et le vocabulaire
    ("    couple: false, conjointDomicile: false, deuxResidents: false,",
     """    pourQui: 'proche',         // 'proche' = on cherche pour quelqu'un · 'moi' = pour soi-même
    couple: false, conjointDomicile: false, deuxResidents: false,"""),

    ("  const perso = () => Number.isFinite(state.revenus) && state.revenus > 0;",
     """  /* ---------- Pour qui cherche-t-on ? ----------
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
  const perso = () => Number.isFinite(state.revenus) && state.revenus > 0;"""),

    # ── 2. Les phrases du moteur et de la fiche
    ("        L’aide au logement, elle, reste due si votre parent y a droit.</p>`;",
     "        L’aide au logement, elle, reste due si ${mot('y_droit')}.</p>`;"),
    ("      <p class=\"f-note\">Ce que les ressources de votre parent ne couvrent pas, partagé entre ses enfants.</p>",
     "      <p class=\"f-note\">Ce que ${mot('res')} ne couvrent pas, partagé entre ${pourMoi() ? 'vos' : 'ses'} enfants.</p>"),
    ("        ${r.prixConnu && !p ? '<p class=\"ctx\">Indiquez la retraite de votre parent, en haut de page, pour voir ce qui resterait vraiment à payer.</p>' : ''}",
     "        ${r.prixConnu && !p ? `<p class=\"ctx\">Indiquez ${mot('retraite')}, en haut de page, pour voir ce qui resterait vraiment à payer.</p>` : ''}"),
    ("      return `Les ressources de votre parent (${euro(dispo)}/mois) couvrent cette somme.`;",
     "      return `${mot('resMaj')} (${euro(dispo)}/mois) couvrent cette somme.`;"),
    ("    return `Il manque ${euro(manque)} chaque mois : au-delà des ressources de votre parent.",
     "    return `Il manque ${euro(manque)} chaque mois : au-delà ${pourMoi() ? 'de vos ressources' : 'des ressources de votre parent'}."),
    ("            <div class=\"ln\"><span>Votre parent verse sur ses propres ressources</span><b>− ${euro(r.ash.partParent)}/mois</b></div>",
     "            <div class=\"ln\"><span>${mot('Sujet')} verse${pourMoi() ? 'z' : ''} sur ${pourMoi() ? 'vos' : 'ses'} propres ressources</span><b>− ${euro(r.ash.partParent)}/mois</b></div>"),
    ("""                      les ressources de votre parent ne suffisent pas à couvrir cette part une fois sa""",
     """                      ${mot('res')} ne suffisent pas à couvrir cette part une fois la"""),
    ("""              : `<p class="f-note">Au tarif retenu, les ressources de votre parent couvrent le prix&nbsp;:""",
     """              : `<p class="f-note">Au tarif retenu, ${mot('res')} couvrent le prix&nbsp;:"""),
    ("        ? `reste à charge médian pour votre parent · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois${rouges ? ` · <b>${rouges}</b> hors de portée sans aide sociale ni aide de la famille` : ''}`",
     "        ? `reste à charge médian pour ${mot('titre')} · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois${rouges ? ` · <b>${rouges}</b> hors de portée sans aide sociale ni aide de la famille` : ''}`"),
    ("        : `tarif médian, avant les aides · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois · <b>indiquez la retraite de votre parent</b> pour voir ce qui resterait à payer`;",
     "        : `tarif médian, avant les aides · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois · <b>indiquez ${mot('retraite')}</b> pour voir ce qui resterait à payer`;"),
    ("        + 'ni sur l’autonomie de votre parent.';",
     "        + `ni sur ${mot('autonomie')}.`;"),

    # ── 3. Les libellés fixes de la page, réécrits au rendu
    ("    majCouverture();",
     """    majCouverture();
    majPourQui();"""),

    ("  /** Ce que les données ne couvrent pas, dit en clair et recalculé à chaque build.",
     """  /** Réécrit les libellés de la page selon la personne concernée. Aucun calcul n'en dépend. */
  function majPourQui() {
    const t = {
      'h1-sujet': pourMoi() ? 'vous' : 'votre parent',
      'lbl-revenus': pourMoi() ? 'Vos retraites et pensions' : 'Retraites et pensions du parent',
      'lbl-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',
      'nav-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',
      'lbl-gir': pourMoi() ? 'Votre niveau d’autonomie (GIR)' : 'Le niveau d’autonomie du parent (GIR)',
      'lbl-couple': pourMoi() ? 'Vivez-vous en couple ?' : 'Vit-il ou elle en couple ?',
      'lbl-proprio': pourMoi() ? 'Êtes-vous propriétaire de votre logement ?' : 'Est-il ou elle propriétaire de son logement ?',
    };
    Object.keys(t).forEach((id) => { const el = $(id); if (el) el.textContent = t[id]; });
    const v = $('v-s');
    if (v) v.textContent = 'Les établissements autour de vous s’affichent aussitôt. Indiquez ensuite '
      + (pourMoi() ? 'votre retraite' : 'la retraite de votre parent')
      + ' : chaque tarif devient le montant qui resterait réellement à payer.';
  }

  /** Ce que les données ne couvrent pas, dit en clair et recalculé à chaque build."""),

    # ── 4. Le choix est partagé et mémorisé comme le reste de la recherche
    ("  const PARTAGE_RECHERCHE = ['mode', 'cp', 'rayon', 'chambre', 'tri',",
     "  const PARTAGE_RECHERCHE = ['mode', 'pourQui', 'cp', 'rayon', 'chambre', 'tri',"),
])

patch(TPL, [
    # le choix, posé avant la première saisie
    ("""      <h2><span class="n">1</span> La situation de <em class="bl">votre parent</em></h2>""",
     """      <h2><span class="n">1</span> <span id="lbl-situation">La situation de votre parent</span></h2>
      <div class="fld fld-pq">
        <label>Pour qui faites-vous cette recherche&nbsp;?</label>
        <div class="seg" data-seg="pourQui:proche,moi" role="group" aria-label="Pour qui">
          <button type="button">Un proche</button><button type="button">Moi-même</button>
        </div>
        <p class="fld-h">Cela ne change rien au calcul, seulement la façon dont les questions sont posées.</p>
      </div>"""),
    ("""        <h1>Ce que l’EHPAD coûtera<br><span class="h1-l2"><em class="bl">vraiment</em> à <em class="co">votre parent</em></span></h1>""",
     """        <h1>Ce que l’EHPAD coûtera<br><span class="h1-l2"><em class="bl">vraiment</em> à <em class="co" id="h1-sujet">votre parent</em></span></h1>"""),
    ("""        <label for="revenus">Retraites et pensions du parent</label>""",
     """        <label for="revenus" id="lbl-revenus">Retraites et pensions du parent</label>"""),
    ("""            <a href="#bande-situation">La situation de votre parent</a>""",
     """            <a href="#bande-situation" id="nav-situation">La situation de votre parent</a>"""),
    ("""      <p class="v-s">Les établissements autour de vous s’affichent aussitôt. Indiquez ensuite la retraite de votre parent&nbsp;: chaque tarif devient le montant qui resterait réellement à payer.</p>""",
     """      <p class="v-s" id="v-s">Les établissements autour de vous s’affichent aussitôt. Indiquez ensuite la retraite de votre parent : chaque tarif devient le montant qui resterait réellement à payer.</p>"""),
    ("""        <label>Vit-il ou elle en couple ?</label>""",
     """        <label id="lbl-couple">Vit-il ou elle en couple ?</label>"""),
    ("""        <label>Est-il ou elle propriétaire de son logement ?</label>""",
     """        <label id="lbl-proprio">Est-il ou elle propriétaire de son logement ?</label>"""),
])

print('%d blocs corrigés' % n)
