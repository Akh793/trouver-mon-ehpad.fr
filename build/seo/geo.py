# -*- coding: utf-8 -*-
"""Référentiel géographique : régions, départements, libellés et articles.
Découpage administratif en vigueur depuis le 1er janvier 2016 (18 régions)."""

REGIONS = {
 'auvergne-rhone-alpes': ('Auvergne-Rhône-Alpes', ['01','03','07','15','26','38','42','43','63','69','73','74']),
 'bourgogne-franche-comte': ('Bourgogne-Franche-Comté', ['21','25','39','58','70','71','89','90']),
 'bretagne': ('Bretagne', ['22','29','35','56']),
 'centre-val-de-loire': ('Centre-Val de Loire', ['18','28','36','37','41','45']),
 'corse': ('Corse', ['2A','2B']),
 'grand-est': ('Grand Est', ['08','10','51','52','54','55','57','67','68','88']),
 'hauts-de-france': ('Hauts-de-France', ['02','59','60','62','80']),
 'ile-de-france': ('Île-de-France', ['75','77','78','91','92','93','94','95']),
 'normandie': ('Normandie', ['14','27','50','61','76']),
 'nouvelle-aquitaine': ('Nouvelle-Aquitaine', ['16','17','19','23','24','33','40','47','64','79','86','87']),
 'occitanie': ('Occitanie', ['09','11','12','30','31','32','34','46','48','65','66','81','82']),
 'pays-de-la-loire': ('Pays de la Loire', ['44','49','53','72','85']),
 'provence-alpes-cote-d-azur': ("Provence-Alpes-Côte d'Azur", ['04','05','06','13','83','84']),
 'guadeloupe': ('Guadeloupe', ['971']),
 'martinique': ('Martinique', ['972']),
 'guyane': ('Guyane', ['973']),
 'la-reunion': ('La Réunion', ['974']),
 'mayotte': ('Mayotte', ['976']),
}
# Collectivités hors régions (statuts particuliers)
COLLECTIVITES = {'975': 'Saint-Pierre-et-Miquelon', '977': 'Saint-Barthélemy', '978': 'Saint-Martin'}

DEPARTEMENTS = {
 '01':"Ain",'02':"Aisne",'03':"Allier",'04':"Alpes-de-Haute-Provence",'05':"Hautes-Alpes",
 '06':"Alpes-Maritimes",'07':"Ardèche",'08':"Ardennes",'09':"Ariège",'10':"Aube",'11':"Aude",
 '12':"Aveyron",'13':"Bouches-du-Rhône",'14':"Calvados",'15':"Cantal",'16':"Charente",
 '17':"Charente-Maritime",'18':"Cher",'19':"Corrèze",'21':"Côte-d'Or",'22':"Côtes-d'Armor",
 '23':"Creuse",'24':"Dordogne",'25':"Doubs",'26':"Drôme",'27':"Eure",'28':"Eure-et-Loir",
 '29':"Finistère",'2A':"Corse-du-Sud",'2B':"Haute-Corse",'30':"Gard",'31':"Haute-Garonne",
 '32':"Gers",'33':"Gironde",'34':"Hérault",'35':"Ille-et-Vilaine",'36':"Indre",'37':"Indre-et-Loire",
 '38':"Isère",'39':"Jura",'40':"Landes",'41':"Loir-et-Cher",'42':"Loire",'43':"Haute-Loire",
 '44':"Loire-Atlantique",'45':"Loiret",'46':"Lot",'47':"Lot-et-Garonne",'48':"Lozère",
 '49':"Maine-et-Loire",'50':"Manche",'51':"Marne",'52':"Haute-Marne",'53':"Mayenne",
 '54':"Meurthe-et-Moselle",'55':"Meuse",'56':"Morbihan",'57':"Moselle",'58':"Nièvre",'59':"Nord",
 '60':"Oise",'61':"Orne",'62':"Pas-de-Calais",'63':"Puy-de-Dôme",'64':"Pyrénées-Atlantiques",
 '65':"Hautes-Pyrénées",'66':"Pyrénées-Orientales",'67':"Bas-Rhin",'68':"Haut-Rhin",'69':"Rhône",
 '70':"Haute-Saône",'71':"Saône-et-Loire",'72':"Sarthe",'73':"Savoie",'74':"Haute-Savoie",
 '75':"Paris",'76':"Seine-Maritime",'77':"Seine-et-Marne",'78':"Yvelines",'79':"Deux-Sèvres",
 '80':"Somme",'81':"Tarn",'82':"Tarn-et-Garonne",'83':"Var",'84':"Vaucluse",'85':"Vendée",
 '86':"Vienne",'87':"Haute-Vienne",'88':"Vosges",'89':"Yonne",'90':"Territoire de Belfort",
 '91':"Essonne",'92':"Hauts-de-Seine",'93':"Seine-Saint-Denis",'94':"Val-de-Marne",'95':"Val-d'Oise",
 '971':"Guadeloupe",'972':"Martinique",'973':"Guyane",'974':"La Réunion",'976':"Mayotte",
 '975':"Saint-Pierre-et-Miquelon",
}

# Article et préposition de chaque département : le français est irrégulier, on ne devine pas.
OU_DEP = {
 '01':"dans l’Ain",'02':"dans l’Aisne",'03':"dans l’Allier",'04':"dans les Alpes-de-Haute-Provence",
 '05':"dans les Hautes-Alpes",'06':"dans les Alpes-Maritimes",'07':"en Ardèche",'08':"dans les Ardennes",
 '09':"en Ariège",'10':"dans l’Aube",'11':"dans l’Aude",'12':"dans l’Aveyron",'13':"dans les Bouches-du-Rhône",
 '14':"dans le Calvados",'15':"dans le Cantal",'16':"en Charente",'17':"en Charente-Maritime",
 '18':"dans le Cher",'19':"en Corrèze",'21':"en Côte-d’Or",'22':"dans les Côtes-d’Armor",
 '23':"dans la Creuse",'24':"en Dordogne",'25':"dans le Doubs",'26':"dans la Drôme",'27':"dans l’Eure",
 '28':"en Eure-et-Loir",'29':"dans le Finistère",'2A':"en Corse-du-Sud",'2B':"en Haute-Corse",
 '30':"dans le Gard",'31':"en Haute-Garonne",'32':"dans le Gers",'33':"en Gironde",'34':"dans l’Hérault",
 '35':"en Ille-et-Vilaine",'36':"dans l’Indre",'37':"en Indre-et-Loire",'38':"en Isère",'39':"dans le Jura",
 '40':"dans les Landes",'41':"en Loir-et-Cher",'42':"dans la Loire",'43':"en Haute-Loire",
 '44':"en Loire-Atlantique",'45':"dans le Loiret",'46':"dans le Lot",'47':"en Lot-et-Garonne",
 '48':"en Lozère",'49':"en Maine-et-Loire",'50':"dans la Manche",'51':"dans la Marne",'52':"en Haute-Marne",
 '53':"en Mayenne",'54':"en Meurthe-et-Moselle",'55':"dans la Meuse",'56':"dans le Morbihan",
 '57':"en Moselle",'58':"dans la Nièvre",'59':"dans le Nord",'60':"dans l’Oise",'61':"dans l’Orne",
 '62':"dans le Pas-de-Calais",'63':"dans le Puy-de-Dôme",'64':"dans les Pyrénées-Atlantiques",
 '65':"dans les Hautes-Pyrénées",'66':"dans les Pyrénées-Orientales",'67':"dans le Bas-Rhin",
 '68':"dans le Haut-Rhin",'69':"dans le Rhône",'70':"en Haute-Saône",'71':"en Saône-et-Loire",
 '72':"dans la Sarthe",'73':"en Savoie",'74':"en Haute-Savoie",'75':"à Paris",'76':"en Seine-Maritime",
 '77':"en Seine-et-Marne",'78':"dans les Yvelines",'79':"dans les Deux-Sèvres",'80':"dans la Somme",
 '81':"dans le Tarn",'82':"en Tarn-et-Garonne",'83':"dans le Var",'84':"dans le Vaucluse",'85':"en Vendée",
 '86':"dans la Vienne",'87':"en Haute-Vienne",'88':"dans les Vosges",'89':"dans l’Yonne",
 '90':"dans le Territoire de Belfort",'91':"dans l’Essonne",'92':"dans les Hauts-de-Seine",
 '93':"en Seine-Saint-Denis",'94':"dans le Val-de-Marne",'95':"dans le Val-d’Oise",
 '971':"en Guadeloupe",'972':"en Martinique",'973':"en Guyane",'974':"à La Réunion",
 '975':"à Saint-Pierre-et-Miquelon",'976':"à Mayotte",
}
OU_REGION = {
 'grand-est': "dans le Grand Est",
 'hauts-de-france': "dans les Hauts-de-France",
 'pays-de-la-loire': "dans les Pays de la Loire",
}

def region_de(dep):
    for slug, (nom, deps) in REGIONS.items():
        if dep in deps: return slug, nom
    return None, None
