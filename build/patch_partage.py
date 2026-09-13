# -*- coding: utf-8 -*-
"""Le lien de partage transportait la situation financière, sans le dire.

Ressources, épargne, tranche d'imposition, nombre d'enfants : tout partait dans
l'adresse, encodée en Base64. Le Base64 n'est pas un chiffrement — c'est une
écriture, que n'importe qui décode en une ligne. Un lien collé dans un message,
un historique de navigateur ou un ticket d'assistance expose donc ces données.

Le partage porte désormais la RECHERCHE par défaut ; la situation financière n'y
est jointe que sur demande explicite, et l'interface dit ce que le lien contient.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.template.html')
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


patch(P, [
    # ── 1. Deux périmètres de partage, explicitement séparés
    ("""  const PARTAGE = ['mode', 'cp', 'rayon', 'gir', 'revenus', 'autres', 'epargne', 'proprietaire', 'couple',
    'conjointDomicile', 'deuxResidents', 'revenusConjoint', 'aideLogement', 'imposable', 'chambre', 'enfants', 'tmi', 'tri',
    'ashOnly', 'hasAB', 'tempOnly', 'prixConnu'];""",
     """  /* Ce qui décrit la RECHERCHE : où, dans quel rayon, avec quels filtres.
     Rien ici ne renseigne sur l'argent ni sur la santé de qui que ce soit. */
  const PARTAGE_RECHERCHE = ['mode', 'cp', 'rayon', 'chambre', 'tri',
    'ashOnly', 'hasAB', 'tempOnly', 'prixConnu'];
  /* Ce qui décrit la SITUATION : ressources, épargne, fiscalité, niveau d'autonomie.
     Un GIR est une donnée de santé. Ces champs ne partent que sur demande explicite. */
  const PARTAGE_SITUATION = ['gir', 'revenus', 'autres', 'epargne', 'proprietaire', 'couple',
    'conjointDomicile', 'deuxResidents', 'revenusConjoint', 'aideLogement', 'imposable', 'enfants', 'tmi'];
  const PARTAGE = PARTAGE_RECHERCHE.concat(PARTAGE_SITUATION);   // lecture d'un lien : on accepte tout"""),

    ("""  function lienPartage() {
    const o = {};
    PARTAGE.forEach((k) => { const v = state[k]; if (v !== null && v !== undefined && !(typeof v === 'number' && !Number.isFinite(v))) o[k] = v; });""",
     """  /** @param {boolean} avecSituation joindre la situation financière et le GIR.
      Le lien n'est pas chiffré : son contenu est lisible par quiconque le reçoit. */
  function lienPartage(avecSituation) {
    const o = {};
    const champs = avecSituation ? PARTAGE : PARTAGE_RECHERCHE;
    champs.forEach((k) => { const v = state[k]; if (v !== null && v !== undefined && !(typeof v === 'number' && !Number.isFinite(v))) o[k] = v; });"""),

    # ── 2. Le bouton : périmètre choisi, message honnête
    ("""  $('share-btn').addEventListener('click', async () => {
    const url = lienPartage();
    try { history.replaceState(null, '', url); } catch (e) {}
    let ok = false;
    try { await navigator.clipboard.writeText(url); ok = true; } catch (e) {}
    $('share-msg').textContent = ok ? 'Lien copié : envoyez-le à vos frères et sœurs, il rouvre exactement cette simulation.'
      : 'Lien prêt dans la barre d’adresse : copiez-le pour l’envoyer.';
    $('share-msg').hidden = false;
    setTimeout(() => { $('share-msg').hidden = true; }, 8000);
  });""",
     """  $('share-btn').addEventListener('click', async () => {
    const avec = !!($('share-situation') && $('share-situation').checked);
    const url = lienPartage(avec);
    try { history.replaceState(null, '', url); } catch (e) {}
    let ok = false;
    try { await navigator.clipboard.writeText(url); ok = true; } catch (e) {}
    const quoi = avec
      ? 'Il contient la situation saisie — ressources, épargne, niveau d’autonomie — en clair : '
        + 'l’adresse est encodée, pas chiffrée. Ne l’envoyez qu’à des personnes concernées.'
      : 'Il rouvre la recherche (commune, rayon, filtres) sans aucune information sur les ressources '
        + 'ni sur l’autonomie de votre parent.';
    $('share-msg').textContent = (ok ? 'Lien copié. ' : 'Lien prêt dans la barre d’adresse. ') + quoi;
    $('share-msg').hidden = false;
    setTimeout(() => { $('share-msg').hidden = true; }, 14000);
  });"""),

    # ── 3. Le test suit le périmètre par défaut
    ("""      ['Lien de partage : aller-retour sans perte', () => {
        const url = lienPartage();
        const o = JSON.parse(decodeURIComponent(escape(atob(/#s=(.+)$/.exec(url)[1]))));
        return o.gir === state.gir && o.rayon === state.rayon;
      }],""",
     """      ['Lien de partage : la recherche voyage, la situation reste', () => {
        const o = JSON.parse(decodeURIComponent(escape(atob(/#s=(.+)$/.exec(lienPartage(false))[1]))));
        return o.rayon === state.rayon && o.gir === undefined && o.revenus === undefined
            && o.epargne === undefined && o.tmi === undefined;
      }],
      ['Lien de partage étendu : la situation n’y est qu’à la demande', () => {
        const o = JSON.parse(decodeURIComponent(escape(atob(/#s=(.+)$/.exec(lienPartage(true))[1]))));
        return o.gir === state.gir && o.rayon === state.rayon;
      }],"""),
])

patch(H, [
    ("""            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>""",
     """            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>
            <label class="share-opt"><input type="checkbox" id="share-situation">
              Joindre la situation saisie (ressources, autonomie) — le lien n’est pas chiffré</label>"""),
    ("""        "Lien de partage : la simulation se rouvre à l’identique chez les frères et sœurs, sans aucun nom transmis",""",
     """        "Lien de partage : la recherche se rouvre à l’identique chez les frères et sœurs, sans ressources ni niveau d’autonomie transmis, sauf demande explicite",""")
])

print('%d blocs corrigés' % n)
