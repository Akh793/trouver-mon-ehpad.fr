# -*- coding: utf-8 -*-
"""Mentions légales : la page de retours crée un traitement, il doit y figurer.

Le texte affirmait « aucune donnée personnelle n'étant collectée par le site, il n'y
a pas de traitement ». Dès qu'un visiteur peut envoyer un message, c'est faux : le
message lui-même est une donnée, le prénom facultatif en est une, et l'empreinte
technique de l'adresse IP en est une aussi. L'affirmation est donc restreinte au
calculateur, qui la mérite, et le traitement des retours est décrit à part.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_pages.py')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:110].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


rem(
    """<h2>Droits</h2>
<p>Aucune donnée personnelle n’étant collectée par le site, il n’y a pas de traitement à exercer de droit d’accès ou d’effacement. Pour toute question : <a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a>.</p>""",
    """<h2 id="retours">Page « Vos retours »</h2>
<p>La page <a href="/retours/">Vos retours</a> est la seule du site qui transmette des informations à un serveur. Ce qu’elle enregistre, et rien d’autre :</p>
<ul>
<li><b>Le message</b> que vous écrivez, et le <b>prénom ou pseudonyme</b> si vous en indiquez un. Aucune adresse e-mail n’est demandée : le service ne peut donc pas vous répondre, ni vous reconnaître d’un message à l’autre.</li>
<li>Une <b>empreinte technique de votre adresse IP</b>, transformée par une fonction à sens unique et jamais conservée en clair. Elle sert uniquement à limiter le nombre de messages envoyés depuis un même appareil, et elle est effacée au bout de deux jours.</li>
</ul>
<p><b>Finalité</b> : recueillir les retours des visiteurs pour corriger et améliorer le site, et publier ceux qui peuvent aider d’autres familles. <b>Base légale</b> : l’intérêt légitime de l’éditeur à améliorer son service, et votre démarche volontaire pour la publication.</p>
<p><b>Publication</b> : aucun message n’apparaît automatiquement. Chacun est lu avant d’être publié. Ne sont pas publiés les messages mettant en cause nommément un établissement, ni ceux permettant d’identifier une personne. <b>Conservation</b> : les messages publiés le restent jusqu’à leur retrait ; les messages écartés sont effacés au bout de trente jours.</p>
<p><b>Sous-traitant</b> : le point de réception et la base de données sont hébergés chez Cloudflare, Inc. Aucune donnée n’est transmise à des établissements, à des annonceurs ou à des tiers commerciaux.</p>
<p><b>Ce qu’il ne faut pas y écrire</b> : cette page est publique. N’y indiquez aucune donnée de santé, aucune ressource, aucun nom de résident, de proche ou de salarié, aucune adresse ni numéro de téléphone. Pour une situation particulière, écrivez à l’adresse ci-dessous.</p>

<h2>Droits</h2>
<p>Le calculateur ne collecte aucune donnée personnelle : les informations que vous y saisissez ne quittent pas votre appareil, et il n’y a donc rien à demander à leur sujet.</p>
<p>Pour un message envoyé sur la page « Vos retours », vous pouvez demander à le consulter, le corriger ou l’effacer. Le service ne conservant aucun moyen de vous identifier, indiquez dans votre demande la date approximative et le contenu du message, pour qu’il puisse être retrouvé. Vous disposez également du droit d’introduire une réclamation auprès de la CNIL. Pour toute question : <a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a>.</p>"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
