/* Script commun aux pages de contenu : consentement, mesure d'usage, bandeau.
   Chargé en differé et mis en cache : il n'est téléchargé qu'une fois pour tout le site. */
(function () {
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied',
    ad_user_data: 'denied', ad_personalization: 'denied', wait_for_update: 500 });

  var KEY = 'mon_ehpad_consent', TTL = 182 * 24 * 3600 * 1000, choix = null;   // 6 mois, recommandation CNIL
  try { var b = localStorage.getItem(KEY); if (b) { var o = JSON.parse(b);
    if (o && o.v && Date.now() - o.t < TTL) choix = o.v; else localStorage.removeItem(KEY); } } catch (e) {}
  function applique(v) {
    gtag('consent', 'update', { analytics_storage: v === 'granted' ? 'granted' : 'denied' });
    dataLayer.push({ event: v === 'granted' ? 'consent_granted' : 'consent_denied' });
  }
  window.ME_consent = {
    get: function () { return choix; },
    set: function (v) { choix = v; try { localStorage.setItem(KEY, JSON.stringify({ v: v, t: Date.now() })); } catch (e) {} applique(v); },
    reset: function () { choix = null; try { localStorage.removeItem(KEY); } catch (e) {} }
  };
  if (choix) applique(choix);

  // Mesure d'usage : uniquement le type de page et le départ vers le calculateur. Aucune donnée personnelle.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-ev]');
    if (!a) return;
    dataLayer.push({ event: a.dataset.ev, seo_page: document.body.dataset.type || '',
                     seo_lieu: document.body.dataset.lieu || '' });
  });

  function pret() {
    var ban = document.getElementById('consent-banner');
    if (!ban) return;
    if (!choix) ban.hidden = false;
    var ok = document.getElementById('consent-accept'), non = document.getElementById('consent-refuse');
    if (ok) ok.addEventListener('click', function () { ME_consent.set('granted'); ban.hidden = true; });
    if (non) non.addEventListener('click', function () { ME_consent.set('denied'); ban.hidden = true; });
    document.querySelectorAll('[data-consent-open]').forEach(function (a) {
      a.addEventListener('click', function (ev) { ev.preventDefault(); ME_consent.reset(); ban.hidden = false; });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pret); else pret();
})();

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
