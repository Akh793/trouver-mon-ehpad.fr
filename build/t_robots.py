# -*- coding: utf-8 -*-
"""Contrôle du robots.txt avec un analyseur conforme à la spécification Google.

Le défaut corrigé : les règles placées après un groupe nommé appartiennent à ce
groupe, pas à « User-agent: * » — un groupe ne se termine qu'à la ligne
user-agent suivante, jamais à une ligne vide.
"""
from protego import Protego

ANCIEN = open('/tmp/robots-ancien.txt', encoding='utf-8').read()
NOUVEAU = open('../site/robots.txt', encoding='utf-8').read()
B = 'https://trouver-mon-ehpad.fr'

CAS = [
    # (robot,            adresse,                              exploration attendue)
    ('Googlebot',        '/',                                   True),
    ('Googlebot',        '/ehpad/abbeville/',                   True),
    ('Googlebot',        '/prix-ehpad/',                        True),
    ('Googlebot',        '/sitemap.xml',                        True),
    ('Googlebot',        '/data/dep/communes-69.js',            True),
    ('Googlebot',        '/?cp=69003&revenus=1600&gir=2',       False),
    ('Googlebot',        '/ehpad/?tri=prix',                    False),
    ('Googlebot-Image',  '/?cp=69003',                          False),
    ('Bingbot',          '/?cp=69003',                          False),
    ('GPTBot',           '/?cp=69003',                          False),
    ('GPTBot',           '/ehpad/abbeville/',                   True),
    ('ClaudeBot',        '/?cp=69003',                          False),
    ('ClaudeBot',        '/prix-ehpad/',                        True),
    ('PerplexityBot',    '/?revenus=1600',                      False),
    ('Applebot',         '/?revenus=1600',                      False),
    ('un-robot-inconnu', '/?revenus=1600',                      False),
    ('un-robot-inconnu', '/guides/',                            True),
]

def verdict(txt, robot, adresse):
    return Protego.parse(txt).can_fetch(B + adresse, robot)

print('=== Ancien fichier : ce que Google pouvait réellement explorer ===')
fuites = 0
for robot, adresse, attendu in CAS:
    obtenu = verdict(ANCIEN, robot, adresse)
    if obtenu != attendu:
        fuites += 1
        print(f'  ⚠️  {robot:18s} {adresse:38s} exploré alors qu\'il ne devait pas')
print(f'  → {fuites} fuite(s) dans l\'ancien fichier\n')

print('=== Nouveau fichier ===')
ok = 0
for robot, adresse, attendu in CAS:
    obtenu = verdict(NOUVEAU, robot, adresse)
    bon = obtenu == attendu
    ok += bon
    etat = 'exploration' if obtenu else 'interdiction'
    print(f'{"✅" if bon else "❌"} {robot:18s} {adresse:38s} {etat}')

s = Protego.parse(NOUVEAU)
attendu_sm = ['https://trouver-mon-ehpad.fr/sitemap.xml']
sm = list(s.sitemaps)
bon_sm = sm == attendu_sm
ok += bon_sm
print(f'{"✅" if bon_sm else "❌"} sitemap déclaré : {sm}')

total = len(CAS) + 1
print(f'\n{ok}/{total} contrôles du robots.txt OK')
print(f'régressions corrigées par rapport à l\'ancien fichier : {fuites}')
raise SystemExit(0 if ok == total else 1)
