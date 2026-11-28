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
# fecha o grupo aberto do menu ao clicar fora ou apertar Esc (o menu existe em todas as páginas, com ou sem app.js)
NAV_JS = ('<script>(function(){function c(t){document.querySelectorAll(".menu details[open]").forEach(function(d){if(!t||!d.contains(t))d.open=false})}'
          'document.addEventListener("click",function(e){c(e.target)});document.addEventListener("keydown",function(e){if(e.key==="Escape")c()})})();</script>\n')
# Versão curta da Mitologia Sexual: (número de afirmações do tema quando a escolha foi feita, índices das essenciais).
# Se o tema ganhar ou perder afirmações, o build para: os índices precisam ser revistos.
MYTHS_SHORT = {
    "consentimento": (16, [0, 1, 5, 6, 12]), "importunacao": (12, [0, 2, 9]), "pressao": (12, [0, 1, 4, 7]), "prazer": (18, [0, 3, 11, 16]),
    "corpo": (12, [1, 3, 6]), "corpos": (13, [0, 4, 10]), "prevencao": (16, [0, 3, 4, 13]), "julgamento": (17, [0, 3, 13, 15]),
    "acordos": (13, [0, 2, 9]), "conversa": (14, [0, 4, 12]), "digital": (9, [0, 1, 5]), "outros": (13, [0, 4, 7]),
}
ANSWER_SECS = 10   # tempo por resposta em todos os testes (definido pelo Julio em 2026-11-27)
MYTH_SECS = ANSWER_SECS
# Versão curta dos testes grandes: por grupo, (número de itens quando a escolha foi feita, índices dos essenciais).
LIMITS_SHORT = {
    "pensamentos": (10, [0, 6, 7]), "naomono": (10, [3, 5, 9]), "porno": (5, [0, 3, 4]), "redes": (6, [0, 2, 5]), "sinais": (3, [0, 2]),
    "emocional": (8, [1, 5, 7]), "flerte": (7, [1, 4, 6]), "contato": (6, [1, 3, 5]), "encontros": (6, [0, 3, 5]), "sigilo": (9, [0, 3, 7]),
    "ex": (8, [0, 2, 7]), "sexual": (12, [3, 5, 8, 11]), "paralelo": (10, [0, 3, 7]),
}
LISTS_SHORT = {
    "spark": {
        "corpo": (10, [0, 2, 5]), "viagem": (12, [0, 5, 8]), "comida": (10, [0, 1, 6]), "jogos": (10, [0, 2, 3]), "cultura": (10, [0, 3, 5]),
        "social": (8, [1, 4, 7]), "casa": (10, [0, 4, 6]), "romance": (14, [0, 2, 8]), "conversa": (8, [0, 5, 7]),
        "clima": (11, [0, 2, 7]), "provocacao": (10, [0, 3, 4]), "sentidos": (10, [0, 1, 4]), "jeitos": (13, [0, 2, 4]), "papeis": (11, [2, 4, 10]), "registro": (8, [0, 1, 4]),
        "olhar": (9, [0, 3, 6]), "flerte": (7, [0, 1, 4]), "gente": (8, [0, 1, 4]), "acordos": (9, [0, 2, 8]),
    },
    "lovelist": {
        "amizade": (7, [0, 1, 4]), "admiracao": (8, [0, 3, 5]), "presenca": (8, [0, 2, 4]), "confianca": (6, [0, 1, 2]), "igualdade": (6, [0, 1, 4]), "mundo": (4, [0, 1]),
        "gestos": (10, [0, 3, 9]), "memorias": (10, [0, 3, 6]), "aventuras": (12, [0, 1, 6]), "marcos": (12, [1, 4, 6, 11]), "dia": (10, [0, 2, 3]),
    },
    "sexlist": {
        "comecos": (12, [0, 4, 8]), "dar": (15, [0, 1, 2, 3]), "posicoes": (14, [0, 2, 4]), "ritmo": (18, [0, 2, 8]), "sentidos": (13, [0, 3, 5]), "papeis": (15, [2, 3, 5]),
        "ver": (10, [0, 2, 4]), "gente": (7, [2, 3, 5]), "ocasioes": (8, [0, 3, 5]),
        "casa": (12, [2, 5, 7]), "fora": (8, [0, 1, 6]), "transporte": (5, [0, 2]), "arlivre": (7, [0, 3, 6]), "semplateia": (4, [1, 2]), "publico": (17, [5, 6, 15]),
    },
}


def prepare_myths(D):
    """Marca as afirmações da versão curta e calcula o tempo aproximado das duas versões."""
    M = D.MYTHS
    if "ns" in M:
        return
    assert set(MYTHS_SHORT) == {t["id"] for t in M["themes"]}, "MYTHS_SHORT precisa cobrir todos os temas"
    for t in M["themes"]:
        n, idx = MYTHS_SHORT[t["id"]]
        assert len(t["items"]) == n, f'tema {t["id"]}: {len(t["items"])} afirmações, a versão curta foi escolhida com {n}; revise MYTHS_SHORT'
        t["short"] = idx
    M["secs"] = MYTH_SECS
    M["ns"] = sum(len(v[1]) for v in MYTHS_SHORT.values())
    mins = lambda n: max(1, int(n * MYTH_SECS / 60 + 0.5))
    M["versions"] = (M["t"]["versions"].replace("{s}", str(M["ns"])).replace("{sm}", str(mins(M["ns"])))
                     .replace("{n}", str(M["n"])).replace("{fm}", str(mins(M["n"]))))
    versions = lambda s, n: (D.PAGES["versions_items"].replace("{s}", str(s)).replace("{sm}", str(mins(s))).replace("{n}", str(n)).replace("{fm}", str(mins(n))))
    # Limites: índices das situações essenciais, na ordem da lista inteira
    LM = D.LIMITS
    assert set(LIMITS_SHORT) == {g for g, _ in LM["groups"]}, "LIMITS_SHORT precisa cobrir todos os grupos"
    LM["short"] = []
    for gid, _ in LM["groups"]:
        pos = [i for i, it in enumerate(LM["items"]) if it[0] == gid]
        n, idx = LIMITS_SHORT[gid]
        assert len(pos) == n, f"Limites, grupo {gid}: {len(pos)} itens, a versão curta foi escolhida com {n}; revise LIMITS_SHORT"
        LM["short"] += [pos[k] for k in idx]
    LM["versions"] = versions(len(LM["short"]), len(LM["items"]))
    # listas: índices dos itens essenciais dentro de cada grupo
    for key, table in LISTS_SHORT.items():
        L = D.LISTS[key]
        gids = [g["id"] for s in L["sections"] for g in s["groups"]]
        assert set(table) == set(gids), f"LISTS_SHORT[{key}] precisa cobrir todos os grupos"
        for s in L["sections"]:
            for g in s["groups"]:
                n, idx = table[g["id"]]
                assert len(g["items"]) == n, f'{key}, grupo {g["id"]}: {len(g["items"])} itens, a versão curta foi escolhida com {n}; revise LISTS_SHORT'
                g["short"] = idx
        L["ns"] = sum(len(v[1]) for v in table.values())
        L["versions"] = versions(L["ns"], L["n"])


# Endereços antigos que continuam funcionando: (caminho antigo, caminho novo). Página mínima com redirecionamento.
REDIRECTS = [("pt/bucket-list-do-amor.html", "pt/antes-de-partir-amor.html"), ("pt/bucket-list-sexual.html", "pt/antes-de-partir-sexo.html")]
LIST_KEYS = ("spark", "lovelist", "sexlist")   # as três ferramentas de lista (app.js: lists)

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

    def page(self, path, title, desc, body, active=None, noindex=False, ld_extra=None, adult=False):
        D, P, PG = self.D, self.P, self.D.PAGES
        url = self.url(path)
        op = self.other_path(path)
        other_url = f"{SITE}/{self.other_prefix}" + ("" if op == "index.html" else op)
        en_url, pt_url = (url, other_url) if self.code == "en" else (other_url, url)
        other_hl = "pt-BR" if self.code == "en" else "en"
        grouped = [k for _, ks in D.NAV_GROUPS for k in ks]
        assert sorted(grouped + ["home", "theory"]) == sorted(k for k, _ in D.NAV), "NAV e NAV_GROUPS precisam cobrir as mesmas chaves"
        full = {k: v[0] for k, v in PG["tools"].items()}
        link = lambda k, t: f'<a href="{self.href(k)}"{" class=on aria-current=page" if k == active else ""}>{e(t)}</a>'
        nav = "".join(link(k, t) for k, t in D.NAV if k not in grouped and k != "home")   # o início é o logo
        # um botão só; dentro do painel, cada grupo é uma coluna com título (texto, não link)
        cols = "".join(f'<div class="sub-g" role="group" aria-labelledby="mg{i}"><p class="sub-h" id="mg{i}">{e(label)}</p>{"".join(link(k, full[k]) for k in ks)}</div>'
                       for i, (label, ks) in enumerate(D.NAV_GROUPS))
        nav += f'<details name="nav"{" class=on" if active in grouped else ""}><summary>{e(PG["tools_menu"])}</summary><div class="sub">{cols}</div></details>'
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
             "description": D.DESCRIPTION, "publisher": {"@id": ORG["@id"]},
             "audience": {"@type": "PeopleAudience", "suggestedMinAge": 18}}, ORG]
        if len(crumbs) > 1:
            graph.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
        graph += ld_extra or []
        ld = {"@context": "https://schema.org", "@graph": graph}
        uses_tool = 'data-tool="' in body
        scripts = (f'<script src="/assets/data-{self.code}.js?v={BUILT}" defer></script>\n<script src="/assets/app.min.js?v={BUILT}" defer></script>\n') if uses_tool else ""
        og_img = f"{SITE}/{self.og_file()}"
        rating = '<meta name="rating" content="adult">' + chr(10) if adult else ""
        full_title = title if D.SITE_NAME in title else f"{title} · {D.SITE_NAME}"
        return f"""<!doctype html>
<html lang="{D.LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{'noindex' if noindex else 'index, follow, max-image-preview:large'}">
{rating}<link rel="canonical" href="{url}">
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
<header class="nav"><div class="wrap"><a class="logo" href="./" aria-label="{e(PG['home_aria'])}"{" aria-current=page" if active == "home" else ""}><span class="mark">{LOGO}</span><span class="t">{D.SITE_NAME}</span></a><nav class="menu" aria-label="{e(PG['nav_aria'])}">{nav}<a class="lang" href="/{self.other_prefix}{'' if op == 'index.html' else op}" hreflang="{other_hl}" lang="{other_hl}" aria-label="{e(PG['lang_aria'])}">{e(D.SWITCH_LABEL)}</a></nav></div></header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="foot"><div class="wrap"><p class="script">{e(PG['footer'])}</p><p><a href="{P['glossary']}">{e(PG['glossary_link'])}</a> · <a href="{P['about']}">{e(PG['about'])}</a> · <a href="{P['privacy']}">{e(PG['privacy_link'])}</a> · <a href="https://biblioverse.org">BiblioVerse</a> · <small>{e(PG['copyright'])}</small></p></div></footer>
{NAV_JS}{CF_SNIPPET}
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
        byk = {t["key"]: t for t in D.TOOLS}
        petal = lambda t: f'<a class="petal" href="{P[t["key"]]}"><span class="k">{e(t["kicker"])}</span><h3>{e(t["name"])}</h3><p>{e(t["text"])}</p><span class="go">{e(PG["open"])}</span></a>'
        tgroups = [(PG["theory_group"], ["theory"])] + [(label, [k for k in ks if k in byk]) for label, ks in D.NAV_GROUPS]
        gids = ["tools-theory", "tools-me", "tools-someone", "tools-two"]   # âncoras iguais nas duas línguas
        assert len(gids) == len(tgroups)
        toc = "".join(f'<a href="#{g}">{e(label)}</a>' for g, (label, _) in zip(gids, tgroups))
        assert sorted(k for _, ks in tgroups for k in ks) == sorted(byk), "toda ferramenta da home precisa estar num grupo"
        tools = "".join(f'<h3 class="petal-group" id="{g}">{e(label)}</h3><div class="petals">{"".join(petal(byk[k]) for k in ks)}</div>' for g, (label, ks) in zip(gids, tgroups))
        body = f'''<section class="collage">
<div class="win hero-win tilt-l"><div class="win-bar"><i></i><i></i><i></i><span>{e(PG["studio"])}</span></div><div class="win-body">
<p class="kicker">{e(H["kicker"])}</p><h1>{e(H["title"])}</h1><p class="sub">{e(H["title2"])}</p><p class="lead">{e(H["lead"])}</p>
<div class="row" style="margin-top:22px"><a class="btn" href="{P['scale']}">{e(PG["do_scale"])}</a><a class="btn ghost" href="{P['theory']}">{e(PG["read_theory"])}</a></div></div></div>
<div class="frame-card tx-stitch tilt-r"><span class="tape r"></span><nav class="oval toc" aria-label="{e(PG["toc_aria"])}">{toc}</nav><p class="cap">{e(PG["oval_caption"])}</p></div>
<div class="lace-card tx-lace tilt-l"><span class="tape"></span><div class="in"><h2>{e(H["privacy"].split(".")[0])}</h2><p>{e(H["privacy"])} <a href="{P['privacy']}">{e(PG['privacy_link'])} →</a></p><p class="adult-note"><span class="tag adult">{e(PG['adult_tag'])}</span> {e(H['adult'])}</p></div></div>
</section>'''
        body += self.section(PG["tools_title"], tools)
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

    def app_ld(self, key, name, desc, adult=False, features=None):
        extra = {"isFamilyFriendly": False, "contentRating": "18+", "audience": {"@type": "PeopleAudience", "suggestedMinAge": 18}} if adult else {}
        if features:
            extra["featureList"] = features
        return [{**extra, "@type": "WebApplication", "@id": self.url(self.P[key]) + "#app", "name": name, "description": desc, "url": self.url(self.P[key]),
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
        self.out(P["limits"], self.page(P["limits"], name, desc, self.page_hero(D.LIMITS["kicker"], D.LIMITS["title"], D.LIMITS["lead"] + " " + D.LIMITS["versions"]) + self.tool_shell("limits"), "limits", ld_extra=self.app_ld("limits", name, desc)))
        PG = D.PAGES
        M = D.MYTHS
        name, desc, seo, _ = TL["myths"]
        how = self.section(PG["lists_how"], self.cards([(f"{i+1}.", a, t) for i, (a, t) in enumerate(M["how"])], "g3"))
        cards = "".join(f'<div class="card"><p class="num">{e(M["t"]["count"].replace("{n}", str(len(t["items"]))))}</p><h3>{e(t["title"])}</h3><p class="small">{e(t["lead"])}</p></div>' for t in M["themes"])
        notes = '<div class="card big soft" style="margin-top:18px"><ul style="margin:0">' + "".join(f"<li>{e(t)}</li>" for t in M["notes"]) + "</ul></div>"
        body = self.page_hero(M["kicker"], M["title"], M["lead"] + " " + M["versions"]) + self.tool_shell("myths") + how + self.section(PG["lists_inside"], f'<div class="grid g3">{cards}</div>' + notes)
        self.out(P["myths"], self.page(P["myths"], seo, desc, body, "myths", ld_extra=self.app_ld("myths", name, desc, features=[t["title"] for t in M["themes"]])))
        for key in LIST_KEYS:
            name, desc, seo, _ = TL[key]
            L = D.LISTS[key]
            assert key == "spark" or str(L["n"]) in seo, (key, L["n"], seo)   # o título de busca cita o número de itens
            how = self.section(PG["lists_how"], self.cards([(f"{i+1}.", a, t) for i, (a, t) in enumerate(L["how"])], "g3"))
            cards = ""
            for s in L["sections"]:
                n = sum(len(g["items"]) for g in s["groups"])
                tag = f' <span class="tag adult">{e(PG["adult_tag"])}</span>' if s["adult"] else ""
                cards += (f'<div class="card"><p class="num">{e(PG["lists_items"].replace("{n}", str(n)))}{tag}</p><h3>{e(s["title"])}</h3><p class="small">{e(s["lead"])}</p>'
                          f'<p class="small muted">{e(" · ".join(g["title"] for g in s["groups"]))}</p></div>')
            notes = '<div class="card big soft" style="margin-top:18px"><ul style="margin:0">' + "".join(f"<li>{e(t)}</li>" for t in L["notes"]) + "</ul></div>"
            body = self.page_hero(L["kicker"], L["title"], L["lead"] + " " + L["versions"]) + self.tool_shell(key) + how + self.section(PG["lists_inside"], f'<div class="grid g3">{cards}</div>' + notes)
            self.out(P[key], self.page(P[key], seo, desc, body, key, ld_extra=self.app_ld(key, name, desc, adult=L["adult"], features=[s["title"] for s in L["sections"]]), adult=(key == "sexlist")))

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
                    weightQ=D.WEIGHT_Q, stay=D.STAY, loveLangs=D.LOVE_LANGS, limits=D.LIMITS, lists=D.LISTS, myths=D.MYTHS, secs=ANSWER_SECS)
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
        L = [f"# {D.SITE_NAME}", "", f"> {D.DESCRIPTION}", "", D.HOME["lead"], "", D.HOME["independence"], "", D.HOME["adult"], ""]
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
        L = [f"# {D.SITE_NAME}", "", f"> {D.DESCRIPTION}", "", f"Source: {SITE}/{self.prefix}", "", D.HOME["lead"], "", D.HOME["independence"], "", D.HOME["adult"], ""]
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
        for key in LIST_KEYS:
            Ls = D.LISTS[key]
            L += [f"### {Ls['kicker']}", "", Ls["lead"] + " " + Ls["versions"], ""] + [f"- {a}: {t}" for a, t in Ls["how"]] + [""] + [f"- {t}" for t in Ls["notes"]] + [""]
            for s in Ls["sections"]:
                L += [f"#### {s['title']}", "", s["lead"], ""]
                L += [f"- {g['title']} ({len(g['items'])})" + ("" if s["adult"] else ": " + " ".join(g["items"])) for g in s["groups"]] + [""]
        M = D.MYTHS
        L += [f"## {M['kicker']}", "", M["lead"] + " " + M["versions"], ""] + [f"- {t}" for t in M["notes"]] + [""]
        for th in M["themes"]:
            L += [f"### {th['title']}", "", th["lead"], ""] + [f"- {it[0]} {M['t']['is_true'] if it[1] else M['t']['is_myth']} {it[2]}" + "".join(f" [{l}]({u})" for l, u in (it[3] if len(it) > 3 else [])) for it in th["items"]] + [""]
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
    for old, new in REDIRECTS:
        write(old, f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>The Love Theory</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{SITE}/{new}"><meta http-equiv="refresh" content="0; url=/{new}">
<script>location.replace("/{new}" + location.hash);</script></head>
<body><p><a href="/{new}">The Love Theory</a></p></body></html>
''')
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
    for _, D, _ in LANGS:
        prepare_myths(D)
    sites = [Site(code, D, prefix) for code, D, prefix in LANGS]
    for s in sites:
        s.build()
    build_root()
    build_sitemap(sites)
    print("ok: " + " + ".join(f"{s.code} {len(s.pages())}" for s in sites) + f" páginas, built {BUILT}")


if __name__ == "__main__":
    main()
