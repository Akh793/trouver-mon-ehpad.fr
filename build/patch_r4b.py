# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 4b : l'écart à la médiane rejoint « Prix & aides »,
et le résumé reçoit ses styles.

L'écart au prix médian n'est pas un indicateur de qualité : posé sous le montant
principal, il se lisait comme une alerte. Il devient un repère du décompte,
avec l'effectif réellement comparable. Le mot « médiane » est conservé tel quel :
ce n'est pas une moyenne, et l'appeler ainsi serait faux.
"""
import io, os, sys

B = os.path.dirname(os.path.abspath(__file__))
n = 0


def patch(rel, paires):
    global n
    p = os.path.join(B, rel)
    s = io.open(p, encoding='utf-8').read()
    for a, b in paires:
        if a not in s:
            print('INTROUVABLE dans %s :' % rel, a[:110].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(p, 'w', encoding='utf-8').write(s)


patch(os.path.join('..', 'site', 'app.js'), [
    ("""  function ecartMediane(o) {
    if (!o.r.prixConnu) return '';
    const avec = dernier.filter((x) => x.r.prixConnu);
    if (avec.length < 5) return '';
    const med = avec.map((x) => x.r.total).sort((a, b) => a - b)[Math.floor(avec.length / 2)];
    const d = o.r.total - med;
    if (Math.abs(d) < 20) return '<p class="ctx">Tarif proche de la médiane de votre sélection.</p>';
    return `<p class="ctx">${euro(Math.abs(d))} ${d < 0 ? 'sous' : 'au-dessus de'} la médiane des ${avec.length} établissements de votre sélection.</p>`;
  }""",
     """  /** Situe la facture dans la sélection. Ce n'est pas un indicateur de qualité :
      un tarif bas peut refléter un prix maîtrisé comme un service réduit. */
  function ecartMediane(o) {
    if (!o.r.prixConnu) return '';
    const avec = dernier.filter((x) => x.r.prixConnu);
    if (avec.length < 5) return '';
    const med = avec.map((x) => x.r.facture).sort((a, b) => a - b)[Math.floor(avec.length / 2)];
    const d = o.r.facture - med;
    const base = `<p class="f-note">Prix médian comparé&nbsp;: ${euro(med)} sur ${avec.length} établissements
      de la sélection ayant déclaré un tarif.`;
    if (Math.abs(d) < 20) return base + ' Cette facture en est proche.</p>';
    return base + ` Cette facture est <b>${euro(Math.abs(d))} ${d < 0 ? 'en dessous' : 'au-dessus'}</b>.</p>`;
  }"""),

    # l'écart rejoint le décompte, après l'avantage fiscal
    ("""    } else if (r.fisc && !r.fisc.applicable) {
      h += `<p class="f-note">Une réduction d’impôt de 25&nbsp;% existe pour les personnes imposables.
        Indiquez-le dans «&nbsp;Préciser la situation&nbsp;» pour voir ce qu’elle représenterait.</p>`;
    }
    return h;""",
     """    } else if (r.fisc && !r.fisc.applicable) {
      h += `<p class="f-note">Une réduction d’impôt de 25&nbsp;% existe pour les personnes imposables.
        Indiquez-le dans «&nbsp;Préciser ma situation&nbsp;» pour voir ce qu’elle représenterait.</p>`;
    }
    h += ecartMediane(o);
    return h;"""),

    # l'état de l'aide sociale s'explique là où il compte
    ("""        ${r.ash ? `<div class="scenario"><b>Et si les ressources ne suffisent pas&nbsp;?</b>""",
     """        <h4 class="f-t1">Aide sociale</h4>
        <div class="ln"><span>État de l’habilitation</span><b>${esc(ashEtat(e))}</b></div>
        <p class="f-note">${esc(ashNote(e))}</p>
        ${r.ash ? `<div class="scenario"><b>Et si les ressources ne suffisent pas&nbsp;?</b>"""),
])

patch('site.css', [
    (".res-tel{color:var(--bl-t)",
     """/* Le complément à financer se lit avec le budget, pas trois écrans plus bas. */
.f-manque{margin-top:.7rem;padding:.6rem .8rem;border-radius:var(--r2);
  background:var(--ti-or);color:var(--sur-or);font-size:.86rem;line-height:1.4}
.f-manque b{font-size:1rem}
.f-dispo-l{margin-top:.6rem;font-size:.82rem;color:var(--mut)}
.res-tel{color:var(--bl-t)"""),
])

print('%d blocs posés' % n)
