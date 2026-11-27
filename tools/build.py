# -*- coding: utf-8 -*-
"""Gera o site The Love Theory nas duas línguas: EN na raiz, PT em /pt/. Rode: python tools/build.py"""
import os, sys, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data_en, data_pt

SITE = "https://lovetheory.biblioverse.org"
HOST = "lovetheory.biblioverse.org"
CF_TOKEN = "a301fcc083604a61ab8be15f203bed7c"  # Cloudflare Web Analytics (conta 2, Gdayjulio); vazio = sem beacon
CF_SNIPPET = ("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
              "data-cf-beacon='{\"token\": \"%s\"}'></script><!-- End Cloudflare Web Analytics -->" % CF_TOKEN) if CF_TOKEN else ""
BUILT = datetime.date.today().isoformat()
FONTS = "https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=DynaPuff:wght@700&family=DM+Sans:wght@400;600;700&display=swap"
ORG = {"@type": "Organization", "@id": "https://biblioverse.org/#organization", "name": "BiblioVerse", "url": "https://biblioverse.org"}
LANGS = [("en", data_en, ""), ("pt", data_pt, "pt/")]

try:
    import rcssmin, rjsmin
except ImportError:
    rcssmin = rjsmin = None


def e(s):
    return html.escape(str(s), quote=True)


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


LOGO = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>')
FLOWER = '<svg viewBox="0 0 200 250" aria-hidden="true"> <defs> <radialGradient id="gC" cx="50%" cy="48%" r="55%"><stop offset="0" stop-color="#fffdf6"/><stop offset=".22" stop-color="#fbe7f2"/><stop offset=".55" stop-color="#d9b8ee"/><stop offset=".85" stop-color="#9c78d6"/><stop offset="1" stop-color="#7c56bf"/></radialGradient> <radialGradient id="gT" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff6c4"/><stop offset=".55" stop-color="#fffaf0"/><stop offset="1" stop-color="#fbe7f2" stop-opacity="0"/></radialGradient> <linearGradient id="la" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#6f8a47"/><stop offset="1" stop-color="#a7bd78"/></linearGradient> <linearGradient id="lb" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#4d6532"/><stop offset="1" stop-color="#7e9a55"/></linearGradient> <clipPath id="lc"><path d="M0,0 C-9,7 -33,11 -39,-7 C-44,-26 -27,-49 -6,-61 C-3,-64 -1,-68 0,-74 C1,-68 3,-64 6,-61 C27,-49 44,-26 39,-7 C33,11 9,7 0,0Z"/></clipPath> <linearGradient id="gB" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#8b66c8"/><stop offset="1" stop-color="#e8d6f6"/></linearGradient> </defs> <path d="M100 146 C97 172 110 196 103 248" stroke="#4d6532" stroke-width="4.5" fill="none" stroke-linecap="round"/> <path d="M104 196 C122 192 140 182 150 166" stroke="#4d6532" stroke-width="2.6" fill="none" stroke-linecap="round"/> <path d="M105 220 C88 216 70 206 58 190" stroke="#4d6532" stroke-width="2.6" fill="none" stroke-linecap="round"/> <path d="M101 166 C120 158 144 144 158 126" stroke="#4d6532" stroke-width="2" fill="none" stroke-linecap="round"/> <g transform="translate(150 166) rotate(52) scale(0.82)"><path d="M0,0 C-9,7 -33,11 -39,-7 C-44,-26 -27,-49 -6,-61 C-3,-64 -1,-68 0,-74 C-2,-48 -3,-24 0,0Z" fill="url(#la)"/><path d="M0,0 C-3,-24 -2,-48 0,-74 C1,-68 3,-64 6,-61 C27,-49 44,-26 39,-7 C33,11 9,7 0,0Z" fill="url(#lb)"/><g stroke="#3f5a2a" stroke-width=".9" fill="none" opacity=".55" clip-path="url(#lc)"><path d="M-1.5,-12 Q-16.5,-17 -30.0,-20.5" /><path d="M-1.5,-12 Q16.5,-17 30.0,-20.5" /><path d="M-1.5,-24 Q-16.5,-31 -30.0,-35.9" /><path d="M-1.5,-24 Q16.5,-31 30.0,-35.9" /><path d="M-1.5,-37 Q-13.2,-45 -24.0,-50.6" /><path d="M-1.5,-37 Q13.2,-45 24.0,-50.6" /><path d="M-1.5,-50 Q-8.2,-57 -15.0,-61.9" /><path d="M-1.5,-50 Q8.2,-57 15.0,-61.9" /></g><path d="M0,0 C-2,-24 -2,-48 0,-72" stroke="#e9f0d6" stroke-width="1.6" fill="none" opacity=".8"/><path d="M0,0 C-9,7 -33,11 -39,-7 C-44,-26 -27,-49 -6,-61 C-3,-64 -1,-68 0,-74 C1,-68 3,-64 6,-61 C27,-49 44,-26 39,-7 C33,11 9,7 0,0Z" fill="none" stroke="#33441f" stroke-width="1.3" stroke-linejoin="round"/></g> <g transform="translate(58 190) rotate(-58) scale(0.9)"><path d="M0,0 C-9,7 -33,11 -39,-7 C-44,-26 -27,-49 -6,-61 C-3,-64 -1,-68 0,-74 C-2,-48 -3,-24 0,0Z" fill="url(#la)"/><path d="M0,0 C-3,-24 -2,-48 0,-74 C1,-68 3,-64 6,-61 C27,-49 44,-26 39,-7 C33,11 9,7 0,0Z" fill="url(#lb)"/><g stroke="#3f5a2a" stroke-width=".9" fill="none" opacity=".55" clip-path="url(#lc)"><path d="M-1.5,-12 Q-16.5,-17 -30.0,-20.5" /><path d="M-1.5,-12 Q16.5,-17 30.0,-20.5" /><path d="M-1.5,-24 Q-16.5,-31 -30.0,-35.9" /><path d="M-1.5,-24 Q16.5,-31 30.0,-35.9" /><path d="M-1.5,-37 Q-13.2,-45 -24.0,-50.6" /><path d="M-1.5,-37 Q13.2,-45 24.0,-50.6" /><path d="M-1.5,-50 Q-8.2,-57 -15.0,-61.9" /><path d="M-1.5,-50 Q8.2,-57 15.0,-61.9" /></g><path d="M0,0 C-2,-24 -2,-48 0,-72" stroke="#e9f0d6" stroke-width="1.6" fill="none" opacity=".8"/><path d="M0,0 C-9,7 -33,11 -39,-7 C-44,-26 -27,-49 -6,-61 C-3,-64 -1,-68 0,-74 C1,-68 3,-64 6,-61 C27,-49 44,-26 39,-7 C33,11 9,7 0,0Z" fill="none" stroke="#33441f" stroke-width="1.3" stroke-linejoin="round"/></g> <g transform="translate(158 126) rotate(52)"><path d="M0,0 C-7,-10 -6,-30 0,-44 C6,-30 7,-10 0,0Z" fill="url(#gB)" stroke="#5a3d8a" stroke-width="1.1"/><path d="M0,-4 C3,-16 2,-28 0,-42" stroke="#fdf0f7" stroke-width="1.4" fill="none" opacity=".8"/><path d="M-5,2 C-3,-6 3,-6 5,2 C2,5 -2,5 -5,2Z" fill="#7e9a55" stroke="#33441f" stroke-width=".9"/></g> <path d="M86 146 C92 154 108 154 114 146 C110 158 90 158 86 146Z" fill="#7e9a55" stroke="#33441f" stroke-width="1"/> <path d="M100.0,33.0 L102.0,33.0 L104.0,33.2 L106.0,33.5 L107.9,33.9 L109.9,34.4 L111.7,35.0 L113.6,35.8 L115.4,36.5 L117.1,37.4 L118.8,38.3 L120.4,39.2 L122.0,40.2 L123.6,41.2 L125.1,42.2 L126.6,43.1 L128.0,44.1 L129.5,45.1 L130.9,46.1 L132.4,47.0 L133.9,47.9 L135.3,48.8 L136.8,49.7 L138.3,50.6 L139.8,51.5 L141.4,52.4 L143.0,53.3 L144.5,54.2 L146.1,55.2 L147.6,56.2 L149.2,57.3 L150.7,58.4 L152.2,59.5 L153.6,60.7 L154.9,62.0 L156.2,63.4 L157.4,64.8 L158.4,66.3 L159.4,67.8 L160.2,69.4 L160.9,71.0 L161.4,72.7 L161.8,74.3 L162.1,76.1 L162.3,77.8 L162.3,79.5 L162.2,81.2 L162.0,83.0 L161.7,84.7 L161.3,86.3 L160.8,88.0 L160.3,89.6 L159.7,91.2 L159.1,92.8 L158.5,94.4 L157.8,95.9 L157.2,97.4 L156.6,98.9 L155.9,100.4 L155.4,101.8 L154.8,103.3 L154.2,104.8 L153.7,106.3 L153.2,107.8 L152.7,109.3 L152.2,110.9 L151.6,112.4 L151.1,114.0 L150.5,115.6 L149.9,117.1 L149.2,118.7 L148.4,120.3 L147.6,121.9 L146.7,123.4 L145.7,124.9 L144.6,126.3 L143.4,127.7 L142.1,129.1 L140.7,130.3 L139.2,131.5 L137.6,132.5 L136.0,133.5 L134.2,134.4 L132.4,135.1 L130.5,135.8 L128.6,136.3 L126.7,136.8 L124.7,137.1 L122.7,137.4 L120.8,137.6 L118.8,137.7 L116.8,137.8 L114.9,137.8 L112.9,137.8 L111.0,137.8 L109.2,137.7 L107.3,137.7 L105.5,137.6 L103.6,137.6 L101.8,137.5 L100.0,137.5 L98.2,137.5 L96.4,137.6 L94.5,137.6 L92.7,137.7 L90.8,137.7 L89.0,137.8 L87.1,137.8 L85.1,137.8 L83.2,137.8 L81.2,137.7 L79.2,137.6 L77.3,137.4 L75.3,137.1 L73.3,136.8 L71.4,136.3 L69.5,135.8 L67.6,135.1 L65.8,134.4 L64.0,133.5 L62.4,132.5 L60.8,131.5 L59.3,130.3 L57.9,129.1 L56.6,127.7 L55.4,126.3 L54.3,124.9 L53.3,123.4 L52.4,121.9 L51.6,120.3 L50.8,118.7 L50.1,117.1 L49.5,115.6 L48.9,114.0 L48.4,112.4 L47.8,110.9 L47.3,109.3 L46.8,107.8 L46.3,106.3 L45.8,104.8 L45.2,103.3 L44.6,101.8 L44.1,100.4 L43.4,98.9 L42.8,97.4 L42.2,95.9 L41.5,94.4 L40.9,92.8 L40.3,91.2 L39.7,89.6 L39.2,88.0 L38.7,86.3 L38.3,84.7 L38.0,83.0 L37.8,81.2 L37.7,79.5 L37.7,77.8 L37.9,76.1 L38.2,74.3 L38.6,72.7 L39.1,71.0 L39.8,69.4 L40.6,67.8 L41.6,66.3 L42.6,64.8 L43.8,63.4 L45.1,62.0 L46.4,60.7 L47.8,59.5 L49.3,58.4 L50.8,57.3 L52.4,56.2 L53.9,55.2 L55.5,54.2 L57.0,53.3 L58.6,52.4 L60.2,51.5 L61.7,50.6 L63.2,49.7 L64.7,48.8 L66.1,47.9 L67.6,47.0 L69.1,46.1 L70.5,45.1 L72.0,44.1 L73.4,43.1 L74.9,42.2 L76.4,41.2 L78.0,40.2 L79.6,39.2 L81.2,38.3 L82.9,37.4 L84.6,36.5 L86.4,35.8 L88.3,35.0 L90.1,34.4 L92.1,33.9 L94.0,33.5 L96.0,33.2 L98.0,33.0 L100.0,33.0Z" fill="url(#gC)" stroke="#5a3d8a" stroke-width="1.6" stroke-linejoin="round"/> <path d="M100,88 Q118.8,62.7 134.6,47.0" stroke="#7b55b8" stroke-width=".8" fill="none" opacity=".35"/><path d="M100,88 Q130.4,93.5 156.0,103.6" stroke="#7b55b8" stroke-width=".8" fill="none" opacity=".35"/><path d="M100,88 Q100.0,112.5 100.0,138.6" stroke="#7b55b8" stroke-width=".8" fill="none" opacity=".35"/><path d="M100,88 Q69.6,93.5 44.0,103.6" stroke="#7b55b8" stroke-width=".8" fill="none" opacity=".35"/><path d="M100,88 Q81.2,62.7 65.4,47.0" stroke="#7b55b8" stroke-width=".8" fill="none" opacity=".35"/><path d="M100,88 L100.0,34.1" stroke="#fdf0f7" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M100,88 L100.0,38.5" stroke="#8a64c4" stroke-width="1.2" opacity=".45"/><path d="M100,88 L159.7,71.3" stroke="#fdf0f7" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M100,88 L154.8,72.7" stroke="#8a64c4" stroke-width="1.2" opacity=".45"/><path d="M100,88 L136.9,131.6" stroke="#fdf0f7" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M100,88 L133.9,128.1" stroke="#8a64c4" stroke-width="1.2" opacity=".45"/><path d="M100,88 L63.1,131.6" stroke="#fdf0f7" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M100,88 L66.1,128.1" stroke="#8a64c4" stroke-width="1.2" opacity=".45"/><path d="M100,88 L40.3,71.3" stroke="#fdf0f7" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M100,88 L45.2,72.7" stroke="#8a64c4" stroke-width="1.2" opacity=".45"/> <path d="M100.0,55.9 L101.2,55.9 L102.5,56.0 L103.7,56.1 L104.9,56.3 L106.2,56.5 L107.4,56.8 L108.5,57.2 L109.7,57.5 L110.8,57.9 L112.0,58.4 L113.1,58.8 L114.1,59.3 L115.2,59.8 L116.2,60.3 L117.2,60.9 L118.3,61.4 L119.2,62.0 L120.2,62.6 L121.2,63.2 L122.2,63.8 L123.1,64.4 L124.1,65.0 L125.0,65.6 L125.9,66.2 L126.9,66.9 L127.8,67.6 L128.7,68.3 L129.6,69.0 L130.4,69.7 L131.3,70.4 L132.1,71.2 L132.9,72.0 L133.7,72.9 L134.4,73.7 L135.1,74.6 L135.7,75.5 L136.3,76.5 L136.8,77.5 L137.3,78.4 L137.7,79.5 L138.1,80.5 L138.4,81.5 L138.6,82.6 L138.8,83.6 L138.9,84.7 L139.0,85.8 L139.0,86.8 L138.9,87.9 L138.8,89.0 L138.7,90.0 L138.5,91.0 L138.3,92.1 L138.1,93.1 L137.8,94.1 L137.5,95.1 L137.2,96.1 L136.9,97.1 L136.6,98.1 L136.2,99.0 L135.9,100.0 L135.5,101.0 L135.1,101.9 L134.7,102.9 L134.3,103.9 L133.8,104.8 L133.4,105.8 L132.9,106.7 L132.4,107.7 L131.9,108.6 L131.3,109.6 L130.7,110.5 L130.0,111.4 L129.4,112.3 L128.6,113.1 L127.9,114.0 L127.0,114.8 L126.2,115.5 L125.3,116.3 L124.3,117.0 L123.3,117.6 L122.3,118.2 L121.2,118.8 L120.1,119.3 L119.0,119.8 L117.9,120.2 L116.7,120.6 L115.5,120.9 L114.4,121.2 L113.2,121.4 L112.0,121.6 L110.8,121.8 L109.5,122.0 L108.3,122.1 L107.1,122.2 L105.9,122.3 L104.7,122.3 L103.6,122.4 L102.4,122.4 L101.2,122.4 L100.0,122.4 L98.8,122.4 L97.6,122.4 L96.4,122.4 L95.3,122.3 L94.1,122.3 L92.9,122.2 L91.7,122.1 L90.5,122.0 L89.2,121.8 L88.0,121.6 L86.8,121.4 L85.6,121.2 L84.5,120.9 L83.3,120.6 L82.1,120.2 L81.0,119.8 L79.9,119.3 L78.8,118.8 L77.7,118.2 L76.7,117.6 L75.7,117.0 L74.7,116.3 L73.8,115.5 L73.0,114.8 L72.1,114.0 L71.4,113.1 L70.6,112.3 L70.0,111.4 L69.3,110.5 L68.7,109.6 L68.1,108.6 L67.6,107.7 L67.1,106.7 L66.6,105.8 L66.2,104.8 L65.7,103.9 L65.3,102.9 L64.9,101.9 L64.5,101.0 L64.1,100.0 L63.8,99.0 L63.4,98.1 L63.1,97.1 L62.8,96.1 L62.5,95.1 L62.2,94.1 L61.9,93.1 L61.7,92.1 L61.5,91.0 L61.3,90.0 L61.2,89.0 L61.1,87.9 L61.0,86.8 L61.0,85.8 L61.1,84.7 L61.2,83.6 L61.4,82.6 L61.6,81.5 L61.9,80.5 L62.3,79.5 L62.7,78.4 L63.2,77.5 L63.7,76.5 L64.3,75.5 L64.9,74.6 L65.6,73.7 L66.3,72.9 L67.1,72.0 L67.9,71.2 L68.7,70.4 L69.6,69.7 L70.4,69.0 L71.3,68.3 L72.2,67.6 L73.1,66.9 L74.1,66.2 L75.0,65.6 L75.9,65.0 L76.9,64.4 L77.8,63.8 L78.8,63.2 L79.8,62.6 L80.8,62.0 L81.7,61.4 L82.8,60.9 L83.8,60.3 L84.8,59.8 L85.9,59.3 L86.9,58.8 L88.0,58.4 L89.2,57.9 L90.3,57.5 L91.5,57.2 L92.6,56.8 L93.8,56.5 L95.1,56.3 L96.3,56.1 L97.5,56.0 L98.8,55.9 L100.0,55.9Z" fill="url(#gT)" opacity=".9"/> <ellipse cx="100" cy="89" rx="9" ry="7.5" fill="#fff3b0" stroke="#e6c870" stroke-width="1"/> <circle cx="97.5" cy="87" r="1.6" fill="#f6f0d6"/><circle cx="102.5" cy="88" r="1.6" fill="#f6f0d6"/><circle cx="100" cy="91" r="1.6" fill="#f6f0d6"/> </svg>'


class Site:
    """Uma língua: o módulo de dados, o prefixo de pasta e os caminhos."""

    def __init__(self, code, D, prefix):
        self.code, self.D, self.prefix = code, D, prefix
        self.P = D.PATHS
        self.other = data_pt if code == "en" else data_en
        self.other_prefix = "pt/" if code == "en" else ""

    def url(self, path):
        return f"{SITE}/{self.prefix}" if path == "index.html" else f"{SITE}/{self.prefix}{path}"

    def prop_path(self, p):
        return f"{self.D.PROP_PREFIX}{p['slug']}.html"

    def other_path(self, path):
        """A mesma página na outra língua."""
        D, O = self.D, self.other
        for k, v in D.PATHS.items():
            if v == path:
                return O.PATHS[k]
        if path.startswith(D.PROP_PREFIX):
            slug = path[len(D.PROP_PREFIX):-5]
            for i, p in enumerate(D.PROPS):
                if p["slug"] == slug:
                    return f"{O.PROP_PREFIX}{O.PROPS[i]['slug']}.html"
        return "index.html"

    def href(self, k):
        """Link interno por chave; a home aponta para a pasta, nunca para index.html."""
        return "./" if k == "home" else self.P[k]

    def page(self, path, title, desc, body, active=None, noindex=False, ld_extra=None):
        D, P, PG = self.D, self.P, self.D.PAGES
        url = self.url(path)
        op = self.other_path(path)
        other_url = f"{SITE}/{self.other_prefix}" + ("" if op == "index.html" else op)
        en_url, pt_url = (url, other_url) if self.code == "en" else (other_url, url)
        other_hl = "pt-BR" if self.code == "en" else "en"
        nav = "".join(f'<a href="{self.href(k)}"{" class=on aria-current=page" if k == active else ""}>{e(t)}</a>' for k, t in D.NAV)
        home = f"{SITE}/{self.prefix}"
        crumbs = [(dict(D.NAV)["home"], home)]
        if active == "theory" and path != P["theory"]:
            crumbs.append((dict(D.NAV)["theory"], self.url(P["theory"])))
        if path != "index.html":
            crumbs.append((title, url))
        graph = [
            {"@type": "WebPage", "@id": url + "#page", "name": title, "description": desc, "url": url, "inLanguage": D.LANG,
             "dateModified": BUILT, "isPartOf": {"@id": f"{home}#website"}, "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
             "primaryImageOfPage": {"@type": "ImageObject", "url": f"{SITE}/{self.og_file()}", "width": 1200, "height": 630}},
            {"@type": "WebSite", "@id": f"{home}#website", "name": D.SITE_NAME, "url": home, "inLanguage": D.LANG,
             "description": D.DESCRIPTION, "publisher": {"@id": ORG["@id"]}}, ORG]
        if len(crumbs) > 1:
            graph.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
        graph += ld_extra or []
        ld = {"@context": "https://schema.org", "@graph": graph}
        uses_tool = 'data-tool="' in body
        scripts = (f'<script src="/assets/data-{self.code}.js?v={BUILT}" defer></script>\n<script src="/assets/app.min.js?v={BUILT}" defer></script>\n') if uses_tool else ""
        og_img = f"{SITE}/{self.og_file()}"
        full_title = title if D.SITE_NAME in title else f"{title} · {D.SITE_NAME}"
        return f"""<!doctype html>
<html lang="{D.LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{'noindex' if noindex else 'index, follow, max-image-preview:large'}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="pt-BR" href="{pt_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{D.SITE_NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta property="og:image:alt" content="{e(PG['og_alt'])}">
<meta property="og:locale" content="{'en_US' if self.code == 'en' else 'pt_BR'}">
<meta property="og:locale:alternate" content="{'pt_BR' if self.code == 'en' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_img}">
<meta name="twitter:image:alt" content="{e(PG['og_alt'])}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="theme-color" content="#f3b4cc">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.min.css?v={BUILT}">
{scripts}<script src="https://biblioverse.org/superbar.js" defer></script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{e(PG['skip'])}</a>
<nav id="bvbar" class="bvbar" data-current="lovetheory" data-bg="#2a1d2c" data-fg="#ffffff" data-accent="#b8236f" aria-label="BiblioVerse" style="position:fixed;top:0;left:0;right:0;height:36px;z-index:9000;background:#2a1d2c"><a href="https://biblioverse.org" style="color:#fff;line-height:36px;padding:0 14px;font-weight:700;text-decoration:none">BiblioVerse</a></nav>
<header class="nav"><div class="wrap"><a class="logo" href="./" aria-label="{e(PG['home_aria'])}"><span class="mark">{LOGO}</span><span class="t">{D.SITE_NAME}</span></a><nav class="menu" aria-label="{e(PG['nav_aria'])}">{nav}<a class="lang" href="/{self.other_prefix}{'' if op == 'index.html' else op}" hreflang="{other_hl}" lang="{other_hl}" aria-label="{e(PG['lang_aria'])}">{e(D.SWITCH_LABEL)}</a></nav></div></header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="foot"><div class="wrap"><p class="script">{e(PG['footer'])}</p><p><a href="{P['glossary']}">{e(PG['glossary_link'])}</a> · <a href="{P['about']}">{e(PG['about'])}</a> · <a href="{P['privacy']}">{e(PG['privacy_link'])}</a> · <a href="https://biblioverse.org">BiblioVerse</a> · <small>{e(PG['copyright'])}</small></p></div></footer>
{CF_SNIPPET}
</body>
</html>
"""

    # ------------------------------------------------------------ helpers
    def page_hero(self, kicker, title, lead):
        return f'<section class="wrap page-hero"><p class="kicker">{e(kicker)}</p><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></section>'

    def cards(self, items, cls="g3", big=False):
        out = []
        for num, h3, p in items:
            out.append(f'<div class="card{" big" if big else ""}">{f"<p class=num>{e(num)}</p>" if num else ""}<h3>{e(h3)}</h3><p>{e(p)}</p></div>')
        return f'<div class="grid {cls}">{"".join(out)}</div>'

    def og_file(self):
        return "og-image.png" if self.code == "en" else "og-image-pt.png"

    def section(self, title, inner, lead=None, cls="", sid=None, sr=False):
        h2 = f'<h2{" class=sr-only" if sr else ""}>{e(title)}</h2>' if title else ""
        return f'<section class="section {cls}"{f" id={sid}" if sid else ""}><div class="wrap">{h2}{f"<p class=lead>{e(lead)}</p>" if lead else ""}{inner}</div></section>'

    def tool_shell(self, tool):
        PG = self.D.PAGES
        return f'<div class="wrap tool"><div id="app" data-tool="{tool}"><noscript><div class="note">{e(PG["noscript"])}</div></noscript><p class="muted">{e(PG["loading"])}</p></div></div>'

    def table(self, headers, rows):
        th = "".join(f"<th>{e(h)}</th>" for h in headers)
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<div class="tbl"><table><tr>{th}</tr>{body}</table></div>'

    def out(self, path, content):
        write(self.prefix + path, content)

    # ------------------------------------------------------------ pages
    def build_home(self):
        D, P, PG, H = self.D, self.P, self.D.PAGES, self.D.HOME
        tools = "".join(f'<a class="petal" href="{P[t["key"]]}"><span class="k">{e(t["kicker"])}</span><h3>{e(t["name"])}</h3><p>{e(t["text"])}</p><span class="go">{e(PG["open"])}</span></a>' for t in D.TOOLS)
        body = f'''<section class="collage">
<div class="win hero-win tilt-l"><div class="win-bar"><i></i><i></i><i></i><span>{e(PG["studio"])}</span></div><div class="win-body">
<p class="kicker">{e(H["kicker"])}</p><h1>{e(H["title"])}</h1><p class="sub">{e(H["title2"])}</p><p class="lead">{e(H["lead"])}</p>
<div class="row" style="margin-top:22px"><a class="btn" href="{P['scale']}">{e(PG["do_scale"])}</a><a class="btn ghost" href="{P['theory']}">{e(PG["read_theory"])}</a></div></div></div>
<div class="frame-card tx-stitch tilt-r"><span class="tape r"></span><div class="oval">{FLOWER}</div><p class="cap">{e(PG["oval_caption"])}</p></div>
<div class="lace-card tx-lace tilt-l"><span class="tape"></span><div class="in"><h2>{e(H["privacy"].split(".")[0])}</h2><p>{e(H["privacy"])} <a href="{P['privacy']}">{e(PG['privacy_link'])} →</a></p></div></div>
</section>'''
        body += self.section(PG["tools_title"], f'<div class="petals">{tools}</div>')
        body += self.section(H["independence_title"], f'<div class="card big pink"><p class="lead" style="margin:0;max-width:none">{e(H["independence"])}</p></div>')
        self.out("index.html", self.page("index.html", PG["home_title"], D.DESCRIPTION, body, "home"))

    def build_theory(self):
        D, P, T = self.D, self.P, self.D.PAGES["theory"]
        props = ""
        for gid, gname in D.GROUPS:
            ps = [p for p in D.PROPS if p["group"] == gid]
            props += f'<h3 style="margin-top:28px">{e(gname)}</h3><div class="grid g3">' + "".join(
                f'<a class="card" href="{self.prop_path(p)}"><p class="num">{D.PROPS.index(p)+1:02d}</p><h3>{e(p["name"])}</h3><p class="small">{e(p["lead"])}</p></a>' for p in ps) + "</div>"
        idx = '<div class="grid g4">' + "".join(f'<a class="card" href="{P[k]}"><h3>{e(t)}</h3><p class="small">{e(d)}</p></a>' for k, t, d in T["pages"]) + "</div>"
        H = self.D.HOME
        intro = self.section(T["intro_title"], '<div class="card big prose">' + "".join(f"<p>{e(t)}</p>" for t in T["intro"]) + '</div>')
        thesis = self.section(T["method_title"], self.cards([(f"{i+1}.", t, p) for i, (t, p) in enumerate(H["thesis"])], "g4"))
        body = self.page_hero(T["kicker"], T["title"], T["lead"]) + intro + thesis + self.section(self.D.PAGES["theory_pages"], idx) + self.section(T["props_title"], props, T["props_lead"], sid="properties")
        self.out(P["theory"], self.page(P["theory"], T["title"], T["desc"], body, "theory"))

    def build_props(self):
        D, P, X = self.D, self.P, self.D.PAGES["prop"]
        selflove_name = self.D.PAGES["tools"]["selflove"][0]
        for i, p in enumerate(D.PROPS):
            prev, nxt = D.PROPS[i - 1], D.PROPS[(i + 1) % len(D.PROPS)]
            gname = dict(D.GROUPS)[p["group"]]
            flags = [f for f in D.FLAGS if p["key"] in f["props"]]
            body = self.page_hero(X["kicker"].format(n=f"{i+1:02d}", group=gname), p["name"], p["lead"])
            subs = "".join(f"<li>{e(s)}</li>" for s in p["subs"])
            roots = "".join(f"<li>{e(r)}</li>" for r in p["roots"])
            body += self.section(None, f'<div class="grid g2"><div class="card big"><p class="num">{e(X["subs"])}</p><ul>{subs}</ul></div><div class="card big soft"><p class="num">{e(X["note"])}</p><p>{e(p["note"])}</p></div></div>')
            body += self.section(X["from_title"], f'<p class="lead">{e(X["from_lead"].format(name=p["name"]))}</p><div class="card"><ul>{roots}</ul></div>')
            body += self.section(X["how_title"], f'<div class="grid g2"><div class="card"><p class="num">{e(X["aggr"])}</p><p>{e(p["expr"][0])}</p></div><div class="card"><p class="num">{e(X["peaceful"])}</p><p>{e(p["expr"][1])}</p></div></div><p class="muted">{e(X["how_note"])}</p>')
            if flags:
                fl = "".join(f'<li><span class="tag {f["sign"]}">{f["sign"]}</span> {e(f["text"])} <span class="muted">· {e(X["false_"])} {e(f["false_when"])}</span></li>' for f in flags)
                body += self.section(X["flags_title"], f'<ul class="flag-list">{fl}</ul><p><a href="{P["flags"]}">{e(X["all_flags"])}</a></p>')
            body += self.section(X["inward_title"], f'<div class="card big pink"><p class="num">{e(selflove_name)}</p><p class="lead" style="margin:0;max-width:none">{e(p["selflove"])}</p></div>')
            body += self.section(None, f'<div class="row"><a class="btn" href="{P["scale"]}">{e(X["measure"].format(name=p["name"]))}</a><a class="btn ghost" href="{self.prop_path(prev)}">← {e(prev["name"])}</a><a class="btn ghost" href="{self.prop_path(nxt)}">{e(nxt["name"])} →</a></div>')
            term = {"@type": "DefinedTerm", "@id": self.url(self.prop_path(p)) + "#term", "name": p["name"], "description": p["lead"] + " " + "; ".join(p["subs"]),
                    "inDefinedTermSet": {"@id": self.url(P["glossary"]) + "#terms"}, "url": self.url(self.prop_path(p))}
            self.out(self.prop_path(p), self.page(self.prop_path(p), p["name"], X["desc"].format(name=p["name"], lead=p["lead"]), body, "theory", ld_extra=[term]))

    def build_model(self):
        P, M, X = self.P, self.D.MODEL_PAGE, self.D.PAGES["model"]
        terms = self.table(X["th"], [(f"<b>{e(a)}</b>", e(b), e(c)) for a, b, c in M["terms"]])
        body = self.page_hero(X["kicker"], M["title"], M["lead"]) + self.section(X["vocab"], terms) + self.section(X["rules"], self.cards([(None, a, b) for a, b in M["rules"]], "g2"))
        body += self.section(M["sources_title"], self.cards([(None, a, b) for a, b in M["sources"]], "g3") + f'<p class="lead" style="margin-top:18px">{e(M["sources_end"])}</p>', M["sources_lead"])
        self.out(P["model"], self.page(P["model"], M["title"], M["lead"], body, "theory"))

    def build_mechanisms(self):
        D, P, X = self.D, self.P, self.D.PAGES["mech"]
        j = self.table(X["th"], [(f"<b>{e(r[0])}</b>" + (f"<br><span class=muted>{e(r[1])}</span>" if r[1] else ""), e(r[2]), e(r[3]), e(r[4]), e(r[5]), e(r[6])) for r in D.JEALOUSY])
        ex = self.table(X["expr_th"], [(f"<b>{e(a)}</b>", e(b), e(c)) for a, b, c in D.EXPRESSION])
        roots = '<div class="grid g3">' + "".join(f'<div class="card"><h3 class="h4">{e(p["name"])}</h3><ul class="small">{"".join(f"<li>{e(r)}</li>" for r in p["roots"])}</ul></div>' for p in D.PROPS) + "</div>"
        body = self.page_hero(X["kicker"], X["title"], X["lead"])
        body += self.section(self.D.PAGES["mech_chain_title"], f'<div class="card big pink"><h3>{e(X["chain"])}</h3><p>{e(X["chain_text"])}</p></div>' + self.cards(X["rules"], "g3"), sr=True)
        body += self.section(X["sig_title"], self.cards(X["sig"], "g3"), X["sig_lead"])
        body += self.section(X["case_title"], j + f'<div class="note">{e(X["case_note"])}</div>' + self.cards([(None, a, b) for a, b in X["case_cards"]], "g3"), X["case_lead"])
        body += self.section(X["expr_title"], ex + '<div class="grid g2">' + "".join(f'<div class="card"><h3 class="h4">{e(a)}</h3><p>{e(b)}</p></div>' for a, b in X["expr_cards"]) + "</div>", X["expr_lead"])
        body += self.section(X["roots_title"], roots)
        self.out(P["mechanisms"], self.page(P["mechanisms"], X["title"], X["desc"], body, "theory"))

    def build_modulators(self):
        D, P, X = self.D, self.P, self.D.PAGES["modul"]
        t = self.table(X["th"], [(f"<b>{e(a)}</b>", e(b), f"<span class=muted>{e(c)}</span>") for a, b, c in D.MODULATORS])
        body = self.page_hero(X["kicker"], X["title"], X["lead"]) + self.section(None, t + f'<div class="note">{e(X["note"])}</div>')
        self.out(P["modulators"], self.page(P["modulators"], X["title"], X["desc"], body, "theory"))

    def build_time(self):
        D, P, T, X = self.D, self.P, self.D.TIME_PAGE, self.D.PAGES["time"]
        body = self.page_hero(X["kicker"], T["title"], T["lead"])
        body += self.section(T["does_title"], self.cards([(None, a, b) for a, b in T["does"]], "g2"))
        body += self.section(T["keeps_title"], self.cards([(None, a, b) for a, b in T["keeps"]], "g3"))
        tp = [p for p in D.PROPS if p["key"] == "temporalidade"][0]
        body += self.section(None, f'<div class="row"><a class="btn" href="{P["scale"]}">{e(X["btn1"])}</a><a class="btn ghost" href="{self.prop_path(tp)}">{e(X["btn2"])}</a></div>')
        self.out(P["time"], self.page(P["time"], T["title"], X["desc"], body, "theory"))

    def build_flags(self):
        D, P, X = self.D, self.P, self.D.PAGES["flags"]
        by_key = {p["key"]: p for p in D.PROPS}
        rows = [(f'<span class="tag {f["sign"]}">{f["sign"]}</span>', e(f["text"]), ", ".join(e(by_key[k]["name"]) for k in f["props"]), f'<span class=muted>{e(f["kind"])}</span>', f'<span class=muted>{e(f["false_when"])}</span>') for f in D.FLAGS]
        body = self.page_hero(X["kicker"], X["title"], X["lead"])
        body += self.section(X["how_title"], self.table(X["th"], rows), X["how_lead"])
        body += self.section(X["kinds_title"], self.cards(X["kinds"], "g3"))
        body += self.section(X["err_title"], self.cards([(None, a, b) for a, b in X["errs"]], "g2"))
        body += self.section(X["mine_title"], self.tool_shell("myflags"), X["mine_lead"])
        self.out(P["flags"], self.page(P["flags"], X["title"], X["desc"], body, "theory"))

    def build_types(self):
        D, P, X = self.D, self.P, self.D.PAGES["types"]
        by_key = {p["key"]: p for p in D.PROPS}
        cards = []
        for t in D.TYPES:
            prof = ", ".join(f"{e(by_key[k]['name'])} {v}" for k, v in t["profile"].items())
            cards.append(f'<div class="card"><p class="num">{e(t["origin"])}</p><h3>{e(t["name"])}</h3><p class="small">{e(t["text"])}</p><p class="small muted">{prof}</p></div>')
        body = self.page_hero(X["kicker"], X["title"], D.TYPES_INTRO)
        body += self.section(X["profiles_title"], f'<div class="grid g3">{"".join(cards)}</div>', X["profiles_lead"])
        body += self.section(X["by_relation"], self.cards([(None, a, b) for a, b in D.TYPES_BY_RELATION], "g3"))
        body += self.section(X["by_structure"], self.cards([(None, a, b) for a, b in D.TYPES_BY_STRUCTURE], "g3"))
        body += self.section(X["by_phase"], f'<div class="card big soft"><p class="lead" style="margin:0">{e(D.TYPES_BY_PHASE)}</p></div>')
        self.out(P["types"], self.page(P["types"], X["kicker"], X["desc"], body, "theory"))

    def build_sexuality(self):
        D, P, S, X = self.D, self.P, self.D.SEXUALITY_PAGE, self.D.PAGES["sex"]
        ap = [p for p in D.PROPS if p["key"] == "atracao"][0]
        body = self.page_hero(X["kicker"], S["title"], S["lead"]) + self.section(self.D.PAGES["sex_items_title"], self.cards([(None, a, b) for a, b in S["items"]], "g3"), sr=True)
        body += self.section(None, f'<div class="row"><a class="btn" href="{P["selfdiscover"]}">{e(X["btn1"])}</a><a class="btn ghost" href="{self.prop_path(ap)}">{e(X["btn2"])}</a></div>')
        self.out(P["sexuality"], self.page(P["sexuality"], S["title"], S["lead"], body, "theory"))

    def build_theories(self):
        D, P, X = self.D, self.P, self.D.PAGES["theories"]
        t = self.table(X["th"], [(f"<b>{e(a)}</b>", f"<span class=muted>{e(b)}</span>", e(c)) for a, b, c in D.THEORIES])
        body = self.page_hero(X["kicker"], X["title"], X["lead"]) + self.section(None, t) + self.section(X["differs_title"], self.cards(X["differs"], "g4"))
        self.out(P["theories"], self.page(P["theories"], X["kicker"], X["desc"], body, "theory"))

    def app_ld(self, key, name, desc):
        return [{"@type": "WebApplication", "@id": self.url(self.P[key]) + "#app", "name": name, "description": desc, "url": self.url(self.P[key]),
                 "applicationCategory": "LifestyleApplication", "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "inLanguage": self.D.LANG,
                 "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": ORG["@id"]}}]

    def build_tools(self):
        D, P, TL = self.D, self.P, self.D.PAGES["tools"]
        for key, tool, noindex in [("scale", "scale", False), ("portraits", "portraits", True), ("couple", "couple", False), ("selflove", "selflove", False), ("selfdiscover", "selfdiscover", False)]:
            name, desc, h1, lead = TL[key]
            self.out(P[key], self.page(P[key], name, desc, self.page_hero(name, h1, lead) + self.tool_shell(tool), key, noindex=noindex, ld_extra=None if noindex else self.app_ld(key, name, desc)))
        name, desc, _, _ = TL["stay"]
        self.out(P["stay"], self.page(P["stay"], name, desc, self.page_hero(D.STAY["kicker"], D.STAY["title"], D.STAY["lead"]) + self.tool_shell("stay"), "stay", ld_extra=self.app_ld("stay", name, desc)))
        name, desc, _, _ = TL["limits"]
        self.out(P["limits"], self.page(P["limits"], name, desc, self.page_hero(D.LIMITS["kicker"], D.LIMITS["title"], D.LIMITS["lead"]) + self.tool_shell("limits"), "limits", ld_extra=self.app_ld("limits", name, desc)))

    def build_glossary(self):
        D, P, X = self.D, self.P, self.D.PAGES["glossary"]
        by_key = {p["key"]: p for p in D.PROPS}
        def href(k):
            if not k: return None
            if k.startswith("prop:"): return self.prop_path(by_key[k[5:]])
            return P.get(k)
        groups = ""
        for gid, gname in D.GLOSSARY_GROUPS:
            terms = [g for g in D.GLOSSARY if g[0] == gid]
            dl = "".join(f'<div class="gl-term"><dt>{e(t)}</dt><dd>{e(d)}' + (f' <a href="{href(k)}">{e(X["see"])} →</a>' if href(k) else "") + '</dd></div>' for _, t, d, k in terms)
            groups += f'<section class="gl-group"><h2>{e(gname)}</h2><dl class="gl">{dl}</dl></section>'
        body = self.page_hero(X["kicker"], X["title"], X["lead"])
        body += f'<div class="wrap"><div id="app" data-tool="glossary"><input type="search" class="gl-search" placeholder="{e(X["search"])}" aria-label="{e(X["search"])}"></div>{groups}<p class="gl-none note hidden" role="status">{e(X["none"])}</p></div>'
        gurl = self.url(P["glossary"])
        term_set = {"@type": "DefinedTermSet", "@id": gurl + "#terms", "name": X["title"], "url": gurl, "inLanguage": self.D.LANG,
                    "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d, "inDefinedTermSet": {"@id": gurl + "#terms"}} for _, t, d, _ in D.GLOSSARY]}
        self.out(P["glossary"], self.page(P["glossary"], X["kicker"], X["desc"], body, "theory", ld_extra=[term_set]))

    def build_about(self):
        P, A, X = self.P, self.D.ABOUT, self.D.PAGES["about_page"]
        body = self.page_hero(X["kicker"], A["title"], A["text"][0]) + self.section(None, "".join(f"<p class=lead>{e(t)}</p>" for t in A["text"][1:]))
        body += self.section(A["privacy_title"], f'<p class="lead">{e(X["privacy_short"])}</p><p><a class="btn ghost" href="{P["privacy"]}">{e(X["privacy_more"])}</a></p>', sid="privacy")
        self.out(P["about"], self.page(P["about"], A["title"], X["desc"], body))

    def build_privacy(self):
        P, R = self.P, self.D.PRIVACY
        secs = ""
        for h, paras, links in R["sections"]:
            ps = "".join(f"<p>{e(R['analytics_on'] if CF_TOKEN else R['analytics_off']) if t == '@analytics' else e(t)}</p>" for t in paras)
            ls = "".join(f'<li><a href="{u}" rel="noopener">{e(n)}</a></li>' for n, u in links)
            secs += f'<section class="card big policy"><h2>{e(h)}</h2>{ps}{f"<ul>{ls}</ul>" if ls else ""}</section>'
        body = self.page_hero(R["kicker"], R["title"], R["lead"]) + f'<div class="wrap policy-wrap">{secs}<p class="muted">{e(R["updated"])}</p></div>'
        self.out(P["privacy"], self.page(P["privacy"], R["title"], R["desc"], body))

    def build_data(self):
        D = self.D
        props = [{k: p.get(k) for k in ("key", "slug", "name", "short", "group", "lead", "subs", "note", "roots", "expr", "selflove", "quick", "deep", "root_q", "quick_root", "reverse", "animal")} for p in D.PROPS]
        slider_keys = {s["key"]: s["slug"] for s in D.SLIDERS}
        data = dict(lang=D.LANG, host=HOST, paths=D.PATHS, ui=D.UI, props=props, thermo=D.THERMO, relations=D.RELATIONS, types=D.TYPES,
                    portraitFlags=D.PORTRAIT_FLAGS, rootNotes=D.ROOT_NOTES, flags=[{k: f[k] for k in ("sign", "text", "props", "kind")} for f in D.FLAGS],
                    sliders=D.SLIDERS, sliderGroups=D.SLIDER_GROUPS, sliderKeys=slider_keys, tastes=D.TASTES, expectQ=D.EXPECT_Q, expectOpts=D.EXPECT_OPTS,
                    weightQ=D.WEIGHT_Q, stay=D.STAY, loveLangs=D.LOVE_LANGS, limits=D.LIMITS)
        write(f"assets/data-{self.code}.js", "window.LT=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")

    def pages(self):
        return list(self.P.values()) + [self.prop_path(p) for p in self.D.PROPS]

    def build(self):
        self.build_data(); self.build_home(); self.build_theory(); self.build_props(); self.build_model(); self.build_mechanisms()
        self.build_modulators(); self.build_time(); self.build_flags(); self.build_types(); self.build_sexuality(); self.build_theories()
        self.build_tools(); self.build_about(); self.build_glossary(); self.build_privacy()
        write(self.prefix + "llms.txt", self.llms())
        write(self.prefix + "llms-full.txt", self.llms_full())

    # ------------------------------------------------------------ GEO: llms.txt
    def llms(self):
        D, P, PG = self.D, self.P, self.D.PAGES
        home = f"{SITE}/{self.prefix}"
        L = [f"# {D.SITE_NAME}", "", f"> {D.DESCRIPTION}", "", D.HOME["lead"], "", D.HOME["independence"], ""]
        L += [f"## {PG['tools_title']}", ""] + [f"- [{t['name']}]({self.url(P[t['key']])}): {t['text']}" for t in D.TOOLS] + [""]
        L += [f"## {PG['theory']['title']}", ""] + [f"- [{t}]({self.url(P[k])}): {d}" for k, t, d in PG["theory"]["pages"]] + [""]
        L += [f"## {PG['theory']['props_title']}", ""] + [f"- [{p['name']}]({self.url(self.prop_path(p))}): {p['lead']}" for p in D.PROPS] + [""]
        other = data_pt if self.code == "en" else data_en
        L += ["## " + ("Português" if self.code == "en" else "English"), "", f"- [{other.SITE_NAME} ({'pt-BR' if self.code == 'en' else 'en'})]({SITE}/{self.other_prefix}llms.txt): {other.DESCRIPTION}", ""]
        L += ["## Optional", "", f"- [Full text]({home}llms-full.txt): {'every page of the theory and the glossary as plain text' if self.code == 'en' else 'todas as páginas da teoria e o glossário em texto corrido'}",
              f"- [{PG['privacy_link']}]({self.url(P['privacy'])}): {D.PRIVACY['desc']}", ""]
        return "\n".join(L)

    def llms_full(self):
        D, PG = self.D, self.D.PAGES
        M, T, S = D.MODEL_PAGE, D.TIME_PAGE, D.SEXUALITY_PAGE
        L = [f"# {D.SITE_NAME}", "", f"> {D.DESCRIPTION}", "", f"Source: {SITE}/{self.prefix}", "", D.HOME["lead"], "", D.HOME["independence"], ""]
        L += [f"## {PG['theory']['intro_title']}", ""] + sum(([t, ""] for t in PG["theory"]["intro"]), [])
        L += [f"## {M['title']}", "", M["lead"], ""] + [f"- {a}: {b} ({c})" for a, b, c in M["terms"]] + [""] + [f"- {a} {b}" for a, b in M["rules"]] + [""]
        L += [f"### {M['sources_title']}", "", M["sources_lead"], ""] + [f"- {a}: {b}" for a, b in M["sources"]] + ["", M["sources_end"], ""]
        L += [f"## {PG['theory']['props_title']}", "", PG["theory"]["props_lead"], ""]
        for i, p in enumerate(D.PROPS):
            L += [f"### {i+1}. {p['name']}", "", p["lead"], "", "; ".join(p["subs"]) + ".", "", p["note"], "",
                  f"{PG['prop']['from_title']}: " + "; ".join(p["roots"]) + ".", f"{PG['prop']['aggr']}: {p['expr'][0]}. {PG['prop']['peaceful']}: {p['expr'][1]}.", ""]
        X = PG["mech"]
        L += [f"## {X['title']}", "", X["lead"], "", X["chain"], "", X["chain_text"], ""] + [f"- {a}: {b}. {c}" for a, b, c in X["rules"]] + [""]
        L += [f"### {X['case_title']}", "", X["case_lead"], ""] + [f"- {r[0]}: {r[2]}; {r[3]}; {r[4]}; {r[5]} / {r[6]}" for r in D.JEALOUSY] + ["", X["case_note"], ""]
        L += [f"## {PG['modul']['title']}", "", PG["modul"]["lead"], ""] + [f"- {a}: {b}" for a, b, _ in D.MODULATORS] + [""]
        L += [f"## {T['title']}", "", T["lead"], ""] + [f"- {a} {b}" for a, b in T["does"]] + [""] + [f"- {a} {b}" for a, b in T["keeps"]] + [""]
        F = PG["flags"]
        L += [f"## {F['title']}", "", F["lead"], ""] + [f"- [{f['sign']}] {f['text']}: {f['kind']}; {f['false_when']}" for f in D.FLAGS] + [""]
        L += [f"## {PG['types']['kicker']}", "", D.TYPES_INTRO, ""] + [f"- {t['name']} ({t['origin']}): {t['text']}" for t in D.TYPES] + [""]
        L += [f"## {S['title']}", "", S["lead"], ""] + [f"- {a}: {b}" for a, b in S["items"]] + [""]
        L += [f"## {PG['theories']['title']}", ""] + [f"- {a}, {b}: {c}" for a, b, c in D.THEORIES] + [""]
        L += [f"## {PG['tools_title']}", ""] + [f"- {t['name']}: {t['text']}" for t in D.TOOLS] + ["", D.STAY["lead"], "", D.LIMITS["lead"], ""]
        L += [f"## {PG['glossary']['title']}", ""] + [f"- {t}: {d}" for _, t, d, _ in D.GLOSSARY] + [""]
        return "\n".join(L)


def build_assets():
    css = open(os.path.join(ROOT, "assets", "style.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "assets", "app.js"), encoding="utf-8").read()
    write("assets/style.min.css", rcssmin.cssmin(css) if rcssmin else css)
    write("assets/app.min.js", rjsmin.jsmin(js) if rjsmin else js)
    old = os.path.join(ROOT, "assets", "data.js")
    if os.path.exists(old):
        os.remove(old)


def build_root():
    nf_en, nf_pt = data_en.PAGES["nf"], data_pt.PAGES["nf"]
    write("404.html", f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>404 · The Love Theory</title>
<meta name="description" content="{e(data_en.PAGES['nf_desc'])}"><meta name="robots" content="noindex"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link href="{FONTS}" rel="stylesheet"><link rel="stylesheet" href="/assets/style.min.css?v={BUILT}"></head>
<body><main id="main" class="wrap" style="padding:80px 20px"><p class="eyebrow">404</p><h1>{e(nf_en["title"])}</h1><p class="lead">{e(nf_en["lead"])} <span lang="pt-BR">{e(nf_pt["title"])} {e(nf_pt["lead"])}</span></p>
<p class="row"><a class="btn" href="/">{e(nf_en["cta"])}</a> <a class="btn ghost" href="/pt/" lang="pt-BR">{e(nf_pt["cta"])}</a> <a class="btn ghost" href="/glossary.html">{e(data_en.PAGES["glossary_link"])}</a> <a class="btn ghost" href="/pt/glossario.html" lang="pt-BR">{e(data_pt.PAGES["glossary_link"])}</a></p></main>{CF_SNIPPET}</body></html>
""")
    write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#d8408f"/><path fill="#fff" d="M32 50.8l-3.5-3.2C19.4 39.4 13.3 33.9 13.3 27.2c0-5.5 4.3-9.8 9.8-9.8 3.1 0 6.1 1.4 8.9 4.3 2.8-2.9 5.8-4.3 8.9-4.3 5.5 0 9.8 4.3 9.8 9.8 0 6.7-6.1 12.2-15.2 20.4L32 50.8z"/></svg>')
    write("CNAME", HOST + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\n# Conteúdo em texto para modelos de linguagem / plain-text content for language models\n# {SITE}/llms.txt\n# {SITE}/pt/llms.txt\n\nSitemap: {SITE}/sitemap.xml\n")
    try:
        import images
        images.make_all(ROOT, [(s, d.PAGES, d.HOME) for s, d in (("en", data_en), ("pt", data_pt))])
    except ImportError:
        print("aviso: Pillow ausente; ícones e imagem OG não regenerados")
    json.dump({"name": "The Love Theory", "short_name": "Love Theory", "description": data_en.DESCRIPTION, "start_url": "/", "scope": "/", "display": "standalone",
               "background_color": "#f7efe7", "theme_color": "#f3b4cc", "lang": "en",
               "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
                         {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                         {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                         {"src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
              open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8", newline=chr(10)), indent=1, ensure_ascii=False)


def build_sitemap(sites):
    en, pt = sites
    rows = []
    for s, o in ((en, pt), (pt, en)):
        for p in s.pages():
            if p == s.P["portraits"]:
                continue
            op = s.other_path(p)
            alt_en, alt_pt = (s.url(p), o.url(op)) if s.code == "en" else (o.url(op), s.url(p))
            rows.append(f'<url><loc>{s.url(p)}</loc><lastmod>{BUILT}</lastmod>'
                        f'<xhtml:link rel="alternate" hreflang="en" href="{alt_en}"/><xhtml:link rel="alternate" hreflang="pt-BR" href="{alt_pt}"/>'
                        f'<xhtml:link rel="alternate" hreflang="x-default" href="{alt_en}"/></url>')
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'] + rows + ["</urlset>"]
    write("sitemap.xml", "\n".join(sm) + "\n")


def main():
    build_assets()
    sites = [Site(code, D, prefix) for code, D, prefix in LANGS]
    for s in sites:
        s.build()
    build_root()
    build_sitemap(sites)
    print("ok: " + " + ".join(f"{s.code} {len(s.pages())}" for s in sites) + f" páginas, built {BUILT}")


if __name__ == "__main__":
    main()
