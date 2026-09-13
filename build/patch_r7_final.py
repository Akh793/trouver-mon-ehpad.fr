# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 7 : deux affirmations fausses, et le mode professionnel.

Deux points du §11 vérifiés dans le code, et faux :

1. « La bibliothèque de cartographie est servie depuis ce site : aucune requête
   vers un service tiers. » La bibliothèque, oui. Mais les tuiles du fond de plan
   sont téléchargées chez l'IGN à chaque affichage de carte : cet organisme voit
   donc l'adresse IP du visiteur et la zone consultée. La phrase est vraie au sens
   strict et trompeuse au sens où elle est lue.

2. Le scénario d'aide sociale affichait un mensuel et son cumul annuel calculés sur
   deux bases : le mois moyen de 30,5 jours d'un côté, les 365 jours réels de
   l'autre. 750 €/mois y devenait 8 975 €/an, soit 25 € de moins que la
   multiplication par douze qu'un lecteur ferait de tête. Le paragraphe suivant
   explique déjà que cette créance n'est pas calculable d'avance : la projection
   annuelle ne lui apportait rien et la contredisait.
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


patch(os.path.join('..', 'site', 'data.js'), [
    ("note: 'La bibliothèque de cartographie est servie depuis ce site : aucune requête vers un service tiers.'",
     "note: 'La bibliothèque de cartographie est servie depuis ce site. Les tuiles du fond de plan, elles, sont téléchargées auprès de l’IGN à l’affichage de la carte : cet organisme public voit alors l’adresse IP du visiteur et la zone consultée.'"),
])

patch(os.path.join('..', 'site', 'app.js'), [
    ("""              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour, à raison de
                 <b>${euro((r.ash.reste / M()) * joursAnnee())} par an</b> au rythme actuel. Le département peut en
                 demander tout ou partie&nbsp;: aux enfants au titre de l’obligation alimentaire pendant
                 le séjour, et à la succession ensuite.</p>""",
     """              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour. Le département peut en
                 demander tout ou partie&nbsp;: aux enfants au titre de l’obligation alimentaire pendant
                 le séjour, et à la succession ensuite.</p>"""),
])

patch('index.template.html', [
    # ── Mode professionnel : ce qui est enregistré, et où, en une phrase
    ("""        <p class="fld-h">Une recherche enregistrée retient la zone, la distance, les critères de recherche et la liste de démarches. Elle ne retient <b>ni identité, ni ressources</b>&nbsp;: les montants saisis servent au calcul du moment et ne sont pas enregistrés dans la recherche. Tout reste sur cet appareil, dans ce navigateur&nbsp;: rien n’est transmis, et vider le cache efface tout. Donnez à vos recherches un repère neutre — «&nbsp;Dossier 001&nbsp;», «&nbsp;Recherche Lyon Est&nbsp;» — jamais le nom de la personne accompagnée.</p>
        <div class="fld" style="margin-top:1rem">
          <label for="dossier-nom">Nom de la recherche</label>
          <input id="dossier-nom" maxlength="60" placeholder="Dossier 001">
        </div>""",
     """        <p class="fld-h">Recherche enregistrée dans ce navigateur, sans identité ni revenus. Zone, critères et liste de démarches uniquement. Vider le cache efface tout.</p>
        <div class="fld" style="margin-top:1rem">
          <label for="dossier-nom">Repère du dossier</label>
          <input id="dossier-nom" maxlength="60" placeholder="Dossier 001">
          <p class="fld-h">N’indiquez pas de nom.</p>
        </div>"""),

    ("""    <p data-mode="pro" hidden class="mode-note" id="pro-dossier-ligne"><span id="pro-dossier">Aucune recherche enregistrée ouverte.</span> Les critères et la liste de démarches restent sur cet appareil, dans ce navigateur&nbsp;: rien n’est transmis, rien n’est enregistré ailleurs. N’y saisissez aucune donnée nominative.</p>""",
     """    <p data-mode="pro" hidden class="mode-note" id="pro-dossier-ligne"><span id="pro-dossier">Aucune recherche enregistrée ouverte.</span> Enregistré dans ce navigateur, sans identité ni revenus.</p>"""),

    ("""      <div class="pro-b-t">
        <p class="pro-b-h">Espace professionnel</p>
        <p class="pro-b-s">Identifiez les établissements compatibles avec le budget, la localisation et les aides disponibles, puis constituez votre liste de démarches.</p>
      </div>""",
     """      <div class="pro-b-t">
        <p class="pro-b-h">Espace professionnel</p>
        <p class="pro-b-s">Comparez les budgets estimés et préparez une liste de démarches.</p>
      </div>"""),

    # ── ViaTrajectoire : ne plus le présenter comme la voie unique
    ("""      <a class="g-card" href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-ehpad-et-maisons-de-retraite" target="_blank" rel="noopener"><b>Déposer un dossier ViaTrajectoire</b><span>Le dossier unique : la seule voie pour candidater. Les places disponibles ne sont publiées nulle part.</span></a>""",
     """      <a class="g-card" href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-ehpad-et-maisons-de-retraite" target="_blank" rel="noopener"><b>Déposer un dossier de demande</b><span>ViaTrajectoire dans la plupart des régions, dossier papier ailleurs. L’établissement vous dira lequel il accepte.</span></a>"""),
])

print('%d blocs posés' % n)
