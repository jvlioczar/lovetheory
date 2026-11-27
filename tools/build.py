# -*- coding: utf-8 -*-
"""Gera o site The Love Theory nas duas línguas: EN na raiz, PT em /pt/. Rode: python tools/build.py"""
import os, sys, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data_en, data_pt

SITE = "https://lovetheory.biblioverse.org"
HOST = "lovetheory.biblioverse.org"
CF_TOKEN = ""  # token do Cloudflare Web Analytics; vazio = sem beacon
CF_SNIPPET = ("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
              "data-cf-beacon='{\"token\": \"%s\"}'></script><!-- End Cloudflare Web Analytics -->" % CF_TOKEN) if CF_TOKEN else ""
BUILT = datetime.date.today().isoformat()
FONTS = "https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=DynaPuff:wght@400;700&family=DM+Sans:wght@400;600;700&display=swap"
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
FLOWER = ('<svg viewBox="0 0 120 120" fill="none" stroke="#2a1d2c" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
          '<path d="M60 112V62"/><path d="M60 80c-10-2-22-12-26-26 14 2 24 12 26 26z" fill="#8a9a69"/><path d="M60 92c10-4 22-14 24-30-14 4-22 16-24 30z" fill="#8a9a69"/>'
          '<ellipse cx="60" cy="42" rx="34" ry="24" fill="#cdb9e6"/><ellipse cx="60" cy="40" rx="18" ry="12" fill="#f8d2e0"/><path d="M60 20v22M38 30l22 12M82 30L60 42M30 48l30-6M90 48l-30-6"/><circle cx="60" cy="42" r="4" fill="#f7efe7"/></svg>')


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

    def page(self, path, title, desc, body, active=None, noindex=False):
        D, P, PG = self.D, self.P, self.D.PAGES
        url = self.url(path)
        op = self.other_path(path)
        other_url = f"{SITE}/{self.other_prefix}" + ("" if op == "index.html" else op)
        en_url, pt_url = (url, other_url) if self.code == "en" else (other_url, url)
        other_hl = "pt-BR" if self.code == "en" else "en"
        nav = "".join(f'<a href="{P[k]}"{" class=on" if k == active else ""}>{e(t)}</a>' for k, t in D.NAV)
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebPage", "@id": url + "#page", "name": title, "description": desc, "url": url, "inLanguage": D.LANG,
             "dateModified": BUILT, "isPartOf": {"@id": f"{SITE}/{self.prefix}#website"}, "publisher": {"@id": ORG["@id"]}},
            {"@type": "WebSite", "@id": f"{SITE}/{self.prefix}#website", "name": D.SITE_NAME, "url": f"{SITE}/{self.prefix}", "inLanguage": D.LANG,
             "description": D.DESCRIPTION, "publisher": {"@id": ORG["@id"]}}, ORG]}
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
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:locale" content="{'en_US' if self.code == 'en' else 'pt_BR'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f3b4cc">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.min.css?v={BUILT}">
<script src="/assets/data-{self.code}.js?v={BUILT}" defer></script>
<script src="/assets/app.min.js?v={BUILT}" defer></script>
<script src="https://biblioverse.org/superbar.js" defer></script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<nav id="bvbar" class="bvbar" data-current="lovetheory" data-bg="#2a1d2c" data-fg="#ffffff" data-accent="#f3b4cc" aria-label="BiblioVerse" style="position:fixed;top:0;left:0;right:0;height:36px;z-index:9000;background:#2a1d2c"><a href="https://biblioverse.org" style="color:#fff;line-height:36px;padding:0 14px;font-weight:700;text-decoration:none">BiblioVerse</a></nav>
<header class="nav"><div class="wrap"><a class="logo" href="{P['home']}"><span class="mark">{LOGO}</span><span class="t">{D.SITE_NAME}</span></a><nav class="menu" aria-label="{e(PG['nav_aria'])}">{nav}<a class="lang" href="/{self.other_prefix}{'' if op == 'index.html' else op}" hreflang="{other_hl}" lang="{other_hl}">{e(D.SWITCH_LABEL)}</a></nav></div></header>
<main>
{body}
</main>
<footer class="foot"><div class="wrap"><p class="script">{e(PG['footer'])}</p><p><a href="{P['glossary']}">{e(PG['glossary_link'])}</a> · <a href="{P['about']}">{e(PG['about'])}</a> · <a href="{P['about']}#privacy">{e(PG['privacy'])}</a> · <a href="https://biblioverse.org">BiblioVerse</a></p></div></footer>
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

    def section(self, title, inner, lead=None, cls="", sid=None):
        return f'<section class="section {cls}"{f" id={sid}" if sid else ""}><div class="wrap">{f"<h2>{e(title)}</h2>" if title else ""}{f"<p class=lead>{e(lead)}</p>" if lead else ""}{inner}</div></section>'

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
<div class="lace-card tx-lace tilt-l"><span class="tape"></span><div class="in"><h3>{e(H["privacy"].split(".")[0])}</h3><p>{e(H["privacy"])}</p></div></div>
</section>'''
        body += self.section(PG["thesis_title"], self.cards([(f"{i+1}.", t, p) for i, (t, p) in enumerate(H["thesis"])], "g4"))
        body += self.section(H["independence_title"], f'<div class="card big pink"><p class="lead" style="margin:0;max-width:none">{e(H["independence"])}</p></div>')
        body += self.section(PG["tools_title"], f'<div class="petals">{tools}</div>')
        self.out("index.html", self.page("index.html", PG["home_title"], D.DESCRIPTION, body, "home"))

    def build_theory(self):
        D, P, T = self.D, self.P, self.D.PAGES["theory"]
        props = ""
        for gid, gname in D.GROUPS:
            ps = [p for p in D.PROPS if p["group"] == gid]
            props += f'<h3 style="margin-top:28px">{e(gname)}</h3><div class="grid g3">' + "".join(
                f'<a class="card" href="{self.prop_path(p)}"><p class="num">{D.PROPS.index(p)+1:02d}</p><h3>{e(p["name"])}</h3><p class="small">{e(p["lead"])}</p></a>' for p in ps) + "</div>"
        idx = '<div class="grid g4">' + "".join(f'<a class="card" href="{P[k]}"><h3>{e(t)}</h3><p class="small">{e(d)}</p></a>' for k, t, d in T["pages"]) + "</div>"
        body = self.page_hero(T["kicker"], T["title"], T["lead"]) + self.section(None, idx) + self.section(T["props_title"], props, T["props_lead"])
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
            self.out(self.prop_path(p), self.page(self.prop_path(p), p["name"], X["desc"].format(name=p["name"], lead=p["lead"]), body, "theory"))

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
        roots = '<div class="grid g3">' + "".join(f'<div class="card"><h4>{e(p["name"])}</h4><ul class="small">{"".join(f"<li>{e(r)}</li>" for r in p["roots"])}</ul></div>' for p in D.PROPS) + "</div>"
        body = self.page_hero(X["kicker"], X["title"], X["lead"])
        body += self.section(None, f'<div class="card big pink"><h3>{e(X["chain"])}</h3><p>{e(X["chain_text"])}</p></div>' + self.cards(X["rules"], "g3"))
        body += self.section(X["sig_title"], self.cards(X["sig"], "g3"), X["sig_lead"])
        body += self.section(X["case_title"], j + f'<div class="note">{e(X["case_note"])}</div>' + self.cards([(None, a, b) for a, b in X["case_cards"]], "g3"), X["case_lead"])
        body += self.section(X["expr_title"], ex + '<div class="grid g2">' + "".join(f'<div class="card"><h4>{e(a)}</h4><p>{e(b)}</p></div>' for a, b in X["expr_cards"]) + "</div>", X["expr_lead"])
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
        self.out(P["time"], self.page(P["time"], T["title"], T["lead"], body, "theory"))

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
        body = self.page_hero(X["kicker"], S["title"], S["lead"]) + self.section(None, self.cards([(None, a, b) for a, b in S["items"]], "g3"))
        body += self.section(None, f'<div class="row"><a class="btn" href="{P["selfdiscover"]}">{e(X["btn1"])}</a><a class="btn ghost" href="{self.prop_path(ap)}">{e(X["btn2"])}</a></div>')
        self.out(P["sexuality"], self.page(P["sexuality"], S["title"], S["lead"], body, "theory"))

    def build_theories(self):
        D, P, X = self.D, self.P, self.D.PAGES["theories"]
        t = self.table(X["th"], [(f"<b>{e(a)}</b>", f"<span class=muted>{e(b)}</span>", e(c)) for a, b, c in D.THEORIES])
        body = self.page_hero(X["kicker"], X["title"], X["lead"]) + self.section(None, t) + self.section(X["differs_title"], self.cards(X["differs"], "g4"))
        self.out(P["theories"], self.page(P["theories"], X["kicker"], X["desc"], body, "theory"))

    def build_tools(self):
        D, P, TL = self.D, self.P, self.D.PAGES["tools"]
        for key, tool, noindex in [("scale", "scale", False), ("portraits", "portraits", True), ("couple", "couple", False), ("selflove", "selflove", False), ("selfdiscover", "selfdiscover", False)]:
            name, desc, h1, lead = TL[key]
            self.out(P[key], self.page(P[key], name, desc, self.page_hero(name, h1, lead) + self.tool_shell(tool), key, noindex=noindex))
        name, desc, _, _ = TL["stay"]
        self.out(P["stay"], self.page(P["stay"], name, desc, self.page_hero(D.STAY["kicker"], D.STAY["title"], D.STAY["lead"]) + self.tool_shell("stay"), "stay"))
        name, desc, _, _ = TL["limits"]
        self.out(P["limits"], self.page(P["limits"], name, desc, self.page_hero(D.LIMITS["kicker"], D.LIMITS["title"], D.LIMITS["lead"]) + self.tool_shell("limits"), "limits"))

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
        body += f'<div class="wrap"><div id="app" data-tool="glossary"><input type="search" class="gl-search" placeholder="{e(X["search"])}" aria-label="{e(X["search"])}"></div>{groups}<p class="gl-none note hidden">{e(X["none"])}</p></div>'
        self.out(P["glossary"], self.page(P["glossary"], X["kicker"], X["desc"], body, "theory"))

    def build_about(self):
        P, A, X = self.P, self.D.ABOUT, self.D.PAGES["about_page"]
        body = self.page_hero(X["kicker"], A["title"], A["text"][0]) + self.section(None, "".join(f"<p class=lead>{e(t)}</p>" for t in A["text"][1:]))
        body += self.section(A["privacy_title"], self.cards([(None, "", t) for t in A["privacy"]], "g2"), sid="privacy")
        self.out(P["about"], self.page(P["about"], A["title"], X["desc"], body))

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
        self.build_tools(); self.build_about(); self.build_glossary()


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
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>404 · The Love Theory</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link href="{FONTS}" rel="stylesheet"><link rel="stylesheet" href="/assets/style.min.css"></head>
<body><main class="wrap" style="padding:80px 20px"><p class="eyebrow">404</p><h1>{e(nf_en["title"])}</h1><p class="lead">{e(nf_en["lead"])} <span lang="pt-BR">{e(nf_pt["title"])} {e(nf_pt["lead"])}</span></p><p class="row"><a class="btn" href="/">{e(nf_en["cta"])}</a> <a class="btn ghost" href="/pt/" lang="pt-BR">{e(nf_pt["cta"])}</a></p></main></body></html>
""")
    write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#d8408f"/><path fill="#fff" d="M32 50.8l-3.5-3.2C19.4 39.4 13.3 33.9 13.3 27.2c0-5.5 4.3-9.8 9.8-9.8 3.1 0 6.1 1.4 8.9 4.3 2.8-2.9 5.8-4.3 8.9-4.3 5.5 0 9.8 4.3 9.8 9.8 0 6.7-6.1 12.2-15.2 20.4L32 50.8z"/></svg>')
    write("CNAME", HOST + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"name": "The Love Theory", "short_name": "Love Theory", "start_url": "/", "display": "standalone", "background_color": "#f7efe7", "theme_color": "#f3b4cc", "lang": "en",
               "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def build_sitemap(sites):
    urls = []
    for s in sites:
        urls += [s.url(p) for p in s.pages() if p != s.P["portraits"]]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + [f"<url><loc>{u}</loc><lastmod>{BUILT}</lastmod></url>" for u in urls] + ["</urlset>"]
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
