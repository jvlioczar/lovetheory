/* The Love Theory — motor das ferramentas. Tudo roda no navegador; nada sai do aparelho.
   Os textos de interface vêm de D.ui (um dicionário por idioma); os caminhos das páginas, de D.paths;
   as propriedades têm uma chave estável (D.props[i].key) para o motor não depender do idioma. */
(function () {
  "use strict";
  var D = window.LT; if (!D) return;
  var T = D.ui, P = D.paths;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var fmt = function (s, o) { return String(s).replace(/\{(\w+)\}/g, function (_, k) { return o && o[k] != null ? o[k] : "{" + k + "}"; }); };
  var fill = function (t, nome) { return esc(t).replace(/\{nome\}/g, "<b>" + esc(nome || T.default_person) + "</b>"); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("lt:" + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("lt:" + k, JSON.stringify(v)); } catch (e) { } }
  };
  var uid = function () { return Date.now().toString(36) + Math.random().toString(36).slice(2, 6); };
  var fmtDate = function (iso) { var d = new Date(iso); return d.toLocaleDateString(D.lang, { day: "numeric", month: "long", year: "numeric" }); };
  var mean = function (a) { return a.length ? a.reduce(function (x, y) { return x + y; }, 0) / a.length : 0; };
  var r1 = function (x) { return Math.round(x * 10) / 10; };
  var PROPS = D.props, BY = {}; PROPS.forEach(function (p) { BY[p.key] = p; });
  var ORDER = PROPS.map(function (p) { return p.key; });
  var K = function (key) { return key; };   /* o motor trabalha com as chaves estáveis; o slug é só da URL */
  var names = function (keys) { return keys.map(function (k) { return BY[k].name; }).join(", "); };
  var relName = function (rel) { return (D.relations.filter(function (r) { return r[0] === rel; })[0] || ["", ""])[1]; };

  /* ---------- radar ---------- */
  function radar(values, values2, opts) {
    opts = opts || {};
    var W = 560, C = W / 2, R = 160, n = ORDER.length, labelsR = R + 28;
    var pt = function (i, v) { var a = -Math.PI / 2 + i * 2 * Math.PI / n; var rr = R * v / 10; return [C + rr * Math.cos(a), C + rr * Math.sin(a)]; };
    var s = '<svg class="radar" viewBox="0 0 ' + W + ' ' + W + '" role="img" aria-label="' + esc(T.radar_aria) + '">';
    [2.5, 5, 7.5, 10].forEach(function (lv) { s += '<polygon class="grid-l" points="' + ORDER.map(function (_, i) { return pt(i, lv).join(","); }).join(" ") + '"/>'; });
    ORDER.forEach(function (_, i) { var p = pt(i, 10); s += '<line class="axis" x1="' + C + '" y1="' + C + '" x2="' + p[0] + '" y2="' + p[1] + '"/>'; });
    var poly = function (vals, cls) { return '<polygon class="' + cls + '" points="' + ORDER.map(function (k, i) { return pt(i, k === K("sombras") ? 0 : (vals[k] || 0)).join(","); }).join(" ") + '"/>'; };
    var sh = values[K("sombras")] || 0;
    if (sh > 0 && !opts.noShadow) s += '<circle class="shadow" cx="' + C + '" cy="' + C + '" r="' + (R * sh / 10) + '"/>';
    if (values2) s += poly(values2, "poly2");
    s += poly(values, "poly");
    ORDER.forEach(function (k, i) {
      var a = -Math.PI / 2 + i * 2 * Math.PI / n, x = C + labelsR * Math.cos(a), y = C + labelsR * Math.sin(a);
      var anchor = Math.abs(Math.cos(a)) < .2 ? "middle" : (Math.cos(a) > 0 ? "start" : "end");
      s += '<text class="lbl" x="' + x.toFixed(1) + '" y="' + (y + 3).toFixed(1) + '" text-anchor="' + anchor + '">' + esc(BY[k].name) + '</text>';
    });
    return s + "</svg>";
  }
  function bars(values, values2) {
    return '<div class="bars">' + ORDER.map(function (k) {
      var v = values[k] || 0, cls = k === K("sombras") ? " gray" : "";
      return '<div class="bar"><span>' + esc(BY[k].name) + '</span><i><b class="' + cls + '" style="width:' + (v * 10) + '%"></b></i><span class="v">' + r1(v) + (values2 ? ' <small class="muted">(' + r1(values2[k] || 0) + ')</small>' : "") + '</span></div>';
    }).join("") + "</div>";
  }
  function rangeInput(name, val, labels) {
    return '<div class="range"><input type="range" min="0" max="10" step="1" name="' + name + '" value="' + val + '" oninput="this.nextElementSibling.value=this.value"><output>' + val + '</output></div>' +
      '<div class="range-labels"><span>' + esc(labels ? labels[0] : T.nothing) + '</span><span>' + esc(labels ? labels[1] : T.totally) + '</span></div>';
  }
  function readRange(form, name) { var el = form.querySelector('[name="' + name + '"]'); return el ? +el.value : 0; }
  function readRadio(form, name) { var el = form.querySelector('[name="' + name + '"]:checked'); return el ? el.value : null; }
  var lis = function (arr) { return "<ul>" + arr.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>"; };

  /* ---------- tipos, flags, notas ---------- */
  function rankTypes(values) {
    return D.types.map(function (t) {
      var keys = Object.keys(t.profile), d = Math.sqrt(mean(keys.map(function (k) { return Math.pow((values[K(k)] || 0) - t.profile[k], 2); })));
      return { t: t, d: d, score: Math.max(0, Math.round((1 - d / 10) * 100)) };
    }).sort(function (a, b) { return a.d - b.d; });
  }
  function portraitFlags(values) {
    return D.portraitFlags.filter(function (f) { return f.when.every(function (c) { var v = values[K(c[0])] || 0; return c[1] === ">=" ? v >= c[2] : v <= c[2]; }); });
  }
  function rootNotes(roots) {
    var out = [], seen = {};
    Object.keys(roots || {}).forEach(function (k) { var r = roots[k]; if (r && D.rootNotes[r] && !seen[r]) { seen[r] = 1; out.push(D.rootNotes[r]); } });
    return out;
  }
  function savePortrait(p) { var all = store.get("portraits", []); all.unshift(p); store.set("portraits", all); return p; }

  /* ---------- imagem para compartilhar (canvas, três formatos, download) ---------- */
  var FMTS = [{ k: "post", w: 1080, h: 1350 }, { k: "square", w: 1080, h: 1080 }, { k: "story", w: 1080, h: 1920 }];
  function wrapText(x, text, maxW, maxLines) {
    var words = String(text).split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) { var t = cur ? cur + " " + w : w; if (x.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; });
    if (cur) lines.push(cur);
    if (maxLines && lines.length > maxLines) { lines = lines.slice(0, maxLines); lines[maxLines - 1] = lines[maxLines - 1].replace(/\s+\S*$/, "") + "…"; }
    return lines;
  }
  function rr(x, a, b, w, h, r) { if (x.roundRect) { x.beginPath(); x.roundRect(a, b, w, h, r); } else { x.beginPath(); x.rect(a, b, w, h); } }
  function canvasRadar(x, cx, cy, R, values, values2) {
    var n = ORDER.length, pt = function (i, v) { var a = -Math.PI / 2 + i * 2 * Math.PI / n; return [cx + R * v / 10 * Math.cos(a), cy + R * v / 10 * Math.sin(a)]; };
    x.save(); x.beginPath(); x.arc(cx, cy, R + 4, 0, Math.PI * 2); x.fillStyle = "#fff"; x.fill(); x.lineWidth = 3; x.strokeStyle = "#2a1d2c"; x.stroke();
    x.lineWidth = 1.5; x.strokeStyle = "#d9cdd3";
    [2.5, 5, 7.5, 10].forEach(function (lv) { x.beginPath(); ORDER.forEach(function (_, i) { var p = pt(i, lv); i ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1]); }); x.closePath(); x.stroke(); });
    var sh = values[K("sombras")] || 0; if (sh) { x.beginPath(); x.arc(cx, cy, R * sh / 10, 0, Math.PI * 2); x.fillStyle = "rgba(60,50,55,.22)"; x.fill(); }
    var poly = function (vals, fill, stroke, dash) {
      x.beginPath(); ORDER.forEach(function (k, i) { var p = pt(i, k === K("sombras") ? 0 : (vals[k] || 0)); i ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1]); }); x.closePath();
      x.fillStyle = fill; x.fill(); x.setLineDash(dash || []); x.lineWidth = 4; x.strokeStyle = stroke; x.stroke(); x.setLineDash([]);
    };
    if (values2) poly(values2, "rgba(42,29,44,.16)", "#2a1d2c", [8, 6]);
    poly(values, "rgba(216,64,143,.38)", "#b8236f");
    x.fillStyle = "#5b4a5e"; x.font = "600 " + Math.round(R * .105) + "px 'DM Sans', sans-serif";
    ORDER.forEach(function (k, i) { var a = -Math.PI / 2 + i * 2 * Math.PI / n, lx = cx + (R + R * .17) * Math.cos(a), ly = cy + (R + R * .17) * Math.sin(a); x.textAlign = Math.abs(Math.cos(a)) < .2 ? "center" : (Math.cos(a) > 0 ? "left" : "right"); x.fillText(BY[k].short || BY[k].name, lx, ly + R * .035); });
    x.restore();
  }
  function shareDialog(spec) {
    var dlg = $("dialog.share");
    if (!dlg) { dlg = document.createElement("dialog"); dlg.className = "share"; document.body.appendChild(dlg); dlg.addEventListener("click", function (ev) { if (ev.target === dlg) dlg.close(); }); }
    dlg.innerHTML = '<div class="share-in"><button type="button" class="share-x" aria-label="' + esc(T.close) + '">×</button><h3>' + esc(T.share_title) + '</h3><p class="muted">' + esc(T.share_text) + '</p><div class="opts">' +
      FMTS.map(function (f, i) { return '<label class="opt"><input type="radio" name="fmt" value="' + f.k + '"' + (i === 0 ? " checked" : "") + '> ' + esc(T.fmt[f.k]) + '</label>'; }).join("") +
      '</div><canvas width="1080" height="1350" aria-label="' + esc(T.share_preview) + '"></canvas><div class="actions"><button type="button" class="btn" data-dl>' + esc(T.download_png) + '</button></div></div>';
    var cv = $("canvas", dlg), fmtc = FMTS[0];
    function draw() {
      var W = fmtc.w, H = fmtc.h, sq = fmtc.k === "square"; cv.width = W; cv.height = H; var x = cv.getContext("2d");
      x.fillStyle = "#f7efe7"; x.fillRect(0, 0, W, H);
      x.fillStyle = "#e6d9d0"; for (var i = 20; i < W; i += 24) for (var j = 20; j < H; j += 24) { x.beginPath(); x.arc(i, j, 1.6, 0, 7); x.fill(); }
      var m = Math.round(W * .06), bar = Math.round(W * .05), pad = Math.round(W * .05);
      var px = m + pad, tw = W - (m + pad) * 2, bottom = H - m - pad;
      x.save(); x.translate(W / 2, H / 2); x.rotate(-.01); x.translate(-W / 2, -H / 2);
      rr(x, m + 8, m + 8, W - m * 2, H - m * 2, 28); x.fillStyle = "#2a1d2c"; x.fill();
      rr(x, m, m, W - m * 2, H - m * 2, 28); x.fillStyle = "#f8d2e0"; x.fill(); x.lineWidth = 3; x.strokeStyle = "#2a1d2c"; x.stroke();
      x.save(); x.beginPath(); rr(x, m, m, W - m * 2, bar, 28); x.clip(); x.fillStyle = "#cdb9e6"; x.fillRect(m, m, W - m * 2, bar); x.restore();
      x.beginPath(); x.moveTo(m, m + bar); x.lineTo(W - m, m + bar); x.stroke();
      [["#fff", 0], ["#f3b4cc", 1], ["#9fb0d4", 2]].forEach(function (c) { x.beginPath(); x.arc(m + bar * .55 + c[1] * bar * .55, m + bar / 2, bar * .17, 0, 7); x.fillStyle = c[0]; x.fill(); x.stroke(); });
      x.fillStyle = "#2a1d2c"; x.font = "600 " + Math.round(W * .02) + "px 'DM Sans', sans-serif"; x.textAlign = "right"; x.fillText("THE LOVE THEORY", W - m - bar * .5, m + bar * .64); x.textAlign = "left";
      var y = m + bar + Math.round(W * (sq ? .045 : .06));
      var kSize = Math.round(W * (sq ? .042 : .05)), tSize = Math.round(W * (sq ? .044 : .056)), tLH = Math.round(tSize * 1.12);
      var titleTxt = spec.rows && H < 1600 && spec.shortTitle ? spec.shortTitle : spec.title;
      x.font = "700 " + tSize + "px DynaPuff, cursive"; var tLines = wrapText(x, titleTxt, tw, 2);
      x.fillStyle = "#b8236f"; x.font = "700 " + kSize + "px Caveat, cursive"; x.fillText(spec.kicker, px, y); y += Math.round(kSize * .55);
      x.fillStyle = "#2a1d2c"; x.font = "700 " + tSize + "px DynaPuff, cursive"; tLines.forEach(function (l) { y += tLH; x.fillText(l, px, y); });
      y += Math.round(W * .035);
      var lSize = Math.round(W * (sq ? .025 : .029)), lLH = Math.round(lSize * 1.4), fSize = Math.round(W * .036);
      x.font = "400 " + lSize + "px 'DM Sans', sans-serif";
      var maxItems = spec.rows ? (sq ? 0 : (H < 1600 ? 1 : 2)) : (sq ? 2 : 3);
      var items = (spec.lines || []).slice(0, maxItems).map(function (l) { return wrapText(x, l, tw, 2); });
      var linesH = items.reduce(function (acc, ls) { return acc + ls.length * lLH + Math.round(lLH * .35); }, 0);
      var footH = linesH + Math.round(fSize * 1.3) + Math.round(W * .03);
      var avail = bottom - footH - y;
      if (spec.values) {
        var labelM = Math.round(W * .085), R = Math.min(Math.round(W * .3), Math.round(avail / 2) - labelM);
        if (R > 60) { canvasRadar(x, W / 2, y + labelM + R, R, spec.values, spec.values2); y += R * 2 + labelM * 2; }
      } else if (spec.rows) {
        var cols = H < 1600 ? 2 : 1, gapC = Math.round(W * .05), cw = Math.round((tw - gapC * (cols - 1)) / cols), perCol = Math.ceil(spec.rows.length / cols);
        var rowH = Math.min(Math.round(W * (cols === 2 ? .085 : .072)), Math.floor(avail / perCol)), y0 = y;
        spec.rows.forEach(function (r, i) {
          var c = Math.floor(i / perCol), cx0 = px + c * (cw + gapC), ry = y0 + (i - c * perCol) * rowH;
          x.textAlign = "right"; x.fillStyle = "#b8236f"; x.font = "700 " + Math.round(rowH * .32) + "px Caveat, cursive"; x.fillText(r.pos, cx0 + cw, ry + rowH * .3);
          var posW = x.measureText(r.pos).width, nm = r.name;
          x.textAlign = "left"; x.fillStyle = "#2a1d2c"; x.font = "700 " + Math.round(rowH * .25) + "px 'DM Sans', sans-serif";
          while (nm.length > 3 && x.measureText(nm).width > cw - posW - Math.round(W * .015)) nm = nm.replace(/…$/, "").slice(0, -1) + "…";
          x.fillText(nm, cx0, ry + rowH * .28);
          var by = ry + rowH * .42, bh = Math.round(rowH * .2);
          rr(x, cx0, by, cw, bh, 99); x.fillStyle = "#fff"; x.fill(); x.lineWidth = 2; x.strokeStyle = "#2a1d2c"; x.stroke();
          if (r.presumed != null) { x.fillStyle = "#2a1d2c"; x.fillRect(cx0 + cw * r.presumed / 4 - 1.5, by - bh * .3, 3, bh * 1.6); }
          x.beginPath(); x.arc(cx0 + cw * r.x / 4, by + bh / 2, bh * .5, 0, 7); x.fillStyle = "#d8408f"; x.fill(); x.stroke();
          x.fillStyle = "#8c7a8f"; x.font = "600 " + Math.round(rowH * .19) + "px 'DM Sans', sans-serif";
          x.textAlign = "left"; x.fillText(r.poles[0], cx0, by + bh + rowH * .22); x.textAlign = "right"; x.fillText(r.poles[1], cx0 + cw, by + bh + rowH * .22);
        });
        x.textAlign = "left"; y = y0 + perCol * rowH;
      } else if (spec.bars) {
        var bH = Math.round(W * .075), bGap = Math.round(W * .06); y += Math.round(W * .05);
        spec.bars.forEach(function (b, i) {
          var by = y + i * (bH + bGap);
          x.fillStyle = "#2a1d2c"; x.font = "700 " + Math.round(W * .03) + "px 'DM Sans', sans-serif"; x.textAlign = "left"; x.fillText(b.label, px, by - Math.round(W * .012));
          x.textAlign = "right"; x.font = "700 " + Math.round(W * .05) + "px DynaPuff, cursive"; x.fillStyle = "#b8236f"; x.fillText(b.pct + "%", px + tw, by - Math.round(W * .012)); x.textAlign = "left";
          rr(x, px, by, tw, bH, 99); x.fillStyle = "#fff"; x.fill(); x.lineWidth = 3; x.strokeStyle = "#2a1d2c"; x.stroke();
          if (b.pct > 0) { rr(x, px, by, Math.max(bH, tw * b.pct / 100), bH, 99); x.fillStyle = i === 0 ? "#d8408f" : "#2a1d2c"; x.fill(); }
        });
        y += spec.bars.length * (bH + bGap) + Math.round(W * .02);
      }
      var fy = bottom - Math.round(fSize * .3), ly = fy - Math.round(fSize * 1.3) - linesH + lLH, lastY = y;
      if (ly < y + lLH) ly = y + lLH;
      x.fillStyle = "#2a1d2c"; x.font = "400 " + lSize + "px 'DM Sans', sans-serif";
      items.forEach(function (ls) { ls.forEach(function (ln) { x.fillText(ln, px, ly); lastY = ly; ly += lLH; }); ly += Math.round(lLH * .35); });
      x.font = "700 " + fSize + "px Caveat, cursive"; x.fillStyle = "#b8236f"; x.fillText(location.host.replace(/^www\./, "") || D.host, px, fy);
      x.restore();
      cv.dataset.fit = (lastY <= fy - Math.round(fSize * 1.05)) ? "ok" : "overflow";
    }
    var ready = document.fonts && document.fonts.load ? Promise.all([document.fonts.load("700 40px Caveat"), document.fonts.load("700 40px DynaPuff"), document.fonts.load("600 20px 'DM Sans'")]) : Promise.resolve();
    ready.then(draw, draw);
    dlg.querySelectorAll("[name=fmt]").forEach(function (r) { r.addEventListener("change", function () { fmtc = FMTS.filter(function (f) { return f.k === r.value; })[0]; draw(); }); });
    $(".share-x", dlg).addEventListener("click", function () { dlg.close(); });
    $("[data-dl]", dlg).addEventListener("click", function () {
      cv.toBlob(function (blob) { var a = document.createElement("a"), u = URL.createObjectURL(blob); a.href = u; a.download = spec.file + "-" + fmtc.k + ".png"; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(u); a.remove(); }, 1000); }, "image/png");
    });
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  }
  function shareBtn(label) { return '<button class="btn ghost" type="button" data-share>' + esc(label || T.share_btn) + '</button>'; }

  /* ---------- Love Scale ---------- */
  function scale(root) {
    var st = { step: 0, nome: "", rel: "parceiro", mode: "quick", thermo: null, values: {}, items: {}, roots: {}, expect: {}, weight: {} };
    function render() {
      var h = "";
      if (st.step === 0) {
        h = '<form class="step" id="f0"><h2>' + esc(T.s_who) + '</h2><p class="muted">' + esc(T.nick_note) + '</p>' +
          '<div class="field"><label>' + esc(T.name) + '</label><input type="text" name="nome" required placeholder="' + esc(T.name_ph) + '" value="' + esc(st.nome) + '"></div>' +
          '<div class="field"><label>' + esc(T.relation) + '</label><select name="rel">' + D.relations.map(function (r) { return '<option value="' + r[0] + '"' + (r[0] === st.rel ? " selected" : "") + '>' + esc(r[1]) + '</option>'; }).join("") + '</select></div>' +
          '<div class="field"><label>' + esc(T.version) + '</label><div class="opts">' +
          '<label class="opt"><input type="radio" name="mode" value="quick" checked> ' + esc(T.quick_opt) + '</label>' +
          '<label class="opt"><input type="radio" name="mode" value="deep"> ' + esc(T.deep_opt) + '</label></div></div>' +
          '<p class="muted">' + esc(T.same_ruler) + '</p><div class="actions"><button class="btn" type="submit">' + esc(T.start) + '</button></div></form>';
      } else if (st.step === 1) {
        h = '<form class="step" id="f1"><h2>' + esc(T.thermo_title) + '</h2><p class="muted">' + esc(T.thermo_text) + '</p>' +
          D.thermo.map(function (t, i) { return '<div class="item"><p class="q">' + esc(t.q) + '</p>' + rangeInput("t" + i, 5) + '</div>'; }).join("") +
          '<div class="actions"><button class="btn" type="submit">' + esc(T.continue_) + '</button></div></form>';
      } else if (st.step >= 2 && st.step < 2 + PROPS.length) {
        var p = PROPS[st.step - 2], deep = st.mode === "deep", idx = st.step - 2;
        var q = (st.rel === "animal" && p.animal) ? p.animal : p;
        h = '<div class="progress"><i style="width:' + Math.round(idx / PROPS.length * 100) + '%"></i></div><form class="step" id="fp"><p class="eyebrow">' + fmt(T.step_of, { i: idx + 1, n: PROPS.length }) + ' · ' + esc(p.name) + '</p><h2>' + esc(p.lead) + '</h2>';
        if (deep) q.deep.forEach(function (t, i) { h += '<div class="item"><p class="q">' + fill(t, st.nome) + '</p>' + rangeInput("d" + i, 5) + '</div>'; });
        else h += '<div class="item"><p class="q">' + fill(q.quick, st.nome) + '</p>' + rangeInput("d0", 5) + '</div>';
        var rq = q.root_q || p.root_q;
        if (deep || p.quick_root) h += '<div class="item"><p class="q">' + fill(rq[0], st.nome) + '</p><div class="opts">' + rq[1].map(function (o) { return '<label class="opt"><input type="radio" name="root" value="' + esc(o[1]) + '"> ' + fill(o[0], st.nome) + '</label>'; }).join("") + '</div></div>';
        if (deep) {
          h += '<div class="item"><p class="q">' + fill(D.expectQ, st.nome) + '</p><div class="opts">' + D.expectOpts.map(function (o) { return '<label class="opt"><input type="radio" name="expect" value="' + o[1] + '"' + (o[1] === 0 ? " checked" : "") + '> ' + esc(o[0]) + '</label>'; }).join("") + '</div></div>';
          h += '<div class="item"><p class="q">' + esc(D.weightQ) + '</p>' + rangeInput("w", 5, [T.nothing, T.much]) + '</div>';
        }
        h += '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(idx + 1 === PROPS.length ? T.see_portrait : T.next) + '</button></div></form>';
      } else h = result();
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f) {
        f.addEventListener("submit", function (e) { e.preventDefault(); next(f); });
        var b = f.querySelector("[data-back]"); if (b) b.addEventListener("click", function () { st.step--; render(); });
      }
      window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
    }
    function next(f) {
      if (st.step === 0) { st.nome = f.nome.value.trim() || T.default_person; st.rel = f.rel.value; st.mode = readRadio(f, "mode") || "quick"; st.step = 1; }
      else if (st.step === 1) {
        var av = [], needy = 0;
        D.thermo.forEach(function (t, i) { var v = readRange(f, "t" + i); if (t.needy) needy = v; else av.push(t.reverse ? 10 - v : v); });
        st.thermo = { avail: r1(mean(av)), needy: needy }; st.step = 2;
      } else {
        var p = PROPS[st.step - 2], n = st.mode === "deep" ? 3 : 1, vals = [];
        for (var i = 0; i < n; i++) vals.push(readRange(f, "d" + i));
        st.values[p.key] = r1(mean(vals)); st.items[p.key] = vals;
        var rt = readRadio(f, "root"); if (rt) st.roots[p.key] = rt;
        if (st.mode === "deep") { st.expect[p.key] = +(readRadio(f, "expect") || 0); st.weight[p.key] = readRange(f, "w"); }
        st.step++;
        if (st.step === 2 + PROPS.length) st.portrait = savePortrait({ id: uid(), nome: st.nome, rel: st.rel, mode: st.mode, date: new Date().toISOString(), values: st.values, roots: st.roots, expect: st.expect, weight: st.weight, thermo: st.thermo, types: rankTypes(st.values).slice(0, 2).map(function (x) { return x.t.slug; }) });
      }
      render();
    }
    function result() {
      var v = st.values, types = rankTypes(v), flags = portraitFlags(v), notes = rootNotes(st.roots), th = st.thermo, rn = relName(st.rel);
      var h = '<div class="step result"><p class="eyebrow">' + esc(T.portrait) + ' · ' + esc(rn) + ' · ' + esc(fmtDate(new Date().toISOString())) + '</p><h2>' + fmt(esc(T.result_title), { nome: esc(st.nome) }) + '</h2>' +
        '<div class="radar-wrap">' + radar(v) + bars(v) + '</div><p class="muted">' + esc(T.shadow_note) + '</p></div>';
      h += '<div class="step"><h3>' + esc(T.closest_title) + '</h3><div class="grid g2">' + types.slice(0, 2).map(function (x, i) {
        return '<div class="type-card' + (i === 0 ? " first" : "") + '"><p class="num">' + esc(i === 0 ? T.closest : T.second) + ' · ' + fmt(esc(T.proximity), { p: x.score }) + '</p><h3>' + esc(x.t.name) + '</h3><p class="small">' + esc(x.t.text) + '</p></div>';
      }).join("") + '</div><p class="muted">' + esc(T.type_note) + ' <a href="' + P.types + '">' + esc(T.all_types) + '</a></p></div>';
      if (flags.length) h += '<div class="step"><h3>' + esc(T.combos_title) + '</h3>' + lis(flags.map(function (f) { return f.text; })) + '</div>';
      var ind = [];
      if (v[K("afeto")] >= 7 && v[K("admiracao")] <= 4) ind.push(T.r_love_no_admire);
      if (v[K("admiracao")] >= 7 && v[K("atracao")] <= 2) ind.push(T.r_admire_no_attr);
      if (st.mode === "deep") {
        var gaps = ORDER.filter(function (k) { return (st.weight[k] || 0) - (v[k] || 0) >= 4 && k !== K("sombras"); });
        if (gaps.length) ind.push(fmt(T.r_weight_gap, { list: names(gaps) }));
        var surp = ORDER.filter(function (k) { return st.expect[k] >= 1; }), dis = ORDER.filter(function (k) { return st.expect[k] <= -1; });
        if (surp.length) ind.push(fmt(T.r_surprise, { list: names(surp) }));
        if (dis.length) ind.push(fmt(T.r_disappoint, { list: names(dis) }));
      }
      if (ind.length) h += '<div class="step"><h3>' + esc(T.readings) + '</h3>' + lis(ind) + '</div>';
      if (notes.length) h += '<div class="step"><h3>' + esc(T.from_title) + '</h3>' + lis(notes) + '</div>';
      if (th) h += '<div class="note">' + esc(th.avail <= 3 ? fmt(T.thermo_closed, { a: th.avail }) : th.needy >= 8 ? T.thermo_needy : fmt(T.thermo_ok, { a: th.avail })) + '</div>';
      h += '<div class="step"><p>' + esc(T.saved_text) + '</p><div class="actions"><a class="btn" href="' + P.portraits + '">' + esc(T.my_portraits_btn) + '</a>' + shareBtn() + '<button class="btn ghost" type="button" data-again>' + esc(T.another) + '</button></div></div>';
      setTimeout(function () {
        var b = root.querySelector("[data-again]"); if (b) b.addEventListener("click", function () { st = { step: 0, nome: "", rel: st.rel, mode: st.mode, values: {}, items: {}, roots: {}, expect: {}, weight: {} }; render(); });
        var s = root.querySelector("[data-share]"); if (s) s.addEventListener("click", function () {
          var hi = ORDER.filter(function (k) { return k !== K("sombras"); }).sort(function (a, b) { return v[b] - v[a]; }).slice(0, 3);
          shareDialog({ file: "love-scale", kicker: T.scale_name + " · " + rn, title: fmt(T.result_title, { nome: st.nome }), values: v,
            lines: [fmt(T.share_closest, { t: types[0].t.name, p: types[0].score }), fmt(T.share_top, { list: names(hi) }), flags.length ? flags[0].text.split(":")[0] + "." : T.share_default] });
        });
      }, 0);
      return h;
    }
    render();
  }

  /* ---------- Retratos e constelação ---------- */
  function portraits(root) {
    var all = store.get("portraits", []);
    if (!all.length) { root.innerHTML = '<div class="step"><h2>' + esc(T.p_none_title) + '</h2><p>' + fmt(esc(T.p_none_text), { link: '<a href="' + P.scale + '">' + esc(T.scale_name) + '</a>' }) + '</p></div>'; return; }
    var byName = {}; all.forEach(function (p) { (byName[p.nome] = byName[p.nome] || []).push(p); });
    var nms = Object.keys(byName), h = "";
    if (nms.length >= 3) {
      var latest = nms.map(function (n) { return byName[n][0]; }), avg = {};
      ORDER.forEach(function (k) { avg[k] = r1(mean(latest.map(function (p) { return p.values[k] || 0; }))); });
      var sorted = ORDER.filter(function (k) { return k !== K("sombras"); }).sort(function (a, b) { return avg[b] - avg[a]; });
      var hi = sorted.slice(0, 3), lo = sorted.slice(-3).reverse(), closed = latest.every(function (p) { return p.thermo && p.thermo.avail <= 3; });
      h += '<div class="step result"><p class="eyebrow">' + fmt(esc(T.const_kicker), { n: nms.length }) + '</p><h2>' + esc(T.const_title) + '</h2><div class="radar-wrap">' + radar(avg) + bars(avg) + '</div>' +
        '<p>' + fmt(esc(T.const_text), { hi: "<b>" + esc(names(hi)) + "</b>", lo: "<b>" + esc(names(lo)) + "</b>" }) + '</p>' + (closed ? '<div class="note">' + esc(T.const_closed) + '</div>' : "");
      var sd = store.get("selfdiscover");
      if (sd && sd.values) {
        var ap = sd.values.apego;
        if (ap <= 1 && avg[K("posse")] >= 6) h += '<div class="note">' + esc(T.apego_low) + '</div>';
        if (ap >= 3 && avg[K("posse")] <= 3 && avg[K("dependencia")] <= 3) h += '<div class="note">' + esc(T.apego_high) + '</div>';
      }
      var sl = store.get("selflove");
      if (sl && sl.values) {
        var gapsSelf = ORDER.filter(function (k) { return k !== K("sombras") && avg[k] - (sl.values[k] || 0) >= 4; });
        if (gapsSelf.length) h += '<div class="note">' + fmt(esc(T.self_gap), { list: esc(names(gapsSelf)) }) + '</div>';
      }
      h += "</div>";
    } else h += '<div class="note">' + fmt(esc(T.const_need), { n: nms.length }) + '</div>';
    h += '<div class="step"><h2>' + esc(T.saved_title) + '</h2>' + nms.map(function (n) {
      var ps = byName[n];
      return '<details' + (nms.length === 1 ? " open" : "") + '><summary>' + esc(n) + ' <span class="muted">· ' + ps.length + " " + esc(ps.length > 1 ? T.portraits_pl : T.portrait_sg) + '</span></summary>' +
        ps.map(function (p, i) {
          var prev = ps[i + 1];
          var deltas = prev ? ORDER.filter(function (k) { return Math.abs((p.values[k] || 0) - (prev.values[k] || 0)) >= 2; }).map(function (k) { var d = r1((p.values[k] || 0) - (prev.values[k] || 0)); return BY[k].name + " " + (d > 0 ? "+" : "") + d; }) : [];
          return '<div class="item"><p class="muted">' + esc(fmtDate(p.date)) + ' · ' + esc(p.mode === "deep" ? T.deep_label : T.quick_label) + (p.types ? ' · ' + esc(p.types.map(function (s) { var t = D.types.filter(function (x) { return x.slug === s; })[0]; return t ? t.name : s; }).join(", ")) : "") + '</p>' +
            '<div class="radar-wrap">' + radar(p.values, prev ? prev.values : null) + bars(p.values, prev ? prev.values : null) + '</div>' +
            (deltas.length ? '<p class="small">' + fmt(esc(T.changed), { d: esc(deltas.join(" · ")) }) + '</p>' : (prev ? '<p class="small muted">' + esc(T.unchanged) + '</p>' : "")) +
            '<button class="btn sm ghost" type="button" data-del="' + p.id + '">' + esc(T.delete_) + '</button></div>';
        }).join("") + "</details>";
    }).join("") + "</div>";
    root.innerHTML = h;
    root.querySelectorAll("[data-del]").forEach(function (b) {
      b.addEventListener("click", function () { if (!confirm(T.confirm_delete)) return; store.set("portraits", store.get("portraits", []).filter(function (p) { return p.id !== b.getAttribute("data-del"); })); portraits(root); });
    });
  }

  /* ---------- Self Love ---------- */
  function selfLove(root) {
    var saved = store.get("selflove");
    function form() {
      root.innerHTML = '<form class="step"><h2>' + esc(T.sl_title) + '</h2><p class="muted">' + esc(T.sl_text) + '</p>' +
        PROPS.map(function (p, i) { return '<div class="item"><p class="q">' + esc(p.selflove) + '</p>' + rangeInput("s" + i, 5, p.key === K("sombras") ? [T.nothing, T.much] : null) + '</div>'; }).join("") +
        '<div class="actions"><button class="btn" type="submit">' + esc(T.see_portrait) + '</button></div></form>';
      root.querySelector("form").addEventListener("submit", function (e) {
        e.preventDefault(); var v = {}; PROPS.forEach(function (p, i) { v[p.key] = readRange(e.target, "s" + i); });
        saved = { date: new Date().toISOString(), values: v }; store.set("selflove", saved); show();
      });
    }
    function show() {
      var v = saved.values, g = function (k) { return v[K(k)]; };
      var care = mean([g("afeto"), g("suporte"), g("protecao"), g("confianca"), g("liberdade"), g("investimento")]), infl = mean([g("admiracao"), g("atracao"), g("paixao")]), open = mean([g("abertura"), g("afeto")]);
      var notes = [];
      if (care < 4) notes.push(T.sl_deficit);
      if (infl >= 8 && open <= 4) notes.push(T.sl_inflation);
      if (g("sombras") >= 6) notes.push(T.sl_shadows);
      if (g("dependencia") >= 7) notes.push(T.sl_dependence);
      if (g("liberdade") <= 3) notes.push(T.sl_freedom);
      if (!notes.length) notes.push(T.sl_balanced);
      var h = '<div class="step result"><p class="eyebrow">' + esc(T.selflove_name) + ' · ' + esc(fmtDate(saved.date)) + '</p><h2>' + esc(T.sl_result) + '</h2><div class="radar-wrap">' + radar(v) + bars(v) + '</div></div>' +
        '<div class="step"><h3>' + esc(T.readings) + '</h3>' + lis(notes);
      var all = store.get("portraits", []);
      if (all.length) {
        var byName = {}; all.forEach(function (p) { if (!byName[p.nome]) byName[p.nome] = p; });
        var latest = Object.keys(byName).map(function (n) { return byName[n]; });
        var gaps = ORDER.filter(function (k) { return k !== K("sombras") && mean(latest.map(function (p) { return p.values[k] || 0; })) - (v[k] || 0) >= 4; });
        if (gaps.length) h += '<div class="note">' + fmt(esc(T.sl_gap), { list: esc(names(gaps)) }) + '</div>';
      }
      h += '<div class="actions">' + shareBtn() + '<button class="btn ghost" type="button" data-redo>' + esc(T.redo) + '</button></div></div>';
      root.innerHTML = h;
      root.querySelector("[data-redo]").addEventListener("click", form);
      root.querySelector("[data-share]").addEventListener("click", function () {
        shareDialog({ file: "self-love", kicker: T.selflove_name, title: T.sl_share_title, values: v, lines: notes.slice(0, 2).map(function (t) { return t.split(":")[0] + "."; }) });
      });
    }
    if (saved) show(); else form();
  }

  /* ---------- Teste de Casal ---------- */
  var b64 = {
    enc: function (obj) {
      var s = ORDER.map(function (k) { return (obj.a[k] || [0, 0, 0, 0]).map(function (v) { return v === 10 ? "A" : String(v); }).join(""); }).join("");
      var t = obj.t ? D.tastes.map(function (c) { return (obj.t[c[0]] || []).map(function (i) { return i.toString(36); }).join(""); }).join(".") : "";
      var l = obj.l ? (obj.l.give || []).map(function (i) { return i.toString(36); }).join("") + "." + (obj.l.receive || []).map(function (i) { return i.toString(36); }).join("") : "";
      var xs = obj.x ? ["vinculo-publico", "status"].map(function (k) { return obj.x[k] == null ? "-" : String(obj.x[k]); }).join("") : "";
      var raw = unescape(encodeURIComponent(JSON.stringify({ v: 2, me: obj.me, you: obj.you, rel: obj.rel, s: s, t: t, l: l, x: xs })));
      return btoa(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    },
    dec: function (str) {
      try {
        str = str.replace(/-/g, "+").replace(/_/g, "/"); while (str.length % 4) str += "=";
        var o = JSON.parse(decodeURIComponent(escape(atob(str)))); if (!o || o.v !== 2 || typeof o.s !== "string") return null;
        var a = {}; ORDER.forEach(function (k, i) { a[k] = o.s.substr(i * 4, 4).split("").map(function (c) { return c === "A" ? 10 : +c; }); });
        var t = null;
        if (o.t) { t = {}; o.t.split(".").forEach(function (part, i) { if (D.tastes[i]) t[D.tastes[i][0]] = part.split("").filter(Boolean).map(function (c) { return parseInt(c, 36); }); }); }
        var l = null;
        if (o.l) { var lp = o.l.split("."); l = { give: (lp[0] || "").split("").filter(Boolean).map(function (c) { return parseInt(c, 36); }), receive: (lp[1] || "").split("").filter(Boolean).map(function (c) { return parseInt(c, 36); }) }; }
        var xv = null;
        if (o.x && o.x.length === 2) { xv = {}; ["vinculo-publico", "status"].forEach(function (k, i) { if (o.x[i] !== "-") xv[k] = +o.x[i]; }); }
        return { me: o.me, you: o.you, rel: o.rel, a: a, t: t, l: l, x: xv };
      } catch (e) { return null; }
    }
  };
  function hashParams() { var o = {}; location.hash.replace(/^#/, "").split("&").forEach(function (kv) { var i = kv.indexOf("="); if (i > 0) o[kv.slice(0, i)] = kv.slice(i + 1); }); return o; }
  function couple(root) {
    var hp = hashParams(), p1 = hp.p1 ? b64.dec(hp.p1) : null, p2 = hp.p2 ? b64.dec(hp.p2) : null;
    var LAYERS = T.layers;
    var st = { step: 0, me: "", you: "", rel: "parceiro", ans: {} };
    if (p1 && !p2) { st.you = p1.me; st.me = p1.you; st.rel = p1.rel; }
    function base() { var sd = store.get("selfdiscover"); return { v: 1, me: st.me, you: st.you, rel: st.rel, a: st.ans, t: sd && sd.tastes ? sd.tastes : null, l: sd && sd.langs ? sd.langs : null, x: sd && sd.values ? { "vinculo-publico": sd.values["vinculo-publico"], status: sd.values.status } : null }; }
    function render() {
      var h = "";
      if (p1 && p2) { root.innerHTML = results(p1, p2); wireShare(p1, p2); return; }
      if (st.step === 0) {
        h = '<form class="step"><h2>' + (p1 ? fmt(esc(T.c_answered), { me: esc(p1.me) }) : esc(T.c_who)) + '</h2>' +
          '<p class="muted">' + (p1 ? fmt(esc(T.c_alone_p2), { me: esc(p1.me) }) : esc(T.c_alone_p1)) + '</p>' +
          '<div class="field"><label>' + esc(T.your_name) + '</label><input type="text" name="me" required value="' + esc(st.me) + '"></div>' +
          '<div class="field"><label>' + esc(T.other_name) + '</label><input type="text" name="you" required value="' + esc(st.you) + '"' + (p1 ? " readonly" : "") + '></div>' +
          '<div class="field"><label>' + esc(T.relation) + '</label><select name="rel"' + (p1 ? " disabled" : "") + '>' + D.relations.filter(function (r) { return r[0] !== "animal" && r[0] !== "fa"; }).map(function (r) { return '<option value="' + r[0] + '"' + (r[0] === st.rel ? " selected" : "") + '>' + esc(r[1]) + '</option>'; }).join("") + '</select></div>' +
          '<div class="actions"><button class="btn" type="submit">' + esc(T.start) + '</button></div></form>';
      } else if (st.step <= PROPS.length) {
        var p = PROPS[st.step - 1];
        h = '<div class="progress"><i style="width:' + Math.round((st.step - 1) / PROPS.length * 100) + '%"></i></div><form class="step"><p class="eyebrow">' + fmt(T.step_of, { i: st.step, n: PROPS.length }) + ' · ' + esc(p.name) + '</p><h2>' + esc(p.lead) + '</h2><p class="muted">' + fill(p.quick, st.you) + '</p>' +
          LAYERS.map(function (L) { return '<div class="item"><p class="q"><span class="tag">' + esc(L[0]) + '</span> ' + esc(L[1]) + ' <span class="muted">· ' + esc(L[2]) + '</span></p>' + rangeInput("l" + L[0], 5) + '</div>'; }).join("") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(st.step === PROPS.length ? T.finish : T.next) + '</button></div></form>';
      } else {
        var code = b64.enc(base()), url = location.href.split("#")[0] + "#" + (p1 ? "p1=" + hp.p1 + "&p2=" + code : "p1=" + code);
        h = '<div class="step"><h2>' + (p1 ? esc(T.c_done_p2) : fmt(esc(T.c_done_p1), { you: esc(st.you) })) + '</h2><p>' + (p1 ? fmt(esc(T.c_p2_text), { me: esc(p1.me) }) : fmt(esc(T.c_p1_text), { you: esc(st.you) })) + '</p>' +
          '<p class="code" id="cpl-url">' + esc(url) + '</p><div class="actions"><button class="btn" type="button" data-copy>' + esc(T.copy_link) + '</button>' + (navigator.share ? '<button class="btn ghost" type="button" data-share-link>' + esc(T.share_sys) + '</button>' : "") + '</div><p class="muted">' + esc(T.link_warn) + '</p></div>';
        if (p1) h += results(p1, base());
        setTimeout(function () {
          var c = root.querySelector("[data-copy]"); if (c) c.addEventListener("click", function () { navigator.clipboard && navigator.clipboard.writeText(url); c.textContent = T.copied; });
          var s = root.querySelector("[data-share-link]"); if (s) s.addEventListener("click", function () { navigator.share({ title: T.c_kicker, url: url }); });
          if (p1) wireShare(p1, base());
        }, 0);
      }
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f) {
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          if (st.step === 0) { st.me = f.me.value.trim(); st.you = f.you.value.trim(); st.rel = f.rel.value; }
          else { var p = PROPS[st.step - 1]; st.ans[p.key] = LAYERS.map(function (L) { return readRange(f, "l" + L[0]); }); }
          st.step++; render();
        });
        var b = f.querySelector("[data-back]"); if (b) b.addEventListener("click", function () { st.step--; render(); });
      }
      window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
    }
    function gapsOf(x, y) {
      var rows = [], g = function (k, lbl, a, b, who) { rows.push({ k: k, lbl: lbl, d: Math.abs(a - b), a: a, b: b, who: who }); };
      ORDER.forEach(function (k) {
        var A = x.a[k] || [0, 0, 0, 0], B = y.a[k] || [0, 0, 0, 0];
        g(k, fmt(T.g_read, { a: x.me, b: y.me }), A[0], B[1], T.who_read);
        g(k, fmt(T.g_read, { a: y.me, b: x.me }), B[0], A[1], T.who_read);
        g(k, T.g_each, A[0], B[0], T.who_asym);
        g(k, T.g_agreed, A[2], B[2], T.who_agreed);
        g(k, T.g_assumed, A[3], B[3], T.who_assumed);
      });
      rows.sort(function (a, b) { return b.d - a.d; });
      var vx = {}, vy = {}; ORDER.forEach(function (k) { vx[k] = (x.a[k] || [0])[0]; vy[k] = (y.a[k] || [0])[0]; });
      return { rows: rows, big: rows.slice(0, 3), vx: vx, vy: vy };
    }
    function results(x, y) {
      var r = gapsOf(x, y), rows = r.rows, big = r.big, vx = r.vx, vy = r.vy;
      var lib = { x: (x.a[K("liberdade")] || [0])[0], y: (y.a[K("liberdade")] || [0])[0] }, pos = { x: (x.a[K("posse")] || [0])[0], y: (y.a[K("posse")] || [0])[0] };
      var h = '<div class="step result"><p class="eyebrow">' + esc(T.c_kicker) + ' · ' + esc(x.me) + ' & ' + esc(y.me) + '</p><h2>' + esc(T.c_title) + '</h2>' +
        '<div class="radar-wrap">' + radar(vx, vy) + '<div><p>' + fmt(esc(T.legend), { x: "<b>" + esc(x.me) + "</b>", y: "<b>" + esc(y.me) + "</b>" }) + '</p>' + bars(vx, vy) + '</div></div></div>';
      h += '<div class="step"><h3>' + esc(T.talk_title) + '</h3><p class="muted">' + esc(T.talk_text) + '</p>' +
        big.map(function (g) { return '<div class="gap hot"><div><b>' + esc(BY[g.k].name) + '</b> · ' + esc(g.who) + '<br><span class="small">' + esc(g.lbl) + ': ' + fmt(esc(T.vs), { a: g.a, b: g.b }) + '</span></div><b class="n">' + g.d + '</b></div>'; }).join("") + "</div>";
      var fp = [];
      if (lib.x <= 4 && pos.y >= 6) fp.push(fmt(T.lp_owner, { x: x.me, y: y.me, l: lib.x, p: pos.y }));
      if (lib.y <= 4 && pos.x >= 6) fp.push(fmt(T.lp_owner, { x: y.me, y: x.me, l: lib.y, p: pos.x }));
      if (lib.x <= 4 && pos.y <= 3) fp.push(fmt(T.lp_self, { x: x.me, y: y.me }));
      if (lib.y <= 4 && pos.x <= 3) fp.push(fmt(T.lp_self, { x: y.me, y: x.me }));
      var cd = ORDER.filter(function (k) { var A = x.a[k] || [0, 0, 0, 0], B = y.a[k] || [0, 0, 0, 0]; return Math.abs(A[2] - A[3]) >= 4 || Math.abs(B[2] - B[3]) >= 4; });
      if (cd.length) fp.push(fmt(T.cd_text, { list: names(cd) }));
      if (fp.length) h += '<div class="step"><h3>' + esc(T.lp_title) + '</h3>' + lis(fp) + '</div>';
      if (x.t && y.t) {
        var common = [];
        D.tastes.forEach(function (c) { var a = x.t[c[0]] || [], b = y.t[c[0]] || []; a.forEach(function (i) { if (b.indexOf(i) >= 0 && c[2][i]) common.push(c[2][i]); }); });
        h += '<div class="step"><h3>' + esc(T.tastes_common) + '</h3><p>' + (common.length ? esc(common.join(", ")) : esc(T.tastes_none)) + '</p></div>';
      }
      if (x.l && y.l && D.loveLangs) {
        var LL = D.loveLangs.map(function (q) { return q[1]; }), pick = function (ix) { return (ix || []).map(function (i) { return LL[i]; }).filter(Boolean); };
        var m1 = pick(x.l.give).filter(function (n) { return pick(y.l.receive).indexOf(n) >= 0; }), m2 = pick(y.l.give).filter(function (n) { return pick(x.l.receive).indexOf(n) >= 0; });
        h += '<div class="step"><h3>' + esc(T.c_langs_title) + '</h3><p>' + fmt(esc(T.c_langs_line), { x: esc(x.me), y: esc(y.me), give: esc(pick(x.l.give).join(", ") || "–"), receive: esc(pick(y.l.receive).join(", ") || "–") }) + ' ' + (m1.length ? fmt(esc(T.c_langs_match), { list: esc(m1.join(", ")) }) : esc(T.c_langs_none)) + '</p>' +
          '<p>' + fmt(esc(T.c_langs_line), { x: esc(y.me), y: esc(x.me), give: esc(pick(y.l.give).join(", ") || "–"), receive: esc(pick(x.l.receive).join(", ") || "–") }) + ' ' + (m2.length ? fmt(esc(T.c_langs_match), { list: esc(m2.join(", ")) }) : esc(T.c_langs_none)) + '</p></div>';
      }
      if (x.x && y.x && x.x.status != null && y.x.status != null) {
        var sx = D.sliders.filter(function (q) { return q.key === "status"; })[0], vx1 = x.x.status, vy1 = y.x.status;
        var line = fmt(esc(T.c_status_line), { x: esc(x.me), y: esc(y.me), v: esc(sx.pos[vx1]), w: esc(sx.pos[vy1]) });
        var note = (vx1 >= 3 && vy1 >= 3) ? T.c_status_both : ((vx1 >= 3 || vy1 >= 3) && Math.abs(vx1 - vy1) >= 2 ? T.c_status_gap : "");
        h += '<div class="step"><h3>' + esc(T.c_status_title) + '</h3><p>' + line + (note ? " " + esc(note) : "") + '</p></div>';
      }
      h += '<div class="step"><h3>' + esc(T.all_gaps) + '</h3><div class="tbl"><table><tr><th>' + esc(T.th_prop) + '</th><th>' + esc(T.th_gap) + '</th><th>' + esc(T.th_values) + '</th><th></th></tr>' + rows.filter(function (g) { return g.d >= 3; }).map(function (g) { return "<tr><td>" + esc(BY[g.k].name) + "</td><td>" + esc(g.who) + "</td><td>" + g.a + " × " + g.b + "</td><td><b>" + g.d + "</b></td></tr>"; }).join("") + '</table></div><p class="muted">' + esc(T.gaps_note) + '</p><div class="actions">' + shareBtn() + '</div></div>';
      return h;
    }
    function wireShare(x, y) {
      setTimeout(function () {
        var s = root.querySelector("[data-share]"); if (!s) return;
        s.addEventListener("click", function () {
          var r = gapsOf(x, y);
          shareDialog({ file: "couple-test", kicker: T.c_kicker, title: fmt(T.c_share_title, { x: x.me, y: y.me }), values: r.vx, values2: r.vy,
            lines: r.big.map(function (g) { return BY[g.k].name + " (" + g.who + "): " + fmt(T.vs, { a: g.a, b: g.b }) + "."; }) });
        });
      }, 0);
    }
    render();
  }

  /* ---------- Self Discover ---------- */
  function selfDiscover(root) {
    var saved = store.get("selfdiscover") || { values: {}, vari: {}, tastes: {}, extras: {}, langs: {} };
    saved.langs = saved.langs || {};
    var sl = D.sliders, variLabel = function (v) { return T.vari_labels[v]; };
    var card = function (s) {
      var v = saved.values[s.key] != null ? saved.values[s.key] : (s.presumed != null ? s.presumed : 2), va = saved.vari[s.key] || 0;
      return '<div class="slider-card" data-slug="' + s.key + '"><h4>' + esc(s.name) + '</h4><p class="small muted">' + esc(s.measures) + '</p>' +
        '<div class="poles"><span>' + esc(s.poles[0]) + '</span><span>' + esc(s.poles[1]) + '</span></div>' +
        '<div class="track">' + (s.presumed != null ? '<span class="presumed" style="left:calc(' + (s.presumed * 25) + '% + ' + (8 - s.presumed * 4) + 'px)"></span>' : "") + '<span class="band"></span>' +
        '<input type="range" min="0" max="4" step="1" name="v-' + s.key + '" value="' + v + '"></div>' +
        '<div class="pos-label" data-pos>' + esc(s.pos[v]) + '</div><p class="small" data-pos-text>' + esc(s.pos_text[v]) + '</p>' +
        '<div class="vari"><span>' + esc(T.variability) + '</span><input type="range" min="0" max="5" step="1" name="x-' + s.key + '" value="' + va + '"><span data-vari>' + esc(variLabel(va)) + '</span></div>' +
        (s.extra ? '<label class="opt" style="margin-top:10px"><input type="checkbox" name="e-' + s.key + '" value="' + esc(s.extra[0]) + '"' + (saved.extras && saved.extras[s.key] ? " checked" : "") + '> ' + esc(s.extra[1]) + '</label>' : "") +
        '<details><summary>' + esc(T.sheet) + '</summary><dl class="sheet"><dt>' + esc(T.sheet_why0) + '</dt><dd>' + esc(s.why0) + '</dd><dt>' + esc(T.sheet_not) + '</dt><dd>' + esc(s.not_) + '</dd><dt>' + esc(T.sheet_links) + '</dt><dd>' + esc(s.links) + '</dd><dt>' + esc(T.sheet_pos) + '</dt><dd>' + s.pos.map(function (p, i) { return "<b>" + esc(p) + "</b>: " + esc(s.pos_text[i]); }).join("<br>") + '</dd></dl></details></div>';
    };
    var chips = function (attr, key, list, on) { return '<div class="chips" data-' + attr + '="' + key + '">' + list.map(function (t, i) { return '<button type="button" class="chip' + (on.indexOf(i) >= 0 ? " on" : "") + '" data-i="' + i + '">' + esc(t) + '</button>'; }).join("") + '</div>'; };
    var h = '<form class="step"><h2>' + esc(T.sd_title) + '</h2><p class="muted">' + esc(T.sd_text1) + '</p><p class="muted">' + esc(T.sd_text2) + '</p>';
    D.sliderGroups.forEach(function (g) {
      var list = sl.filter(function (s) { return s.group === g[0] && !s.more; });
      if (!list.length) return;
      h += '<h3 style="margin-top:28px">' + esc(g[1]) + '</h3>' + list.map(card).join("");
    });
    var more = sl.filter(function (s) { return s.more; });
    if (more.length) h += '<details class="more" style="margin-top:28px"' + (more.some(function (s) { return saved.values[s.key] != null; }) ? " open" : "") + '><summary>' + esc(T.more_sliders) + '</summary><p class="muted">' + esc(T.more_text) + '</p>' + more.map(card).join("") + '</details>';
    var LL = D.loveLangs.map(function (l) { return l[1]; });
    h += '<h3 style="margin-top:28px">' + esc(T.langs_title) + '</h3><p class="muted">' + esc(T.langs_text) + '</p>' +
      '<div class="slider-card"><h4>' + esc(T.langs_give) + '</h4>' + chips("lang", "give", LL, saved.langs.give || []) + '<h4 style="margin-top:14px">' + esc(T.langs_receive) + '</h4>' + chips("lang", "receive", LL, saved.langs.receive || []) + '</div>';
    h += '<h3 style="margin-top:28px">' + esc(T.tastes_title) + '</h3><p class="muted">' + esc(T.tastes_text) + '</p>';
    D.tastes.forEach(function (c) { h += '<div class="slider-card"><h4>' + esc(c[1]) + '</h4>' + chips("taste", c[0], c[2], saved.tastes[c[0]] || []) + '</div>'; });
    h += '<div class="actions"><button class="btn" type="submit">' + esc(T.sd_save) + '</button></div></form><div id="selfmap"></div>';
    root.innerHTML = h;
    function paint(c) {
      var s = sl.filter(function (x) { return x.key === c.getAttribute("data-slug"); })[0];
      var v = +c.querySelector('[name^="v-"]').value, va = +c.querySelector('[name^="x-"]').value;
      c.querySelector("[data-pos]").textContent = s.pos[v]; c.querySelector("[data-pos-text]").textContent = s.pos_text[v]; c.querySelector("[data-vari]").textContent = variLabel(va);
      var band = c.querySelector(".band"), half = va * 10, left = Math.max(0, v * 25 - half), right = Math.min(100, v * 25 + half);
      band.style.left = left + "%"; band.style.width = (va ? right - left : 0) + "%";
    }
    root.querySelectorAll(".slider-card[data-slug]").forEach(function (c) { paint(c); c.addEventListener("input", function () { paint(c); }); });
    root.querySelectorAll(".chip").forEach(function (b) { b.addEventListener("click", function () { b.classList.toggle("on"); }); });
    var onIdx = function (sel) { return Array.prototype.map.call(root.querySelectorAll(sel + " .chip.on"), function (b) { return +b.getAttribute("data-i"); }); };
    root.querySelector("form").addEventListener("submit", function (e) {
      e.preventDefault(); var f = e.target, values = {}, vari = {}, tastes = {}, extras = {};
      sl.forEach(function (s) { values[s.key] = readRange(f, "v-" + s.key); vari[s.key] = readRange(f, "x-" + s.key); var ex = s.extra && f.querySelector('[name="e-' + s.key + '"]'); if (ex && ex.checked) extras[s.key] = s.extra[0]; });
      D.tastes.forEach(function (c) { tastes[c[0]] = onIdx('[data-taste="' + c[0] + '"]'); });
      saved = { date: new Date().toISOString(), values: values, vari: vari, tastes: tastes, extras: extras, langs: { give: onIdx('[data-lang="give"]'), receive: onIdx('[data-lang="receive"]') } };
      store.set("selfdiscover", saved); showMap();
    });
    function posLabel(s) { var x = saved.values[s.key], ex = saved.extras && saved.extras[s.key]; return s.pos[x] + (ex ? " · " + ex : ""); }
    function showMap() {
      var v = saved.values, va = saved.vari, out = '<div class="step result"><p class="eyebrow">' + esc(T.map_kicker) + ' · ' + esc(fmtDate(saved.date)) + '</p><h2>' + esc(T.map_title) + '</h2>';
      var row = function (s) {
        var x = v[s.key], w = va[s.key] || 0, left = Math.max(0, x * 25 - w * 10), width = w ? Math.min(100, x * 25 + w * 10) - left : 0;
        return '<div class="map-row"><div><b>' + esc(s.name) + '</b><br><span class="muted">' + esc(posLabel(s)) + (w ? ", " + esc(variLabel(w)) : "") + '</span></div><div><div class="poles"><span>' + esc(s.poles[0]) + '</span><span>' + esc(s.poles[1]) + '</span></div><div class="t">' + (s.presumed != null ? '<s style="left:calc(' + (s.presumed * 25) + '% - 1px)"></s>' : "") + (width ? '<b style="left:' + left + '%;width:' + width + '%;opacity:.45"></b>' : "") + '<b style="left:calc(' + (x * 25) + '% - 7px);width:14px"></b></div></div></div>';
      };
      out += sl.filter(function (s) { return !s.more && v[s.key] != null; }).map(row).join("");
      var moreDone = sl.filter(function (s) { return s.more && v[s.key] != null; });
      if (moreDone.length) out += '<h4 style="margin-top:18px">' + esc(T.more_sliders) + '</h4>' + moreDone.map(row).join("");
      var far = sl.filter(function (s) { return s.presumed != null && v[s.key] != null && Math.abs(v[s.key] - s.presumed) >= 2; }), variable = sl.filter(function (s) { return (va[s.key] || 0) >= 3; });
      var nm = function (xs) { return xs.map(function (s) { return s.name; }).join(", "); };
      out += '<div class="spacer"></div>' + (far.length ? '<p>' + fmt(esc(T.sd_far), { list: "<b>" + esc(nm(far)) + "</b>" }) + '</p>' : '<p>' + esc(T.sd_near) + '</p>');
      if (variable.length) out += '<p>' + fmt(esc(T.sd_variable), { list: "<b>" + esc(nm(variable)) + "</b>" }) + '</p>';
      var lg = saved.langs || {}, LL = D.loveLangs.map(function (l) { return l[1]; }), pick = function (ix) { return (ix || []).map(function (i) { return LL[i]; }).join(", "); };
      if ((lg.give || []).length || (lg.receive || []).length) out += '<p class="small">' + esc(T.langs_give) + ': ' + esc(pick(lg.give) || "–") + ' · ' + esc(T.langs_receive) + ': ' + esc(pick(lg.receive) || "–") + '</p>';
      if (store.get("portraits", []).length >= 3) out += '<p class="muted">' + fmt(esc(T.sd_const_link), { link: '<a href="' + P.portraits + '">' + esc(T.my_portraits) + '</a>' }) + '</p>';
      out += '<p class="muted">' + esc(T.sd_local) + '</p><div class="actions">' + shareBtn(T.sd_share_btn) + '</div></div>';
      $("#selfmap").innerHTML = out; $("#selfmap").scrollIntoView({ behavior: "smooth" });
      $("#selfmap [data-share]").addEventListener("click", function () {
        var rows = sl.filter(function (s) { return !s.more; }).map(function (s) { return { name: s.name, pos: posLabel(s), x: v[s.key], presumed: s.presumed, poles: s.poles }; });
        shareDialog({ file: "self-discover", kicker: T.selfdiscover_name, title: T.map_title, shortTitle: T.map_short, rows: rows,
          lines: [far.length ? fmt(T.sd_far_short, { list: nm(far.slice(0, 4)) }) : T.sd_near_short, T.sd_legend] });
      });
    }
    if (saved.date) showMap();
  }

  /* ---------- Ficar ou ir? ---------- */
  function stay(root) {
    var S = D.stay, st = { step: 0, nome: "", rel: "parceiro", red: {}, pros: {}, cons: {}, reasons: [], w: {}, more: false };
    var qOf = function (it) { return (st.rel !== "parceiro" && it.q_amigo) ? it.q_amigo : it.q; };
    var prosList = function () { return st.more ? S.pros.concat(S.pros_more || []) : S.pros; };
    var consList = function () { return st.more ? S.cons.concat(S.cons_more || []) : S.cons; };
    var items = function (list, bag) { return list.map(function (it) { return '<div class="item"><p class="q">' + esc(qOf(it)) + '</p>' + rangeInput("v-" + it.id, bag[it.id] != null ? bag[it.id] : 5) + '</div>'; }).join(""); };
    function render() {
      var h = "";
      if (st.step === 0) {
        h = '<form class="step"><h2>' + esc(T.st_who) + '</h2><p class="muted">' + esc(T.nick_note) + '</p>' +
          '<div class="field"><label>' + esc(T.name) + '</label><input type="text" name="nome" required value="' + esc(st.nome) + '"></div>' +
          '<div class="field"><label>' + esc(T.relation) + '</label><select name="rel">' + S.relations.map(function (r) { return '<option value="' + r[0] + '"' + (r[0] === st.rel ? " selected" : "") + '>' + esc(r[1]) + '</option>'; }).join("") + '</select></div>' +
          '<div class="note"><ol>' + T.st_steps.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + '</ol></div>' +
          '<div class="actions"><button class="btn" type="submit">' + esc(T.start) + '</button></div></form>';
      } else if (st.step === 1) {
        h = '<form class="step"><p class="eyebrow">' + fmt(T.step_of, { i: 1, n: 4 }) + '</p><h2>' + esc(T.st_red_title) + '</h2><p class="muted">' + esc(T.st_red_text) + '</p>' +
          S.redlines.map(function (r) { return '<div class="item"><p class="q">' + esc(r.label) + ' <span class="muted">· ' + esc(r.q) + '</span></p><div class="opts">' + S.levels.map(function (l, i) { return '<label class="opt"><input type="radio" name="r-' + r.id + '" value="' + i + '"' + ((st.red[r.id] || 0) === i ? " checked" : "") + '> ' + esc(l) + '</label>'; }).join("") + '</div></div>'; }).join("") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(T.continue_) + '</button></div></form>';
      } else if (st.step === 2 || st.step === 3) {
        var base = st.step === 2 ? S.pros : S.cons, extra = st.step === 2 ? (S.pros_more || []) : (S.cons_more || []), bag = st.step === 2 ? st.pros : st.cons;
        h = '<form class="step"><p class="eyebrow">' + fmt(T.step_of, { i: st.step, n: 4 }) + '</p><h2>' + esc(st.step === 2 ? T.st_pros : T.st_cons) + '</h2><p class="muted">' + fmt(esc(T.st_hint), { nome: esc(st.nome) }) + '</p>' + items(base, bag) +
          (extra.length ? '<details class="more" style="margin-top:18px"' + (st.more ? " open" : "") + '><summary>' + esc(T.st_more) + '</summary><p class="muted">' + esc(T.st_more_text) + '</p><label class="opt"><input type="checkbox" name="more"' + (st.more ? " checked" : "") + '> ' + esc(T.st_more) + '</label>' + items(extra, bag) + '</details>' : "") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(T.continue_) + '</button></div></form>';
      } else if (st.step === 4) {
        h = '<form class="step"><p class="eyebrow">' + fmt(T.step_of, { i: 4, n: 4 }) + '</p><h2>' + esc(T.st_why) + '</h2><p class="muted">' + esc(T.st_why_text) + '</p><div class="opts">' +
          S.reasons.map(function (r) { return '<label class="opt"><input type="checkbox" name="reason" value="' + r.id + '"' + (st.reasons.indexOf(r.id) >= 0 ? " checked" : "") + '> ' + esc(r.label) + '</label>'; }).join("") +
          '</div><div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(T.st_see) + '</button></div></form>';
      } else h = result();
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f && st.step < 5) {
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          if (st.step === 0) { st.nome = f.nome.value.trim() || T.default_person; st.rel = f.rel.value; }
          else if (st.step === 1) S.redlines.forEach(function (r) { st.red[r.id] = +(readRadio(f, "r-" + r.id) || 0); });
          else if (st.step === 2 || st.step === 3) {
            var mc = f.querySelector("[name=more]"); if (mc) st.more = st.more || mc.checked;
            var list = st.step === 2 ? S.pros.concat(S.pros_more || []) : S.cons.concat(S.cons_more || []), bag = st.step === 2 ? st.pros : st.cons;
            list.forEach(function (it) { if (f.querySelector('[name="v-' + it.id + '"]')) bag[it.id] = readRange(f, "v-" + it.id); });
          }
          else if (st.step === 4) st.reasons = Array.prototype.map.call(f.querySelectorAll("[name=reason]:checked"), function (c) { return c.value; });
          st.step++; render();
        });
        var b = f.querySelector("[data-back]"); if (b) b.addEventListener("click", function () { st.step--; render(); });
        var mc = f.querySelector("[name=more]"); if (mc) mc.addEventListener("change", function () { st.more = mc.checked; });
      }
      if (st.step === 5) wireResult();
      window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
    }
    function calc() {
      var side = function (list, bag) { var num = 0, den = 0; list.forEach(function (it) { var w = st.w[it.id] || 2; num += (bag[it.id] || 0) * w; den += 10 * w; }); return den ? Math.round(num / den * 100) : 0; };
      var top = function (list, bag) { return list.slice().sort(function (a, b) { return (bag[b.id] || 0) * (st.w[b.id] || 2) - (bag[a.id] || 0) * (st.w[a.id] || 2); }).filter(function (it) { return (bag[it.id] || 0) >= 5; }).slice(0, 2).map(function (it) { return qOf(it).replace(/\.$/, "").toLowerCase(); }); };
      var kinds = { amor: [], prisao: [], responsabilidade: [] };
      st.reasons.forEach(function (id) { var r = S.reasons.filter(function (x) { return x.id === id; })[0]; if (r) kinds[r.kind].push(r.label.toLowerCase()); });
      return { pros: side(prosList(), st.pros), cons: side(consList(), st.cons), topPros: top(prosList(), st.pros), topCons: top(consList(), st.cons), kinds: kinds };
    }
    function reading(c) {
      var R = S.readings, fillR = function (t) { return fmt(t, { cons: c.topCons.join(T.and_) || T.st_cons_fallback, reasons: c.kinds.prisao.join(", ") || c.kinds.amor.join(", ") || T.none_f }); };
      var prison = c.kinds.prisao.length > c.kinds.amor.length, out = [];
      if (!st.reasons.length) out.push(R.none);
      if (Math.abs(c.pros - c.cons) < 8) out.push(fillR(R.even));
      else if (c.pros > c.cons) out.push(fillR(prison ? R.pros_prisao : (c.topCons.length ? R.pros_amor : R.pros_amor_clean)));
      else out.push(fillR(prison ? R.cons_prisao : R.cons_amor));
      if (c.kinds.responsabilidade.length) out.push(R.responsibility);
      return out;
    }
    function result() {
      var hits = S.redlines.map(function (r) { return { r: r, lvl: st.red[r.id] || 0 }; }).filter(function (x) { return x.lvl > 0; });
      var reds = hits.filter(function (x) { return x.lvl >= x.r.red; }), graves = hits.filter(function (x) { return x.r.grave != null && x.lvl >= x.r.grave && x.lvl < x.r.red; });
      var help = reds.some(function (x) { return x.r.help; });
      var h = '<div class="step result"><p class="eyebrow">' + esc(S.kicker) + ' · ' + esc(st.nome) + ' · ' + esc(fmtDate(new Date().toISOString())) + '</p><h2>' + esc(T.st_balance) + '</h2>';
      if (reds.length || graves.length) {
        h += '<div class="redbox"><h3>' + esc(T.st_red_title) + '</h3><p>' + esc(S.readings.red) + '</p><ul>' +
          reds.map(function (x) { return '<li><b>' + esc(x.r.label) + '</b> · ' + esc(S.levels[x.lvl].toLowerCase()) + '</li>'; }).join("") +
          graves.map(function (x) { return '<li><b>' + esc(x.r.label) + '</b> · ' + esc(S.levels[x.lvl].toLowerCase()) + '. ' + esc(S.grave_text) + '</li>'; }).join("") +
          '</ul><p>' + esc(S.red_text) + '</p>' + (help ? '<p class="help"><b>' + esc(S.help_text) + '</b></p>' : "") + '</div>';
      } else h += '<div class="note">' + esc(T.st_no_red) + ' ' + esc(S.red_text) + '</div>';
      h += '<div id="balance"></div></div>';
      h += '<div class="step"><h3>' + esc(T.st_adjust) + '</h3><p class="muted">' + esc(T.st_adjust_text) + '</p><div class="grid g2"><div><h4>' + esc(T.st_for) + '</h4>' + tableFor(prosList(), st.pros) + '</div><div><h4>' + esc(T.st_against) + '</h4>' + tableFor(consList(), st.cons) + '</div></div></div>';
      h += '<div class="step"><div id="reading"></div><p class="muted">' + esc(S.readings.footer) + '</p><div class="actions">' + shareBtn(T.st_share_btn) + '<a class="btn ghost" href="' + P.couple + '">' + esc(T.st_to_couple) + '</a><button class="btn ghost" type="button" data-again>' + esc(T.redo) + '</button></div><p class="muted">' + esc(T.st_img_note) + '</p></div>';
      return h;
    }
    function tableFor(list, bag) {
      return '<div class="tbl"><table class="balance"><tr><th>' + esc(T.th_item) + '</th><th>' + esc(T.th_score) + '</th><th>' + esc(T.th_weight) + '</th></tr>' + list.map(function (it) {
        return '<tr><td>' + esc(qOf(it)) + '</td><td><b>' + (bag[it.id] || 0) + '</b></td><td><select data-w="' + it.id + '">' + S.weights.map(function (w) { return '<option value="' + w[0] + '"' + ((st.w[it.id] || 2) === w[0] ? " selected" : "") + '>' + esc(w[1]) + '</option>'; }).join("") + '</select></td></tr>';
      }).join("") + '</table></div>';
    }
    function paint() {
      var c = calc(), kd = c.kinds, parts = [];
      if (kd.amor.length) parts.push(fmt(T.st_of_love, { list: kd.amor.join(", ") }));
      if (kd.prisao.length) parts.push(fmt(T.st_of_prison, { list: kd.prisao.join(", ") }));
      if (kd.responsabilidade.length) parts.push(fmt(T.st_of_resp, { list: kd.responsabilidade.join(", ") }));
      $("#balance", root).innerHTML = '<div class="scale"><div class="side"><span>' + esc(T.st_for) + '</span><i><b style="width:' + c.pros + '%"></b></i><strong>' + c.pros + '%</strong></div><div class="side"><span>' + esc(T.st_against) + '</span><i><b class="dark" style="width:' + c.cons + '%"></b></i><strong>' + c.cons + '%</strong></div></div>' +
        '<p class="small">' + (c.topPros.length ? esc(T.st_weighs_for + " " + c.topPros.join("; ")) + '. ' : "") + (c.topCons.length ? esc(T.st_weighs_against + " " + c.topCons.join("; ")) + '.' : "") + '</p>' +
        (st.reasons.length ? '<p class="small">' + esc(T.st_reasons_line + " " + parts.join("; ")) + '.</p>' : "");
      $("#reading", root).innerHTML = '<h3>' + esc(T.st_reading) + '</h3>' + reading(c).map(function (t) { return "<p>" + esc(t) + "</p>"; }).join("");
      store.set("stay", { nome: st.nome, rel: st.rel, date: new Date().toISOString(), pros: c.pros, cons: c.cons });
    }
    function wireResult() {
      paint();
      root.querySelectorAll("[data-w]").forEach(function (s) { s.addEventListener("change", function () { st.w[s.getAttribute("data-w")] = +s.value; paint(); }); });
      root.querySelector("[data-again]").addEventListener("click", function () { st = { step: 0, nome: "", rel: st.rel, red: {}, pros: {}, cons: {}, reasons: [], w: {}, more: false }; render(); });
      root.querySelector("[data-share]").addEventListener("click", function () {
        var c = calc();
        shareDialog({ file: "stay-or-go", kicker: S.kicker, title: fmt(T.st_share_title, { nome: st.nome }), bars: [{ label: T.st_for, pct: c.pros }, { label: T.st_against, pct: c.cons }],
          lines: [c.topPros.length ? T.st_weighs_for + " " + c.topPros.join("; ") + "." : T.st_few_for, c.topCons.length ? T.st_weighs_against + " " + c.topCons.join("; ") + "." : T.st_few_against, reading(c)[0]] });
      });
    }
    render();
  }

  /* ---------- Glossário: filtro ---------- */
  function glossary(root) {
    var input = root.querySelector("input"), rows = Array.prototype.slice.call(document.querySelectorAll(".gl-term")), groups = Array.prototype.slice.call(document.querySelectorAll(".gl-group")), none = document.querySelector(".gl-none");
    var norm = function (s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
    input.addEventListener("input", function () {
      var q = norm(input.value.trim()), shown = 0;
      rows.forEach(function (r) { var on = !q || norm(r.textContent).indexOf(q) >= 0; r.classList.toggle("hidden", !on); if (on) shown++; });
      groups.forEach(function (g) { g.classList.toggle("hidden", !g.querySelector(".gl-term:not(.hidden)")); });
      if (none) none.classList.toggle("hidden", shown > 0);
    });
  }

  /* ---------- Limites: o que conta como traição ---------- */
  var lb64 = {
    enc: function (o) { var raw = unescape(encodeURIComponent(JSON.stringify({ v: 1, me: o.me, you: o.you, s: o.ans.map(function (v) { return v < 0 ? "-" : String(v); }).join("") }))); return btoa(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); },
    dec: function (str) { try { str = str.replace(/-/g, "+").replace(/_/g, "/"); while (str.length % 4) str += "="; var o = JSON.parse(decodeURIComponent(escape(atob(str)))); if (!o || typeof o.s !== "string" || o.s.length !== 100) return null; return { me: o.me, you: o.you, ans: o.s.split("").map(function (c) { return c === "-" ? -1 : +c; }) }; } catch (e) { return null; } }
  };
  function limits(root) {
    var L = D.limits, hp = hashParams(), p1 = hp.l1 ? lb64.dec(hp.l1) : null, p2 = hp.l2 ? lb64.dec(hp.l2) : null;
    var G = L.groups, N = L.items.length, saved = store.get("limits");
    var st = { step: 0, me: "", you: "", ans: [] }; for (var i = 0; i < N; i++) st.ans.push(-1);
    if (p1 && !p2) { st.me = p1.you || ""; st.you = p1.me; }
    var gItems = function (gid) { var out = []; L.items.forEach(function (it, i) { if (it[0] === gid) out.push(i); }); return out; };
    var gAvg = function (ans, gid) { var xs = gItems(gid).map(function (i) { return ans[i]; }).filter(function (v) { return v >= 0; }); return xs.length ? mean(xs) : null; };
    var posOf = function (avg) { return T.lm_pos[Math.min(4, Math.max(0, Math.round(avg)))]; };
    function render() {
      var h = "";
      if (p1 && p2) { root.innerHTML = pair(p1, p2); wire(); return; }
      if (st.step === 0) {
        h = '<form class="step"><h2>' + (p1 ? fmt(esc(T.lm_p2_title), { me: esc(p1.me) }) : esc(T.lm_who)) + '</h2><p class="muted">' + (p1 ? fmt(esc(T.lm_p2_text), { me: esc(p1.me) }) : esc(T.lm_text)) + '</p>' +
          '<div class="field"><label>' + esc(T.name) + '</label><input type="text" name="me" required value="' + esc(st.me) + '"></div>' +
          (p1 ? "" : '<div class="field"><label>' + esc(T.lm_partner) + '</label><input type="text" name="you" value="' + esc(st.you) + '"></div>') +
          '<div class="note"><b>' + esc(T.lm_legend) + '</b><ul>' + L.options.map(function (o) { return "<li><b>" + esc(o[0]) + "</b> · " + esc(o[1]) + "</li>"; }).join("") + '</ul></div>' +
          '<div class="actions"><button class="btn" type="submit">' + esc(T.start) + '</button></div></form>';
      } else if (st.step <= G.length) {
        var g = G[st.step - 1], idx = gItems(g[0]);
        h = '<div class="progress"><i style="width:' + Math.round((st.step - 1) / G.length * 100) + '%"></i></div><form class="step"><p class="eyebrow">' + fmt(T.lm_group_of, { i: st.step, n: G.length }) + '</p><h2>' + esc(g[1]) + '</h2>' +
          idx.map(function (i) { return '<div class="item lm-item"><p class="q">' + esc(L.items[i][1]) + '</p><div class="opts">' + L.options.map(function (o, k) { return '<label class="opt"><input type="radio" name="q' + i + '" value="' + k + '"' + (st.ans[i] === k ? " checked" : "") + '> ' + esc(o[1]) + '</label>'; }).join("") + '</div></div>'; }).join("") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(st.step === G.length ? (p1 ? T.finish : T.lm_see) : T.next) + '</button></div></form>';
      } else h = p1 ? pair(p1, { me: st.me, you: st.you, ans: st.ans }, true) : solo();
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f && st.step <= G.length) {
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          if (st.step === 0) { st.me = f.me.value.trim() || T.default_person; if (f.you) st.you = f.you.value.trim(); }
          else gItems(G[st.step - 1][0]).forEach(function (i) { var v = readRadio(f, "q" + i); st.ans[i] = v == null ? -1 : +v; });
          st.step++; render();
        });
        var b = f.querySelector("[data-back]"); if (b) b.addEventListener("click", function () { st.step--; render(); });
      }
      if (st.step > G.length) wire();
      window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
    }
    function summary(ans) {
      var rows = G.map(function (g) { return { g: g, avg: gAvg(ans, g[0]) }; }).filter(function (r) { return r.avg != null; });
      var byAvg = rows.slice().sort(function (a, b) { return b.avg - a.avg; });
      var answered = ans.filter(function (v) { return v >= 0; }).length;
      var dc = [], tg = []; ans.forEach(function (v, i) { if (v === 2) dc.push(i); if (v === 4) tg.push(i); });
      return { rows: rows, strict: byAvg.slice(0, 3), lenient: byAvg.slice(-3).reverse(), answered: answered, dc: dc, tg: tg };
    }
    function groupBars(rows, scale) {
      return '<div class="bars">' + rows.map(function (r) { return '<div class="bar"><span>' + esc(r.g[1]) + '</span><i><b style="width:' + Math.round(r.avg / scale * 100) + '%"></b></i><span class="v">' + (scale === 4 ? esc(posOf(r.avg)) : Math.round(r.avg) + "%") + '</span></div>'; }).join("") + '</div>';
    }
    function solo() {
      var s = summary(st.ans), code = lb64.enc({ me: st.me, you: st.you, ans: st.ans }), url = location.href.split("#")[0] + "#l1=" + code;
      saved = { date: new Date().toISOString(), me: st.me, ans: st.ans }; store.set("limits", saved);
      var h = '<div class="step result"><p class="eyebrow">' + esc(T.lm_kicker) + ' · ' + esc(st.me) + ' · ' + esc(fmtDate(saved.date)) + '</p><h2>' + esc(T.lm_title) + '</h2><p class="muted">' + fmt(esc(T.lm_answered), { n: s.answered }) + '</p>' + groupBars(s.rows, 4) +
        '<div class="spacer"></div><p>' + fmt(esc(T.lm_strict), { list: "<b>" + esc(s.strict.map(function (r) { return r.g[1]; }).join(", ")) + "</b>" }) + ' ' + fmt(esc(T.lm_lenient), { list: "<b>" + esc(s.lenient.map(function (r) { return r.g[1]; }).join(", ")) + "</b>" }) + '</p>' +
        '<p>' + esc(s.dc.length ? fmt(T.lm_context, { n: s.dc.length }) : T.lm_context_none) + '</p>' + (s.dc.length ? lis(s.dc.slice(0, 12).map(function (i) { return L.items[i][1]; })) : "") +
        (s.tg.length ? '<p>' + fmt(esc(T.lm_grave), { n: s.tg.length, list: esc(s.tg.slice(0, 5).map(function (i) { return L.items[i][1].replace(/\.$/, "").toLowerCase(); }).join("; ")) }) + '</p>' : "") + '</div>';
      h += '<div class="step"><h3>' + esc(T.lm_link_title) + '</h3><p>' + esc(T.lm_unspoken) + '</p><p class="muted">' + esc(T.lm_link_text) + '</p><p class="code" id="lm-url">' + esc(url) + '</p><div class="actions"><button class="btn" type="button" data-copy>' + esc(T.lm_copy) + '</button>' + shareBtn(T.lm_share_btn) + '<button class="btn ghost" type="button" data-again>' + esc(T.lm_redo) + '</button></div><p class="muted">' + esc(T.lm_warn) + '</p></div>';
      return h;
    }
    function pair(x, y, withLink) {
      var both = [], agree = 0, div = [], dcBoth = 0, dcOne = 0;
      L.items.forEach(function (it, i) {
        var a = x.ans[i], b = y.ans[i]; if (a < 0 || b < 0) return;
        both.push(i); if (Math.abs(a - b) <= 1) agree++;
        if (Math.abs(a - b) >= 2) div.push({ i: i, a: a, b: b, d: Math.abs(a - b), gi: G.map(function (g) { return g[0]; }).indexOf(it[0]) });
        if (a === 2 && b === 2) dcBoth++; else if (a === 2 || b === 2) dcOne++;
      });
      div.sort(function (p, q) { return q.gi - p.gi || q.d - p.d; });
      var pct = both.length ? Math.round(agree / both.length * 100) : 0;
      var rows = G.map(function (g) { var idx = gItems(g[0]).filter(function (i) { return x.ans[i] >= 0 && y.ans[i] >= 0; }); var ok = idx.filter(function (i) { return Math.abs(x.ans[i] - y.ans[i]) <= 1; }).length; return { g: g, avg: idx.length ? ok / idx.length * 100 : null }; }).filter(function (r) { return r.avg != null; });
      var h = '<div class="step result"><p class="eyebrow">' + fmt(esc(T.lm_pair_kicker), { x: esc(x.me), y: esc(y.me) }) + '</p><h2>' + esc(T.lm_pair_title) + '</h2><p>' + fmt(esc(T.lm_agree), { p: pct }) + '</p><h4>' + esc(T.lm_group_agree) + '</h4>' + groupBars(rows, 100) + '</div>';
      h += '<div class="step"><h3>' + esc(T.lm_diverge_title) + '</h3><p class="muted">' + esc(T.lm_diverge_text) + '</p>' +
        (div.length ? '<div class="tbl"><table><tr><th>' + esc(T.lm_th[0]) + '</th><th>' + esc(x.me) + '</th><th>' + esc(y.me) + '</th></tr>' + div.map(function (r) { return '<tr><td>' + esc(L.items[r.i][1]) + ' <span class="muted">· ' + esc(G[r.gi][1]) + '</span></td><td>' + esc(L.options[r.a][1]) + '</td><td>' + esc(L.options[r.b][1]) + '</td></tr>'; }).join("") + '</table></div>' : '<div class="note">' + esc(T.lm_none_diverge) + '</div>') +
        '<p>' + (dcBoth ? fmt(esc(T.lm_both_context), { n: dcBoth }) + " " : "") + (dcOne ? fmt(esc(T.lm_one_context), { n: dcOne }) : "") + '</p></div>';
      if (withLink) {
        var url = location.href.split("#")[0] + "#l1=" + hp.l1 + "&l2=" + lb64.enc(y);
        h += '<div class="step"><h3>' + esc(T.c_done_p2) + '</h3><p class="code" id="lm-url">' + esc(url) + '</p><div class="actions"><button class="btn" type="button" data-copy>' + esc(T.lm_copy) + '</button>' + shareBtn(T.lm_share_btn) + '</div><p class="muted">' + esc(T.lm_warn) + '</p></div>';
      } else h += '<div class="step"><div class="actions">' + shareBtn(T.lm_share_btn) + '</div></div>';
      pairCache = { x: x, y: y, rows: rows, pct: pct };
      return h;
    }
    var pairCache = null;
    function wire() {
      var c = root.querySelector("[data-copy]"), u = root.querySelector("#lm-url"); if (c && u) c.addEventListener("click", function () { navigator.clipboard && navigator.clipboard.writeText(u.textContent); c.textContent = T.copied; });
      var a = root.querySelector("[data-again]"); if (a) a.addEventListener("click", function () { st = { step: 0, me: st.me, you: st.you, ans: st.ans.map(function () { return -1; }) }; render(); });
      var s = root.querySelector("[data-share]"); if (!s) return;
      s.addEventListener("click", function () {
        if (pairCache && (p2 || p1)) {
          shareDialog({ file: "limits", kicker: T.lm_kicker, title: fmt(T.lm_share_pair, { x: pairCache.x.me, y: pairCache.y.me }), shortTitle: fmt(T.lm_share_pair, { x: pairCache.x.me, y: pairCache.y.me }),
            rows: pairCache.rows.map(function (r) { return { name: r.g[1], pos: Math.round(r.avg) + "%", x: r.avg / 25, presumed: null, poles: ["0%", "100%"] }; }), lines: [fmt(T.lm_agree, { p: pairCache.pct })] });
        } else {
          var sm = summary(st.ans);
          shareDialog({ file: "limits", kicker: T.lm_kicker, title: T.lm_share_solo, shortTitle: T.lm_share_solo,
            rows: sm.rows.map(function (r) { return { name: r.g[1], pos: posOf(r.avg), x: r.avg, presumed: null, poles: T.lm_poles }; }), lines: [fmt(T.lm_strict, { list: sm.strict.map(function (r) { return r.g[1]; }).join(", ") })] });
        }
      });
    }
    render();
  }

  /* ---------- Listas: Manter a Chama, Bucket List do Amor, Bucket List Sexual ----------
     Respostas por item: 0 não, 1 talvez, 2 quero, 3 já faço / já vivi; -1 sem resposta.
     No cruzamento, qualquer item com um "não" fica de fora e nunca é mostrado. */
  function lists(root, key) {
    var L = D.lists[key], X = L.t, hp = hashParams(), flat = [], G = [];
    L.sections.forEach(function (s, si) { s.groups.forEach(function (g) { var idx = g.items.map(function (t) { flat.push(t); return flat.length - 1; }); G.push({ si: si, g: g, idx: idx }); }); });
    var N = flat.length, NS = L.sections.length, base = location.href.split("#")[0];
    var secOf = []; G.forEach(function (x) { x.idx.forEach(function (i) { secOf[i] = x.si; }); });
    var codec = {
      enc: function (o) {
        var s = o.ans.map(function (v, i) { return v < 0 || !o.parts[secOf[i]] ? "-" : String(v); }).join("");
        var raw = unescape(encodeURIComponent(JSON.stringify({ v: L.v, me: o.me, you: o.you || "", p: o.parts.map(function (b) { return b ? 1 : 0; }).join(""), s: s })));
        return btoa(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      },
      dec: function (str) {
        try {
          str = str.replace(/-/g, "+").replace(/_/g, "/"); while (str.length % 4) str += "=";
          var o = JSON.parse(decodeURIComponent(escape(atob(str))));
          if (!o || o.v !== L.v || typeof o.s !== "string" || o.s.length !== N || typeof o.p !== "string" || o.p.length !== NS) return null;
          return { me: String(o.me || T.default_person).slice(0, 40), you: String(o.you || "").slice(0, 40), parts: o.p.split("").map(function (c) { return c === "1"; }),
            ans: o.s.split("").map(function (c) { return c === "-" ? -1 : Math.min(3, Math.max(0, +c || 0)); }) };
        } catch (e) { return null; }
      }
    };
    var p1 = hp.l1 ? codec.dec(hp.l1) : null, p2 = p1 && hp.l2 ? codec.dec(hp.l2) : null;
    var saved = store.get(key); if (saved && (saved.v !== L.v || !saved.ans || saved.ans.length !== N || !saved.parts || saved.parts.length !== NS)) saved = null;
    var blank = function () { var a = []; for (var i = 0; i < N; i++) a.push(-1); return a; };
    var st = { step: 0, me: saved ? saved.me : "", you: saved ? saved.you || "" : "", ans: saved ? saved.ans.slice() : blank(), parts: saved ? saved.parts.slice() : L.sections.map(function (s) { return !!s["default"]; }), dirty: false };
    if (p1 && !p2) { st.parts = p1.parts.slice(); if (!st.me) st.me = p1.you || ""; st.you = p1.me; }
    var first = true, pickPool = [], pairCache = null;
    var active = function (parts) { return G.filter(function (x) { return parts[x.si]; }); };
    var needAdult = function (parts) { return L.sections.some(function (s, i) { return parts[i] && s.adult; }); };
    var save = function () { saved = { v: L.v, date: new Date().toISOString(), me: st.me, you: st.you, ans: st.ans, parts: st.parts }; store.set(key, saved); st.dirty = false; };
    var adultTag = function (s) { return s.adult ? ' <span class="tag adult">' + esc(T.bl_adult_tag) + '</span>' : ""; };

    function render() {
      var h = "", ag = active(st.parts);
      if (p1 && p2) { root.innerHTML = pair(p1, p2, false); wire(); return; }
      if (st.step === 0) {
        h = '<form class="step">' + (saved && !p1 ? '<div class="note"><p>' + fmt(esc(T.bl_saved), { date: esc(fmtDate(saved.date)) }) + '</p><div class="actions"><button class="btn ghost" type="button" data-view>' + esc(T.bl_view) + '</button></div></div>' : "") +
          '<h2>' + (p1 ? fmt(esc(T.bl_p2_title), { me: esc(p1.me) }) : esc(T.bl_who)) + '</h2>' + (p1 ? '<p class="muted">' + fmt(esc(T.bl_p2_text), { me: esc(p1.me) }) + '</p>' : "") +
          '<div class="field"><label>' + esc(T.name) + '</label><input type="text" name="me" required value="' + esc(st.me) + '"></div>' +
          (p1 ? "" : '<div class="field"><label>' + esc(T.bl_partner) + '</label><input type="text" name="you" value="' + esc(st.you) + '"></div>');
        if (NS > 1 || L.adult) {
          h += '<h3>' + (p1 ? fmt(esc(T.bl_p2_parts), { me: esc(p1.me) }) : esc(T.bl_parts)) + '</h3><div class="bl-parts">' + L.sections.map(function (s, i) {
            if (p1 && !st.parts[i]) return "";
            var n = s.groups.reduce(function (a, g) { return a + g.items.length; }, 0);
            return '<div class="bl-part"><label class="opt"><input type="checkbox" name="part" value="' + i + '"' + (st.parts[i] ? " checked" : "") + (p1 || NS === 1 ? " disabled" : "") + '> ' + esc(s.title) + ' <span class="muted">· ' + fmt(esc(T.bl_count), { n: n }) + '</span>' + adultTag(s) + '</label><p class="small muted">' + esc(s.lead) + '</p></div>';
          }).join("") + '</div>';
        }
        h += '<div class="note"><ul>' + L.notes.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + '</ul></div>' +
          '<div class="note"><b>' + esc(T.bl_legend) + '</b><ul>' + L.options.map(function (o) { return "<li>" + esc(o[1]) + "</li>"; }).join("") + '</ul></div>' +
          (L.adult ? '<p class="bl-adult"><label class="opt"><input type="checkbox" name="adult"' + (needAdult(st.parts) ? " required" : "") + '> ' + esc(T.bl_adult_check) + '</label></p>' : "") +
          '<div class="actions"><button class="btn" type="submit">' + esc(saved && !p1 ? T.bl_update : T.start) + '</button></div></form>';
      } else if (st.step <= ag.length) {
        var x = ag[st.step - 1], sec = L.sections[x.si], firstOfSec = st.step === 1 || ag[st.step - 2].si !== x.si;
        h = '<div class="progress"><i style="width:' + Math.round((st.step - 1) / ag.length * 100) + '%"></i></div><form class="step"><p class="eyebrow">' + esc(sec.title) + ' · ' + fmt(esc(T.bl_group_of), { i: st.step, n: ag.length }) + '</p><h2>' + esc(x.g.title) + '</h2>' +
          (firstOfSec ? '<p>' + esc(sec.lead) + '</p>' : "") + (x.g.note ? '<div class="note">' + esc(x.g.note) + '</div>' : "") +
          x.idx.map(function (i) { return '<div class="item lm-item"><p class="q">' + esc(flat[i]) + '</p><div class="opts">' + L.options.map(function (o, k) { return '<label class="opt"><input type="radio" name="q' + i + '" value="' + k + '"' + (st.ans[i] === k ? " checked" : "") + '> ' + esc(o[1]) + '</label>'; }).join("") + '</div></div>'; }).join("") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(st.step === ag.length ? (p1 ? T.finish : X.see) : T.next) + '</button></div></form>';
      } else h = p1 ? pair(p1, { me: st.me, you: st.you, parts: st.parts, ans: st.ans }, true) : solo();
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f && st.step === 0) {
        var boxes = Array.prototype.slice.call(f.querySelectorAll("[name=part]")), ad = f.querySelector("[name=adult]");
        var cur = function () { var p = st.parts.slice(); boxes.forEach(function (b) { p[+b.value] = b.checked; }); return p; };
        var sync = function () { if (ad) { var need = needAdult(cur()); ad.required = need; ad.closest(".bl-adult").classList.toggle("hidden", !need); } if (boxes[0]) boxes[0].setCustomValidity(""); };
        boxes.forEach(function (b) { b.addEventListener("change", sync); }); sync();
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          var p = cur(); if (!p.some(Boolean)) { boxes[0].setCustomValidity(T.bl_parts); boxes[0].reportValidity(); return; }
          st.me = f.me.value.trim() || T.default_person; if (f.you) st.you = f.you.value.trim(); st.parts = p; st.dirty = true; st.step = 1; render();
        });
        var v = f.querySelector("[data-view]"); if (v) v.addEventListener("click", function () { st.step = ag.length + 1; render(); });
      } else if (f) {
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          ag[st.step - 1].idx.forEach(function (i) { var val = readRadio(f, "q" + i); st.ans[i] = val == null ? -1 : +val; });
          save(); st.dirty = true; st.step++; render();
        });
        f.querySelector("[data-back]").addEventListener("click", function () { st.step--; render(); });
      }
      if (st.step > ag.length) wire();
      if (!first) window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
      first = false;
    }
    function listing(idxs, tagOf) {
      if (!idxs.length) return '<p class="muted">' + esc(T.bl_empty_group) + '</p>';
      var set = {}; idxs.forEach(function (i) { set[i] = 1; });
      return G.map(function (x) {
        var mine = x.idx.filter(function (i) { return set[i]; }); if (!mine.length) return "";
        return '<h4>' + esc(x.g.title) + '</h4><ul>' + mine.map(function (i) { var tg = tagOf ? tagOf(i) : ""; return '<li>' + esc(flat[i]) + (tg ? ' <span class="muted">· ' + esc(tg) + '</span>' : "") + '</li>'; }).join("") + '</ul>';
      }).join("");
    }
    function block(title, text, idxs, open, tagOf) {
      return '<details class="bl-block"' + (open ? " open" : "") + '><summary>' + esc(title) + ' <span class="muted">· ' + idxs.length + '</span></summary>' + (text ? '<p class="muted">' + esc(text) + '</p>' : "") + listing(idxs, tagOf) + '</details>';
    }
    function barsOf(rows) {
      return '<div class="bars">' + rows.map(function (r) { return '<div class="bar"><span>' + esc(r.name) + '</span><i><b style="width:' + r.pct + '%"></b></i><span class="v">' + esc(r.label) + '</span></div>'; }).join("") + '</div>';
    }
    function imgRows(rows) {
      var keep = rows.slice().sort(function (a, b) { return b.pct - a.pct; }).slice(0, 14);
      return rows.filter(function (r) { return keep.indexOf(r) >= 0; }).map(function (r) { return { name: r.name, pos: r.label, x: r.pct / 25, presumed: null, poles: ["", ""] }; });
    }
    function summary(ans, parts) {
      var c = [0, 0, 0, 0], by = [[], [], [], []], rows = [], total = 0;
      active(parts).forEach(function (x) {
        total += x.idx.length;
        var a = x.idx.filter(function (i) { return ans[i] >= 0; }); if (!a.length) return;
        a.forEach(function (i) { c[ans[i]]++; by[ans[i]].push(i); });
        var pct = Math.round(a.filter(function (i) { return L.bar === "yes" ? ans[i] >= 2 : ans[i] === 3; }).length / a.length * 100);
        rows.push({ name: x.g.title, pct: pct, label: fmt(T.bl_yes_pct, { p: pct }) });
      });
      return { c: c, by: by, rows: rows, total: total, answered: c[0] + c[1] + c[2] + c[3] };
    }
    function pickBox(pool) {
      pickPool = pool;
      return L.pick && pool.length ? '<div class="actions"><button class="btn ghost" type="button" data-pick>' + esc(X.pick_btn) + '</button></div><div class="note hidden" id="bl-pick" role="status" aria-live="polite"></div>' : "";
    }
    function solo() {
      if (st.dirty || !saved) save();
      var s = summary(st.ans, st.parts), url = base + "#l1=" + codec.enc({ me: st.me, you: st.you, parts: st.parts, ans: st.ans });
      pairCache = null;
      var h = '<div class="step result"><p class="eyebrow">' + esc(L.kicker) + ' · ' + esc(st.me) + ' · ' + esc(fmtDate(saved.date)) + '</p><h2>' + esc(X.solo_title) + '</h2><p class="muted">' + fmt(esc(T.bl_answered), { n: s.answered, N: s.total }) + '</p>' +
        '<p class="bl-counts">' + [3, 2, 1, 0].map(function (k) { return '<span class="stat"><b>' + s.c[k] + '</b> ' + esc(L.options[k][1]) + '</span>'; }).join("") + '</p>' +
        (s.rows.length ? '<h4>' + esc(X.bar_title) + '</h4>' + barsOf(s.rows) : '<div class="note">' + esc(T.bl_none) + '</div>') + '</div>';
      h += '<div class="step">' + (s.answered && !s.by[2].length ? '<div class="note">' + esc(X.want_empty) + '</div>' : "") + block(X.want_title, null, s.by[2], true) + block(X.maybe_title, null, s.by[1], false) + block(X.done_title, null, s.by[3], false) + pickBox(s.by[2].concat(s.by[3])) + '</div>';
      h += '<div class="step"><h3>' + esc(X.link_title) + '</h3><p class="muted">' + esc(X.link_text) + '</p><p class="code" id="bl-url">' + esc(url) + '</p><div class="actions"><button class="btn" type="button" data-copy>' + esc(T.bl_copy) + '</button>' + shareBtn(X.share_btn) +
        '<button class="btn ghost" type="button" data-update>' + esc(T.bl_update) + '</button><button class="btn ghost" type="button" data-redo>' + esc(T.bl_redo) + '</button></div><p class="muted">' + esc(T.bl_warn) + '</p></div>';
      return h;
    }
    function pair(x, y, withLink) {
      var go = [], keep = [], talk = [], hidden = 0, tag = {};
      for (var i = 0; i < N; i++) {
        var a = x.ans[i], b = y.ans[i]; if (a < 0 || b < 0) continue;
        if (!a || !b) hidden++;
        else if (a === 3 && b === 3) keep.push(i);
        else if (a >= 2 && b >= 2) { go.push(i); if (a === 3 || b === 3) tag[i] = fmt(X.tag3, { n: a === 3 ? x.me : y.me }); }
        else talk.push(i);
      }
      var sum = fmt(X.pair_sum, { go: go.length, keep: keep.length, talk: talk.length }), set = {}; go.forEach(function (i) { set[i] = 1; });
      var rows = G.map(function (g) { var n = g.idx.filter(function (i) { return set[i]; }).length; return { name: g.g.title, n: n }; }).filter(function (r) { return r.n; });
      var max = rows.reduce(function (m, r) { return Math.max(m, r.n); }, 1); rows.forEach(function (r) { r.pct = Math.round(r.n / max * 100); r.label = String(r.n); });
      var h = '<div class="step result"><p class="eyebrow">' + fmt(esc(T.bl_kicker_pair), { k: esc(L.kicker), x: esc(x.me), y: esc(y.me) }) + '</p><h2>' + esc(X.pair_title) + '</h2><p>' + esc(sum) + '</p>' +
        (go.length ? "" : '<div class="note">' + esc(X.none_go) + '</div>') + block(X.go_title, X.go_text, go, true, function (i) { return tag[i]; }) + block(X.keep_title, X.keep_text, keep, false) + block(X.talk_title, X.talk_text, talk, !go.length) +
        (hidden ? '<p class="muted">' + fmt(esc(X.hidden), { n: hidden }) + '</p>' : "") + pickBox(go.concat(keep)) + '</div>';
      if (withLink) {
        var url = base + "#l1=" + hp.l1 + "&l2=" + codec.enc(y);
        h += '<div class="step"><h3>' + esc(T.bl_done_p2) + '</h3><p class="code" id="bl-url">' + esc(url) + '</p><div class="actions"><button class="btn" type="button" data-copy>' + esc(T.bl_copy) + '</button>' + shareBtn(X.share_btn) + '</div><p class="muted">' + esc(T.bl_warn) + '</p></div>';
      } else h += '<div class="step"><div class="actions">' + shareBtn(X.share_btn) + '</div></div>';
      pairCache = { x: x, y: y, rows: rows, sum: sum };
      return h;
    }
    function wire() {
      var c = root.querySelector("[data-copy]"), u = root.querySelector("#bl-url"); if (c && u) c.addEventListener("click", function () { navigator.clipboard && navigator.clipboard.writeText(u.textContent); c.textContent = T.copied; });
      var up = root.querySelector("[data-update]"); if (up) up.addEventListener("click", function () { st.step = 0; render(); });
      var rd = root.querySelector("[data-redo]"); if (rd) rd.addEventListener("click", function () { store.set(key, null); saved = null; st = { step: 0, me: st.me, you: st.you, ans: blank(), parts: L.sections.map(function (s) { return !!s["default"]; }), dirty: false }; render(); });
      var pk = root.querySelector("[data-pick]"), box = root.querySelector("#bl-pick");
      if (pk && box) pk.addEventListener("click", function () { var i = pickPool[Math.floor(Math.random() * pickPool.length)]; box.innerHTML = '<b>' + esc(X.pick_title) + '</b><p style="margin:6px 0 0">' + esc(flat[i]) + '</p>'; box.classList.remove("hidden"); pk.textContent = T.bl_again; });
      var s = root.querySelector("[data-share]"); if (!s) return;
      s.addEventListener("click", function () {
        if (pairCache) {
          var t = fmt(X.share_pair, { x: pairCache.x.me, y: pairCache.y.me });
          shareDialog({ file: key, kicker: L.kicker, title: t, shortTitle: t, rows: imgRows(pairCache.rows), lines: [pairCache.sum] });
        } else {
          var sm = summary(st.ans, st.parts);
          shareDialog({ file: key, kicker: L.kicker, title: X.share_solo, shortTitle: X.share_solo, rows: imgRows(sm.rows), lines: [fmt(X.line_solo, { q: sm.c[2], d: sm.c[3], t: sm.c[1], a: sm.answered })] });
        }
      });
    }
    render();
  }

  /* ---------- Mitologia Sexual: mito ou verdade, com a explicação na hora ----------
     Item = [afirmação, 1 verdade / 0 mito, explicação, links opcionais [[rótulo, url]]].
     Resposta: 0 mito, 1 verdade, 2 não sei, -1 sem resposta. Duas versões: curta (th.short, índices
     das afirmações essenciais de cada tema, definidos no build) e completa (tudo, por tema). */
  function myths(root) {
    var M = D.myths, X = M.t, flat = [], TH = [];
    M.themes.forEach(function (th, ti) {
      var idx = th.items.map(function (it) { flat.push(it); return flat.length - 1; });
      TH.push({ ti: ti, th: th, idx: idx, sidx: (th.short || []).map(function (k) { return idx[k]; }) });
    });
    var N = flat.length, NT = TH.length, NS = TH.reduce(function (a, x) { return a + x.sidx.length; }, 0);
    var mins = function (n) { return Math.max(1, Math.round(n * M.secs / 60)); };
    var sizeOf = function (n) { return fmt(esc(X.count), { n: n }) + ' · ' + fmt(esc(X.time), { m: mins(n) }); };
    var saved = store.get("myths"); if (saved && (saved.v !== M.v || !saved.ans || saved.ans.length !== N || !saved.parts || saved.parts.length !== NT || (saved.mode !== "short" && saved.mode !== "full"))) saved = null;
    var blank = function () { var a = []; for (var i = 0; i < N; i++) a.push(-1); return a; };
    var allParts = function () { return TH.map(function () { return true; }); };
    var st = { step: 0, mode: saved ? saved.mode : "short", ans: blank(), parts: saved ? saved.parts.slice() : allParts() }, first = true;
    var ids = function (x, mode) { return mode === "short" ? x.sidx : x.idx; };
    var active = function (parts, mode) { return TH.filter(function (x) { return (mode === "short" || parts[x.ti]) && ids(x, mode).length; }); };
    function fb(i) {
      var a = st.ans[i], it = flat[i]; if (a < 0) return "";
      var ok = a === it[1];
      return '<div class="fb ' + (ok ? "ok" : a === 2 ? "dk" : "no") + '"><b>' + esc(ok ? X.right : a === 2 ? X.dunno : X.wrong) + ' ' + esc(it[1] ? X.is_true : X.is_myth) + '</b> ' + esc(it[2]) +
        (it[3] ? ' ' + it[3].map(function (l) { return '<a href="' + esc(l[1]) + '" target="_blank" rel="noopener">' + esc(l[0]) + ' ↗</a>'; }).join(" · ") : "") + '</div>';
    }
    function score(ans, parts, mode) {
      var rows = [], c = 0, a = 0, n = 0, bel = [], dou = [], unk = [];
      active(parts, mode).forEach(function (x) {
        var ca = 0, aa = 0;
        ids(x, mode).forEach(function (i) { n++; var v = ans[i]; if (v < 0) return; aa++; if (v === flat[i][1]) ca++; else if (v === 2) unk.push(i); else if (flat[i][1]) dou.push(i); else bel.push(i); });
        c += ca; a += aa; if (aa) rows.push({ name: x.th.title, pct: Math.round(ca / aa * 100), label: ca + "/" + aa });
      });
      return { rows: rows, c: c, a: a, n: n, bel: bel, dou: dou, unk: unk, pct: a ? Math.round(c / a * 100) : 0 };
    }
    function review(title, idxs, open) {
      if (!idxs.length) return "";
      return '<details class="bl-block"' + (open ? " open" : "") + '><summary>' + esc(title) + ' <span class="muted">· ' + idxs.length + '</span></summary>' +
        idxs.map(function (i) { return '<div class="rv"><p class="q">' + esc(flat[i][0]) + '</p>' + fb(i) + '</div>'; }).join("") + '</details>';
    }
    function render() {
      var h = "", ag = active(st.parts, st.mode);
      if (st.step === 0) {
        var sv = saved ? score(saved.ans, saved.parts, saved.mode) : null;
        var modeOpt = function (m, name, n, text) { return '<div class="bl-part"><label class="opt"><input type="radio" name="mode" value="' + m + '"' + (st.mode === m ? " checked" : "") + '> ' + esc(name) + ' <span class="muted">· ' + sizeOf(n) + '</span></label><p class="small muted">' + esc(text) + '</p></div>'; };
        h = '<form class="step">' + (saved ? '<div class="note"><p>' + fmt(esc(X.saved), { date: esc(fmtDate(saved.date)), c: sv.c, n: sv.a }) + '</p><div class="actions"><button class="btn ghost" type="button" data-view>' + esc(X.view) + '</button></div></div>' : "") +
          '<h2>' + esc(X.start_title) + '</h2><div class="note"><ul>' + M.notes.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + '</ul></div>' +
          '<h3>' + esc(X.mode_title) + '</h3><div class="bl-parts">' + modeOpt("short", X.short_name, NS, X.short_text) + modeOpt("full", X.full_name, N, X.full_text) + '</div>' +
          '<div class="my-themes' + (st.mode === "full" ? "" : " hidden") + '"><h3>' + esc(X.parts) + '</h3><div class="bl-parts">' +
          TH.map(function (x) { return '<div class="bl-part"><label class="opt"><input type="checkbox" name="part" value="' + x.ti + '"' + (st.parts[x.ti] ? " checked" : "") + '> ' + esc(x.th.title) + ' <span class="muted">· ' + sizeOf(x.idx.length) + '</span></label><p class="small muted">' + esc(x.th.lead) + '</p></div>'; }).join("") +
          '</div></div><div class="actions"><button class="btn" type="submit">' + esc(saved ? X.again : X.start) + '</button></div></form>';
      } else if (st.step <= ag.length) {
        var x = ag[st.step - 1];
        h = '<div class="progress"><i style="width:' + Math.round((st.step - 1) / ag.length * 100) + '%"></i></div><form class="step"><p class="eyebrow">' + fmt(esc(X.group_of), { i: st.step, n: ag.length }) + '</p><h2>' + esc(x.th.title) + '</h2><p>' + esc(x.th.lead) + '</p>' +
          ids(x, st.mode).map(function (i) {
            var done = st.ans[i] >= 0;
            return '<div class="item lm-item"><p class="q">' + esc(flat[i][0]) + '</p><div class="opts">' + [1, 0, 2].map(function (k) { return '<label class="opt"><input type="radio" name="q' + i + '" value="' + k + '"' + (st.ans[i] === k ? " checked" : "") + (done ? " disabled" : "") + '> ' + esc(M.options[k]) + '</label>'; }).join("") + '</div><div class="fb-slot" aria-live="polite">' + fb(i) + '</div></div>';
          }).join("") +
          '<div class="actions"><button class="btn ghost" type="button" data-back>' + esc(T.back) + '</button><button class="btn" type="submit">' + esc(st.step === ag.length ? X.see : T.next) + '</button></div></form>';
      } else h = result();
      root.innerHTML = h;
      var f = root.querySelector("form");
      if (f && st.step === 0) {
        var boxes = Array.prototype.slice.call(f.querySelectorAll("[name=part]")), themes = f.querySelector(".my-themes");
        var modeNow = function () { return readRadio(f, "mode") || "short"; };
        Array.prototype.forEach.call(f.querySelectorAll("[name=mode]"), function (r) { r.addEventListener("change", function () { themes.classList.toggle("hidden", modeNow() !== "full"); boxes[0].setCustomValidity(""); }); });
        boxes.forEach(function (b) { b.addEventListener("change", function () { boxes[0].setCustomValidity(""); }); });
        f.addEventListener("submit", function (e) {
          e.preventDefault();
          var m = modeNow(), p = m === "full" ? boxes.map(function (b) { return b.checked; }) : allParts();
          if (!p.some(Boolean)) { boxes[0].setCustomValidity(X.parts); boxes[0].reportValidity(); return; }
          st = { step: 1, mode: m, ans: blank(), parts: p }; render();
        });
        var v = f.querySelector("[data-view]"); if (v) v.addEventListener("click", function () { st = { step: active(saved.parts, saved.mode).length + 1, mode: saved.mode, ans: saved.ans.slice(), parts: saved.parts.slice(), keep: true }; render(); });
      } else if (f) {
        f.addEventListener("change", function (e) {
          var r = e.target; if (!r || r.type !== "radio") return;
          var i = +r.name.slice(1), it = r.closest(".item"); st.ans[i] = +r.value;
          it.querySelector(".fb-slot").innerHTML = fb(i);
          Array.prototype.forEach.call(it.querySelectorAll("input"), function (el) { el.disabled = true; });
        });
        f.addEventListener("submit", function (e) { e.preventDefault(); st.step++; render(); });
        f.querySelector("[data-back]").addEventListener("click", function () { st.step--; render(); });
      } else wire();
      if (!first) window.scrollTo({ top: root.offsetTop - 90, behavior: "smooth" });
      first = false;
    }
    function result() {
      if (!st.keep) { saved = { v: M.v, date: new Date().toISOString(), mode: st.mode, ans: st.ans, parts: st.parts }; store.set("myths", saved); st.keep = true; }
      var s = score(st.ans, st.parts, st.mode), lv = !s.a ? null : X.levels[s.pct < 50 ? 0 : s.pct < 70 ? 1 : s.pct < 90 ? 2 : 3];
      var h = '<div class="step result"><p class="eyebrow">' + esc(M.kicker) + ' · ' + esc(st.mode === "short" ? X.short_name : X.full_name) + ' · ' + esc(fmtDate(saved.date)) + '</p><h2>' + fmt(esc(X.result_title), { c: s.c, n: s.a }) + '</h2><p class="muted">' + fmt(esc(X.answered), { a: s.a, n: s.n }) + '</p>' +
        (lv ? '<p>' + esc(lv) + '</p><h4>' + esc(X.bar_title) + '</h4><div class="bars">' + s.rows.map(function (r) { return '<div class="bar"><span>' + esc(r.name) + '</span><i><b style="width:' + r.pct + '%"></b></i><span class="v">' + esc(r.label) + '</span></div>'; }).join("") + '</div>' : '<div class="note">' + esc(X.empty) + '</div>') + '</div>';
      if (s.a) h += '<div class="step">' + (s.bel.length + s.dou.length + s.unk.length ? review(X.believed, s.bel, true) + review(X.doubted, s.dou, !s.bel.length) + review(X.unknown, s.unk, !s.bel.length && !s.dou.length) : '<div class="note">' + esc(X.none_wrong) + '</div>') + '</div>';
      h += '<div class="step">' + (st.mode === "short" ? '<h3>' + esc(X.full_name) + ' <span class="muted">· ' + sizeOf(N - s.a) + '</span></h3><p class="muted">' + esc(X.to_full_text) + '</p><div class="actions"><button class="btn" type="button" data-full>' + esc(X.to_full) + '</button></div>' : "") +
        '<h3>' + esc(X.next_title) + '</h3><ul>' + X.next.map(function (k) { return '<li><a href="' + esc(P[k[0]]) + '">' + esc(k[1]) + '</a>: ' + esc(k[2]) + '</li>'; }).join("") + '</ul><div class="actions">' + (s.a ? shareBtn(X.share_btn) : "") + '<button class="btn ghost" type="button" data-again>' + esc(X.again) + '</button></div></div>';
      return h;
    }
    function wire() {
      var a = root.querySelector("[data-again]"); if (a) a.addEventListener("click", function () { st = { step: 0, mode: st.mode, ans: blank(), parts: st.parts }; render(); });
      var fu = root.querySelector("[data-full]"); if (fu) fu.addEventListener("click", function () { st = { step: 1, mode: "full", ans: st.ans, parts: allParts() }; render(); });
      var sh = root.querySelector("[data-share]"); if (!sh) return;
      sh.addEventListener("click", function () {
        var s = score(st.ans, st.parts, st.mode), by = s.rows.slice().sort(function (p, q) { return q.pct - p.pct; }), t = fmt(X.share_title, { p: s.pct });
        shareDialog({ file: "myths", kicker: M.kicker, title: t, shortTitle: t, rows: s.rows.map(function (r) { return { name: r.name, pos: r.label, x: r.pct / 25, presumed: null, poles: ["", ""] }; }),
          lines: [fmt(X.line, { c: s.c, n: s.a, best: by[0].name, worst: by[by.length - 1].name })] });
      });
    }
    render();
  }

  /* ---------- Minhas flags ---------- */
  function myFlags(root) {
    var saved = store.get("myflags", []);
    root.innerHTML = '<form class="step"><h3>' + esc(T.mf_title) + '</h3><p class="muted">' + esc(T.mf_text) + '</p><div class="opts">' +
      D.flags.map(function (f, i) { return '<label class="opt"><input type="checkbox" name="f" value="' + i + '"' + (saved.indexOf(i) >= 0 ? " checked" : "") + '> <span class="tag ' + f.sign + '">' + f.sign + '</span> ' + esc(f.text) + '</label>'; }).join("") +
      '</div><div class="actions"><button class="btn" type="submit">' + esc(T.mf_see) + '</button></div><div id="myflags-out"></div></form>';
    var f = root.querySelector("form");
    function show(sel) {
      var count = {}; sel.forEach(function (i) { D.flags[i].props.forEach(function (p) { count[K(p)] = (count[K(p)] || 0) + 1; }); });
      var watched = ORDER.filter(function (k) { return count[k]; }).sort(function (a, b) { return count[b] - count[a]; }), ignored = ORDER.filter(function (k) { return !count[k] && k !== K("sombras"); });
      var reds = sel.filter(function (i) { return D.flags[i].sign === "red"; }).length, greens = sel.length - reds;
      $("#myflags-out").innerHTML = sel.length ? '<div class="note"><p>' + fmt(esc(T.mf_watch), { w: "<b>" + esc(names(watched.slice(0, 4))) + "</b>" }) + (ignored.length ? fmt(esc(T.mf_ignore), { i: "<b>" + esc(names(ignored.slice(0, 5))) + "</b>" }) : "") + '.</p><p>' +
        esc(reds > greens * 2 ? T.mf_reds : greens > reds * 2 ? T.mf_greens : T.mf_balanced) + '</p><p class="muted">' + esc(T.mf_footer) + '</p></div>' : "";
    }
    f.addEventListener("submit", function (e) { e.preventDefault(); var sel = Array.prototype.map.call(f.querySelectorAll('[name=f]:checked'), function (c) { return +c.value; }); store.set("myflags", sel); show(sel); });
    if (saved.length) show(saved);
  }

  /* ---------- acessibilidade: liga cada controle ao seu rótulo depois de cada renderização ---------- */
  var aid = 0, nid = function (el, pre) { if (!el.id) el.id = (pre || "a") + "-" + (++aid); return el.id; };
  function a11y(scope) {
    scope.querySelectorAll(".field").forEach(function (f) {
      var lab = f.querySelector(":scope > label"), ctl = f.querySelector("input, select, textarea");
      if (lab && ctl && !lab.htmlFor) lab.htmlFor = nid(ctl, "f");
    });
    scope.querySelectorAll('input[type=text]:not([maxlength])').forEach(function (i) { i.maxLength = 40; i.autocomplete = "off"; });
    scope.querySelectorAll(".item").forEach(function (it) {
      var q = it.querySelector(".q"); if (!q) return;
      var qid = nid(q, "q");
      it.querySelectorAll('input[type=range]:not([aria-labelledby])').forEach(function (r) { r.setAttribute("aria-labelledby", qid); });
      it.querySelectorAll(".opts").forEach(function (o) { if (!o.getAttribute("role")) { o.setAttribute("role", "radiogroup"); o.setAttribute("aria-labelledby", qid); } });
    });
    scope.querySelectorAll(".slider-card").forEach(function (c) {
      var h = c.querySelector("h4"); if (!h) return;
      var hid = nid(h, "s");
      var rs = c.querySelectorAll("input[type=range]");
      if (rs[0] && !rs[0].hasAttribute("aria-labelledby")) rs[0].setAttribute("aria-labelledby", hid);
      if (rs[1] && !rs[1].hasAttribute("aria-label")) rs[1].setAttribute("aria-label", T.variability + " · " + h.textContent);
      c.querySelectorAll(".chips").forEach(function (g) { if (!g.getAttribute("role")) { g.setAttribute("role", "group"); g.setAttribute("aria-labelledby", hid); } });
    });
    scope.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", b.classList.contains("on") ? "true" : "false"); });
    scope.querySelectorAll("table.balance select:not([aria-label])").forEach(function (sel) { var td = sel.closest("tr").querySelector("td"); sel.setAttribute("aria-label", (td ? td.textContent : "") + " · " + T.th_weight); });
  }
  document.addEventListener("click", function (ev) { var c = ev.target.closest && ev.target.closest(".chip"); if (c) setTimeout(function () { c.setAttribute("aria-pressed", c.classList.contains("on") ? "true" : "false"); }, 0); });

  document.addEventListener("DOMContentLoaded", function () {
    var app = $("#app"); if (!app) return;
    if (window.MutationObserver) new MutationObserver(function () { a11y(app); }).observe(app, { childList: true, subtree: true });
    var tool = app.getAttribute("data-tool");
    ({ scale: scale, portraits: portraits, selflove: selfLove, couple: couple, selfdiscover: selfDiscover, myflags: myFlags, stay: stay, glossary: glossary, limits: limits, myths: myths, spark: function (r) { lists(r, "spark"); }, lovelist: function (r) { lists(r, "lovelist"); }, sexlist: function (r) { lists(r, "sexlist"); } }[tool] || function () { })(app);
  });
})();
