# -*- coding: utf-8 -*-
"""Conversion Lambert-93 (EPSG:2154) → WGS84 (EPSG:4326), en Python pur.

Certaines sources publient les coordonnées en Lambert-93 sans le signaler : les
valeurs arrivent alors dans les colonnes lat/lon et placent l'établissement hors
de la Terre. La formule inverse de la projection conique conforme de Lambert est
entièrement déterministe ; l'implémenter ici évite d'ajouter une dépendance de
build pour dix-huit lignes, et rend la correction reproductible.

Paramètres officiels (IGN, RGF93 / Lambert-93) :
    ellipsoïde GRS80, a = 6378137, 1/f = 298.257222101
    latitudes standard 44° et 49°, origine 46°30' N, 3° E
    faux est 700 000 m, faux nord 6 600 000 m
"""
import math

A = 6378137.0
F = 1 / 298.257222101
E = math.sqrt(2 * F - F * F)          # première excentricité
PHI0 = math.radians(46.5)
PHI1, PHI2 = math.radians(44.0), math.radians(49.0)
LAMBDA0 = math.radians(3.0)
X0, Y0 = 700000.0, 6600000.0


def _m(phi):
    return math.cos(phi) / math.sqrt(1 - E * E * math.sin(phi) ** 2)


def _t(phi):
    return math.tan(math.pi / 4 - phi / 2) / ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2)


_N = (math.log(_m(PHI1)) - math.log(_m(PHI2))) / (math.log(_t(PHI1)) - math.log(_t(PHI2)))
_F = _m(PHI1) / (_N * _t(PHI1) ** _N)
_RHO0 = A * _F * _t(PHI0) ** _N


def vers_wgs84(x, y):
    """(est, nord) en mètres Lambert-93 → (latitude, longitude) en degrés."""
    dx, dy = x - X0, _RHO0 - (y - Y0)
    rho = math.copysign(math.hypot(dx, dy), _N)
    theta = math.atan2(dx, dy)
    t = (rho / (A * _F)) ** (1 / _N)
    phi = math.pi / 2 - 2 * math.atan(t)
    # convergence : quelques itérations suffisent pour descendre sous le millimètre
    for _ in range(12):
        s = E * math.sin(phi)
        phi2 = math.pi / 2 - 2 * math.atan(t * ((1 - s) / (1 + s)) ** (E / 2))
        if abs(phi2 - phi) < 1e-12:
            phi = phi2
            break
        phi = phi2
    return math.degrees(phi), math.degrees(theta / _N + LAMBDA0)


def est_lambert93(lat, lon):
    """Vrai si le couple ressemble à des mètres Lambert-93 et non à des degrés."""
    try:
        return abs(float(lat)) > 180 or abs(float(lon)) > 180
    except (TypeError, ValueError):
        return False


if __name__ == '__main__':
    # Cas de contrôle : coordonnées réellement présentes dans les données publiées,
    # comparées à la transformation de référence (pyproj) au moment de l'écriture.
    cas = [
        (810549.54, 6413785.23, 44.81441, 4.39836),     # Marcols-Les-Eaux (07)
        (573230.19, 6278681.62, 43.59585, 1.43048),     # Toulouse (31)
        (422504.56, 6426265.96, 44.87998, -0.51518),    # Lormont (33)
        (700000.0, 6600000.0, 46.5, 3.0),               # origine de la projection
    ]
    ok = 0
    for x, y, la, lo in cas:
        a, b = vers_wgs84(x, y)
        d = max(abs(a - la), abs(b - lo))
        bon = d < 1e-4
        ok += bon
        print('%s  %.5f, %.5f  (écart %.7f°)' % ('OK ' if bon else 'ÉCHEC', a, b, d))
    print('%d/%d' % (ok, len(cas)))
