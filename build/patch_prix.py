# -*- coding: utf-8 -*-
"""Historique de prix : comparabilité, années manquantes, unité de l'écart.

Trois défauts :
  1. la courbe reliait deux années séparées par une lacune d'un trait continu, tout en
     affirmant le contraire sous le graphique ;
  2. l'écart à l'inflation était exprimé en pourcentage alors que la soustraction de deux
     pourcentages donne des POINTS ;
  3. rien ne disait que la comparaison suppose un objet inchangé — même type de chambre,
     même périmètre de prestations — ce que la source ne permet pas de vérifier.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:110].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


# ── 1. La courbe s'interrompt là où la déclaration manque
rem(
    """    const d = vals.map((v, k) => `${k ? 'L' : 'M'}${X(v[0]).toFixed(1)},${Y(v[1]).toFixed(1)}`).join(' ');""",
    """    // Une année sans déclaration interrompt le tracé : relier deux points distants
    // dessinerait une progression régulière que personne n'a observée.
    let d = '', precedent = null;
    vals.forEach((v) => {
      const suite = precedent !== null && v[0] === precedent + 1;
      d += `${suite ? 'L' : 'M'}${X(v[0]).toFixed(1)},${Y(v[1]).toFixed(1)} `;
      precedent = v[0];
    });
    d = d.trim();"""
)

# ── 2. L'écart à l'inflation se compte en points, et la comparabilité se dit
rem(
    """  function blocPrix(p) {
    if (!p) return '';
    const vals = p.p.filter((x) => x != null);
    const infl = INFLATION_CUM_2018_2025;
    const compl = (p.d === '2018' && p.f === '2025')
      ? (p.e > infl ? `soit <b>${pct(p.e - infl)} de plus que l’inflation</b> (+17,2 % sur la période)`
                    : `soit ${pct(p.e - infl)} par rapport à l’inflation (+17,2 % sur la période)`)
      : 'période incomplète : l’établissement n’a pas déclaré chaque année';
    const baisse = p.e < 0;
    return `<div class="prix-box ${baisse ? 'baisse' : ''}">
      <div class="prix-h">${sparkline(p)}
        <div><b class="${baisse ? 'vert' : 'rouge'}">${pct(p.e)}</b> de ${p.d} à ${p.f}
          <span class="muted">(${p.a != null ? pct(p.a, 1) + ' par an' : '—'})</span></div>
      </div>
      <p class="prix-s">${euro2(vals[0])} → ${euro2(vals[vals.length - 1])} par jour · ${compl}.</p>
      ${vals.length < p.p.length ? '<p class="prix-n">Années sans déclaration : la courbe ne les relie pas.</p>' : ''}
    </div>`;
  }""",
    """  function blocPrix(p) {
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
  }"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
