/* Arabic AI Atlas: the geographic map view. d3 + topojson-client, vendored.
 * Pure helpers (bubble ring layout, choropleth step, bubble radius, hash round trip) are exported
 * for Node tests; the DOM part registers window.AtlasMap and is driven by app.js. */
(function () {
  "use strict";

  var TYPE_ORDER = ["llm", "asr", "tts", "ocr", "embedding", "tool", "benchmark", "dataset", "org", "agent-skill"];
  var R_MIN = 4, R_MAX = 26, RING_GAP = 3;

  /* ---------- pure helpers ---------- */

  // 0..4 on a log scale of entry count relative to the busiest country. Zero stays 0.
  function choroplethStep(count, max) {
    count = +count || 0; max = +max || 0;
    if (count <= 0 || max <= 0) return 0;
    var s = Math.log(count + 1) / Math.log(Math.max(max, count) + 1);
    return Math.max(0, Math.min(4, Math.floor(s * 5 - 1e-9)));
  }

  // Radius ∝ sqrt(downloads + 1), from R_MIN up to R_MAX at `max` downloads; clamped.
  function bubbleRadius(downloads, max) {
    var d = Math.max(0, +downloads || 0), m = Math.max(1, +max || 0);
    if (d >= m) return R_MAX;
    var r = R_MIN + (R_MAX - R_MIN) * (Math.sqrt(d + 1) - 1) / (Math.sqrt(m + 1) - 1 || 1);
    return Math.max(R_MIN, Math.min(R_MAX, r));
  }

  // One ring position per type with entries, in TYPE_ORDER, clockwise starting at 12 o'clock.
  // Each bubble gets an arc share proportional to its diameter so neighbours do not collide.
  // countryTotals: {type: {n, downloads, r?}}; radius(t, type) overrides the radius.
  function bubbleLayout(countryTotals, radius) {
    var totals = countryTotals || {};
    var rOf = radius || function (t) { return t.r || bubbleRadius(t.downloads, 1e6); };
    var items = TYPE_ORDER.concat(Object.keys(totals).filter(function (k) { return TYPE_ORDER.indexOf(k) === -1; }).sort())
      .filter(function (type) { return totals[type] && totals[type].n > 0; })
      .map(function (type) {
        var t = totals[type];
        return { type: type, n: t.n, downloads: t.downloads || 0, r: rOf(t, type), x: 0, y: 0, angle: 0 };
      });
    if (items.length <= 1) return items;
    var span = items.reduce(function (s, it) { return s + 2 * it.r + RING_GAP; }, 0);
    var R = Math.max(span / (2 * Math.PI) * 1.1, 9);
    if (items.length === 2) R = Math.max(R, (items[0].r + items[1].r + RING_GAP) / 2);
    // The first bubble sits exactly at 12 o'clock.
    var acc = -(2 * items[0].r + RING_GAP) / span * Math.PI;
    items.forEach(function (it) {
      var share = (2 * it.r + RING_GAP) / span * 2 * Math.PI;
      var a = -Math.PI / 2 + acc + share / 2;
      acc += share;
      it.angle = a;
      it.x = Math.round(R * Math.cos(a) * 100) / 100;
      it.y = Math.round(R * Math.sin(a) * 100) / 100;
    });
    items.ring = R;
    return items;
  }

  // The map's bubble scale tops out at the largest (country, type) download total among the
  // Arab countries; International entries are docked under the map with their own scale.
  function cellMax(entries, intl) {
    var cells = {}, best = { key: null, downloads: 0 };
    (entries || []).forEach(function (e) {
      var c = e.country || "INTL";
      if ((c === "INTL") !== !!intl) return;
      var k = c + "|" + e.type;
      cells[k] = (cells[k] || 0) + ((e.metrics && e.metrics.downloads) || 0);
      if (cells[k] > best.downloads) best = { key: k, downloads: cells[k] };
    });
    return best;
  }

  // Extent of a ring layout (distance from centre to the outermost bubble edge).
  function ringExtent(items) {
    return items.reduce(function (m, it) { return Math.max(m, Math.hypot(it.x, it.y) + it.r); }, 0);
  }

  function core() {
    if (typeof module !== "undefined" && module.exports && typeof require === "function") return require("./app.js");
    return typeof window !== "undefined" ? window.Atlas : null;
  }

  // Canonical hash for a hash string: parse then serialise with the app's own state rules.
  function hashState(hash) { var c = core(); return c.serializeHash(c.parseHash(hash)); }

  var api = {
    choroplethStep: choroplethStep, bubbleRadius: bubbleRadius, bubbleLayout: bubbleLayout,
    ringExtent: ringExtent, cellMax: cellMax, hashState: hashState, TYPE_ORDER: TYPE_ORDER
  };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  if (typeof document === "undefined") return;

  /* ---------- DOM ---------- */

  var d3 = window.d3, topojson = window.topojson;
  var BBOX = { west: -13.2, east: 59.8, south: 12.1, north: 37.3 };
  var PAD = 0.06;
  var MOBILE = window.matchMedia ? window.matchMedia("(max-width: 899px)") : { matches: false };
  var REDUCED = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };

  var S = {
    ready: false, opts: null, geo: null, meta: null, features: {}, all: null, land: null,
    w: 0, h: 0, projection: null, path: null, zoom: null, transform: d3 ? d3.zoomIdentity : null,
    svg: null, gGeo: null, gMarks: null, zoomedTo: null, data: null, lastKey: null, pending: null
  };

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    for (var k in attrs || {}) {
      if (attrs[k] == null || attrs[k] === false) continue;
      if (k === "text") n.textContent = attrs[k]; else if (k === "className") n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    }
    (children || []).forEach(function (c) { if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function dur(ms) { return REDUCED.matches ? 0 : ms; }
  function fmt(n) {
    if (!n) return "0";
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
    if (n >= 1e3) return Math.round(n / 1e3) + "K";
    return String(n);
  }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

  function init(opts) {
    S.opts = opts;
    var stage = opts.stage;
    var base = opts.base || "./";
    Promise.all([
      fetch(base + "geo/countries-110m.json").then(function (r) { return r.json(); }),
      fetch(base + "geo/centroids.json").then(function (r) { return r.json(); })
    ]).then(function (res) {
      var topo = res[0];
      S.meta = res[1];
      S.all = topojson.feature(topo, topo.objects.countries).features;
      S.land = topojson.merge(topo, topo.objects.countries.geometries);
      S.all.forEach(function (f) { S.features[f.id] = f; });
      build(stage);
      S.ready = true;
      if (S.pending) { update(S.pending); S.pending = null; }
    }).catch(function () {
      stage.querySelector(".map-msg").textContent = "The map geometry could not be loaded. Switch to the grid view to browse the atlas.";
    });
  }

  function arabMeta() {
    var out = {};
    Object.keys(S.meta.countries).forEach(function (c) { out[S.meta.countries[c].id] = { code: c, listed: true, m: S.meta.countries[c] }; });
    Object.keys(S.meta.arab_league_other).forEach(function (c) { out[S.meta.arab_league_other[c].id] = { code: c, listed: false, m: S.meta.arab_league_other[c] }; });
    out["732"] = out["732"] || { code: "EH", listed: false, m: { ar: "", en: "" }, unlabeled: true };
    return out;
  }

  function build(stage) {
    var svgNode = stage.querySelector("svg.map");
    S.svg = d3.select(svgNode);
    S.svg.selectAll("*").remove();
    var defs = S.svg.append("defs");
    var hatch = defs.append("pattern").attr("id", "hatch").attr("patternUnits", "userSpaceOnUse")
      .attr("width", 6).attr("height", 6).attr("patternTransform", "rotate(45)");
    hatch.append("rect").attr("class", "hatch-bg").attr("width", 6).attr("height", 6);
    hatch.append("line").attr("class", "hatch-line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6);

    S.svg.append("rect").attr("class", "sea").attr("x", -1e4).attr("y", -1e4).attr("width", 2e4).attr("height", 2e4)
      .on("click", function () { reset(); });
    S.gGeo = S.svg.append("g").attr("class", "geo");
    S.gMarks = S.svg.append("g").attr("class", "marks");

    S.zoom = d3.zoom().scaleExtent([1, 8]).on("zoom", function (ev) {
      S.transform = ev.transform;
      S.gGeo.attr("transform", ev.transform);
      placeMarks();
      syncReset();
    });
    S.arab = arabMeta();
    placeStage();
    layout();
    var ro = new ResizeObserver(function () {
      var w = Math.round(stage.querySelector(".map-frame").clientWidth);
      if (w && Math.abs(w - S.w) > 1) refresh();
    });
    ro.observe(stage.querySelector(".map-frame"));
    (MOBILE.addEventListener ? MOBILE.addEventListener.bind(MOBILE, "change") : MOBILE.addListener.bind(MOBILE))(function () {
      refresh();
    });
    stage.querySelector(".map-reset").addEventListener("click", function () { reset(); });
    stage.querySelector(".map-msg").textContent = "";
  }

  // Phones get the map as a static hero above the filters; desktop keeps it in the main column.
  function placeStage() {
    var stage = S.opts.stage, layoutEl = document.querySelector(".layout");
    if (!S.home) S.home = { parent: stage.parentNode, next: stage.nextSibling };
    if (MOBILE.matches && layoutEl) layoutEl.parentNode.insertBefore(stage, layoutEl);
    else if (stage.parentNode !== S.home.parent) S.home.parent.insertBefore(stage, S.home.next);
  }

  function refresh() {
    placeStage();
    layout();
    if (!S.data) return;
    draw(false);
    panel();
    var sel = selected();
    zoomTo(sel && S.meta.countries[sel] ? sel : null, false);
  }

  function bboxPoints() {
    var pts = [];
    for (var x = BBOX.west; x <= BBOX.east; x += 1) { pts.push([x, BBOX.south]); pts.push([x, BBOX.north]); }
    for (var y = BBOX.south; y <= BBOX.north; y += 1) { pts.push([BBOX.west, y]); pts.push([BBOX.east, y]); }
    return { type: "MultiPoint", coordinates: pts };
  }

  // Fit the projection to the Arab world box; height follows the box's aspect so nothing clips.
  function layout() {
    var frame = S.opts.stage.querySelector(".map-frame");
    var w = Math.max(320, frame.clientWidth || 960);
    var proj = d3.geoConicConformal().parallels([18, 34]).rotate([-23, 0]);
    var box = bboxPoints();
    // Phones keep a little extra room on the right for the Gulf callout labels.
    var padR = MOBILE.matches ? PAD + 0.07 : PAD;
    proj.fitWidth(w * (1 - PAD - padR), box);
    var b = d3.geoPath(proj).bounds(box);
    var innerH = b[1][1] - b[0][1];
    var h = Math.round(innerH / (1 - 2 * PAD));
    proj.fitExtent([[w * PAD, h * PAD], [w * (1 - padR), h * (1 - PAD)]], box);
    S.w = w; S.h = h;
    S.projection = proj;
    S.path = d3.geoPath(proj);
    S.svg.attr("viewBox", "0 0 " + w + " " + h).attr("width", null).attr("height", null);
    frame.style.aspectRatio = w + " / " + h;
    S.zoom.extent([[0, 0], [w, h]]).translateExtent([[-w * 0.1, -h * 0.1], [w * 1.1, h * 1.1]]);
    S.transform = d3.zoomIdentity;
    S.svg.interrupt().property("__zoom", S.transform);
    S.gGeo.attr("transform", null);
    if (MOBILE.matches) S.svg.on(".zoom", null);
    else S.svg.call(S.zoom).on("dblclick.zoom", null);
    drawGeo();
    S.zoomedTo = null;
  }

  function drawGeo() {
    var g = S.gGeo;
    g.selectAll("*").remove();
    g.append("path").attr("class", "graticule").attr("d", S.path(d3.geoGraticule().step([5, 5])()));
    // Engraved water lines: concentric coastline strokes, widest first, alternating ink and sea.
    var water = g.append("g").attr("class", "water");
    [16, 12, 8, 4].forEach(function (wd, i) {
      water.append("path").attr("class", "wl wl-" + i).attr("d", S.path(S.land)).style("stroke-width", wd);
    });
    g.append("path").attr("class", "land").attr("d", S.path(S.land));
    var arab = S.arab;
    var others = S.all.filter(function (f) { return !arab[f.id]; });
    g.append("path").attr("class", "borders-foreign").attr("d", S.path({ type: "FeatureCollection", features: others }));
    var ctry = g.append("g").attr("class", "countries");
    ctry.selectAll("path").data(S.all.filter(function (f) { return arab[f.id]; }), function (f) { return f.id; })
      .join("path")
      .attr("class", function (f) { var a = arab[f.id]; return "ctry " + (a.listed ? "listed" : "unlisted"); })
      .attr("data-code", function (f) { return arab[f.id].code; })
      .attr("d", S.path)
      .on("pointerenter", function (ev, f) { var a = arab[f.id]; if (a.listed) hover(ev, a.code); else hoverOther(ev, a); })
      .on("pointermove", moveTip)
      .on("pointerleave", function () { unhover(); })
      .on("click", function (ev, f) { var a = arab[f.id]; if (a.listed) select(a.code); else reset(); });
    // Countries too small for 110m geometry render as points.
    var pts = [];
    Object.keys(S.meta.countries).forEach(function (c) { var m = S.meta.countries[c]; if (m.point) pts.push({ code: c, m: m, listed: true }); });
    Object.keys(S.meta.arab_league_other).forEach(function (c) { var m = S.meta.arab_league_other[c]; if (m.point) pts.push({ code: c, m: m, listed: false }); });
    ctry.selectAll("circle.ctry-pt").data(pts).join("circle")
      .attr("class", function (d) { return "ctry ctry-pt " + (d.listed ? "listed" : "unlisted"); })
      .attr("data-code", function (d) { return d.code; })
      .attr("r", 2.4).style("vector-effect", "non-scaling-stroke")
      .attr("cx", function (d) { return S.projection(d.m.lonlat)[0]; })
      .attr("cy", function (d) { return S.projection(d.m.lonlat)[1]; })
      .on("pointerenter", function (ev, d) { if (d.listed) hover(ev, d.code); else hoverOther(ev, { m: d.m }); })
      .on("pointermove", moveTip).on("pointerleave", function () { unhover(); })
      .on("click", function (ev, d) { if (d.listed) select(d.code); });
    var ghosts = Object.keys(S.meta.arab_league_other).map(function (c) { return S.meta.arab_league_other[c]; })
      .filter(function (m) { return !m.nolabel; });
    S.gGhost = S.gMarks.selectAll("text.ghost").data(ghosts).join("text").attr("class", "ghost").attr("lang", "ar")
      .attr("text-anchor", "middle").text(function (m) { return m.ar; });
    g.append("path").attr("class", "borders-arab")
      .attr("d", S.path({ type: "FeatureCollection", features: S.all.filter(function (f) { return arab[f.id]; }) }));
  }

  /* data → drawing */

  function aggregate(entries) {
    var by = {}, intl = {};
    entries.forEach(function (e) {
      var c = e.country || "INTL";
      var bucket = c === "INTL" ? intl : (by[c] = by[c] || {});
      var t = bucket[e.type] = bucket[e.type] || { n: 0, downloads: 0, top: [] };
      t.n++; t.downloads += (e.metrics && e.metrics.downloads) || 0;
    });
    return { by: by, intl: intl };
  }

  function update(d) {
    if (!S.ready) { S.pending = d; return; }
    S.data = d;
    var key = d.entries.length + "|" + d.entries.slice(0, 40).map(function (e) { return e.id; }).join(",") + "|" + d.state.type.join(",");
    var animate = key !== S.lastKey;
    S.lastKey = key;
    draw(animate);
    panel();
    var sel = selected();
    var target = sel && S.meta.countries[sel] ? sel : null;
    if (target !== S.zoomedTo) zoomTo(target, true);
    syncReset();
  }

  function selected() {
    var c = S.data && S.data.state.country;
    return c && c.length === 1 ? c[0] : null;
  }

  function scaleFactor() { return MOBILE.matches ? Math.max(0.42, Math.min(1, S.w / 1100)) : Math.max(0.7, Math.min(1, S.w / 1150)); }

  function draw(animate) {
    var d = S.data;
    var agg = aggregate(d.entries);
    S.agg = agg;
    var codes = Object.keys(S.meta.countries);
    var counts = {}, max = 0, dmax = cellMax(d.entries, false).downloads;
    codes.forEach(function (c) {
      var t = agg.by[c] || {};
      counts[c] = Object.keys(t).reduce(function (s, k) { return s + t[k].n; }, 0);
      max = Math.max(max, counts[c]);
    });
    S.max = max; S.dmax = dmax; S.counts = counts;
    var sel = d.state.country;
    S.gGeo.selectAll(".ctry.listed").each(function () {
      var code = this.getAttribute("data-code");
      var n = counts[code] || 0;
      this.setAttribute("data-step", n ? choroplethStep(n, max) : "none");
      this.classList.toggle("is-selected", sel.indexOf(code) !== -1);
      this.classList.toggle("is-dimmed", sel.length > 0 && sel.indexOf(code) === -1);
    });
    var k = scaleFactor();
    var marks = codes.map(function (c) {
      var m = S.meta.countries[c];
      var ring = bubbleLayout(agg.by[c] || {}, function (t) { return bubbleRadius(t.downloads, dmax) * k; });
      return { code: c, m: m, ring: ring, n: counts[c], ext: ringExtent(ring) };
    });
    var g = S.gMarks.selectAll("g.mark").data(marks, function (x) { return x.code; }).join(function (enter) {
      var gg = enter.append("g").attr("class", "mark").attr("data-code", function (x) { return x.code; });
      gg.append("line").attr("class", "leader");
      gg.append("circle").attr("class", "leader-dot").attr("r", 2.2);
      gg.append("g").attr("class", "ring");
      var lab = gg.append("g").attr("class", "label").attr("tabindex", 0).attr("role", "button");
      lab.append("text").attr("class", "l-ar").attr("lang", "ar");
      lab.append("text").attr("class", "l-en");
      lab.append("text").attr("class", "l-n");
      lab.on("click", function (ev, x) { ev.stopPropagation(); select(x.code); })
        .on("keydown", function (ev, x) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(x.code); } })
        .on("pointerenter", function (ev, x) { hover(ev, x.code); }).on("pointermove", moveTip).on("pointerleave", function () { unhover(); });
      return gg;
    });
    g.classed("is-empty", function (x) { return !x.n; })
      .classed("is-selected", function (x) { return sel.indexOf(x.code) !== -1; })
      .classed("is-dimmed", function (x) { return sel.length > 0 && sel.indexOf(x.code) === -1; })
      .classed("mobile", MOBILE.matches);
    g.each(function (x) {
      var node = d3.select(this);
      var side = x.m.side || "below";
      var off = Math.max(x.ext, 4 * k) + 5;
      var lab = node.select(".label").attr("aria-label", x.m.en + ", " + plural(x.n, "entry", "entries"));
      var fs = MOBILE.matches ? 11 : 15;
      var tx, ty, anchor;
      if (side === "right") { tx = off; ty = -fs * 0.15; anchor = "start"; }
      else if (side === "left") { tx = -off; ty = -fs * 0.15; anchor = "end"; }
      else { tx = 0; ty = off + fs * 0.85; anchor = "middle"; }
      lab.selectAll("text").attr("text-anchor", anchor).attr("x", tx);
      lab.select(".l-ar").attr("y", ty).style("font-size", fs + "px").text(x.m.ar);
      lab.select(".l-en").attr("y", ty + fs * 0.95).text(MOBILE.matches ? "" : x.m.en);
      lab.select(".l-n").attr("y", ty + (MOBILE.matches ? fs * 1.05 : fs * 1.85)).text(x.n ? (MOBILE.matches ? String(x.n) : plural(x.n, "entry", "entries")) : "");
      var b = node.select(".ring").selectAll("circle.bubble").data(x.ring, function (it) { return it.type; });
      b.exit().remove();
      var be = b.enter().append("circle").attr("class", "bubble").attr("r", 0)
        .on("click", function (ev, it) { ev.stopPropagation(); select(x.code, it.type); })
        .on("pointerenter", function (ev, it) { hover(ev, x.code, it.type); })
        .on("pointermove", moveTip).on("pointerleave", function () { unhover(); });
      var all = be.merge(b)
        .attr("cx", function (it) { return it.x; }).attr("cy", function (it) { return it.y; })
        .style("fill", function (it) { return S.opts.colors[it.type]; })
        .attr("data-type", function (it) { return it.type; });
      if (animate && dur(300)) {
        all.attr("r", 0).transition().duration(300).ease(d3.easeCubicOut)
          .delay(function (it, i) { return i * 18; }).attr("r", function (it) { return it.r; });
      } else {
        all.interrupt().attr("r", function (it) { return it.r; });
      }
    });
    placeMarks();
    dock(agg.intl, cellMax(d.entries, true).downloads, animate);
    legend(max, dmax);
  }

  function placeMarks() {
    if (!S.gMarks) return;
    var t = S.transform;
    if (S.gGhost) S.gGhost.attr("transform", function (m) { var p = S.projection(m.lonlat); return "translate(" + t.applyX(p[0]) + "," + t.applyY(p[1]) + ")"; })
      .attr("hidden", MOBILE.matches ? true : null);
    S.gMarks.selectAll("g.mark").each(function (x) {
      var p = S.projection(x.m.lonlat), a = S.projection(x.m.anchor || x.m.lonlat);
      var pt = [t.applyX(p[0]), t.applyY(p[1])];
      // Zoomed in far enough, the callout returns to the country itself.
      var at = x.m.anchor && t.k < 2.2 && !MOBILE.matches ? [t.applyX(a[0]), t.applyY(a[1])] : pt;
      var node = d3.select(this);
      node.select(".ring").attr("transform", "translate(" + at[0] + "," + at[1] + ")");
      node.select(".label").attr("transform", "translate(" + at[0] + "," + at[1] + ")");
      x._at = at;
      var callout = at !== pt;
      node.select(".leader").attr("x1", pt[0]).attr("y1", pt[1]).attr("x2", at[0]).attr("y2", at[1]).attr("hidden", callout ? null : true);
      node.select(".leader-dot").attr("cx", pt[0]).attr("cy", pt[1]).attr("hidden", callout ? null : true);
    });
    declutter();
    var lg = S.opts.stage.querySelector(".legend");
    if (lg) lg.classList.toggle("is-zoomed", t.k > 1.05);
  }

  // Greedy label placement: busiest countries first; a label that would overlap one already
  // placed (or another country's bubbles) is hidden. Matters mostly on phones.
  function declutter() {
    var placed = [];
    var marks = S.gMarks.selectAll("g.mark").nodes().map(function (n) { return { n: n, d: d3.select(n).datum() }; });
    marks.forEach(function (m) {
      var a = m.d._at, e = m.d.ext;
      if (a && e) placed.push({ code: m.d.code, r: { left: a[0] - e, right: a[0] + e, top: a[1] - e, bottom: a[1] + e } });
    });
    marks.sort(function (a, b) { return (b.d.n || 0) - (a.d.n || 0); });
    marks.forEach(function (m) {
      var lab = m.n.querySelector(".label");
      lab.removeAttribute("visibility");
      var bb = lab.getBBox(), a = m.d._at || [0, 0];
      var r = { left: a[0] + bb.x, right: a[0] + bb.x + bb.width, top: a[1] + bb.y, bottom: a[1] + bb.y + bb.height };
      var hit = placed.some(function (p) {
        return p.code !== m.d.code && r.left < p.r.right - 1 && r.right > p.r.left + 1 && r.top < p.r.bottom - 1 && r.bottom > p.r.top + 1;
      });
      if (hit) lab.setAttribute("visibility", "hidden");
      else placed.push({ code: m.d.code, r: r });
    });
  }

  function dock(intl, dmax, animate) {
    var box = S.opts.stage.querySelector(".dock");
    var n = 0, types = TYPE_ORDER.filter(function (t) { return intl[t] && intl[t].n; });
    types.forEach(function (t) { n += intl[t].n; });
    var sel = S.data.state.country;
    box.classList.toggle("is-selected", sel.indexOf("INTL") !== -1);
    box.classList.toggle("is-dimmed", sel.length > 0 && sel.indexOf("INTL") === -1);
    var head = box.querySelector(".dock-head");
    head.textContent = "";
    head.appendChild(el("span", { className: "ar", lang: "ar", dir: "rtl", text: "دولي" }));
    head.appendChild(el("span", { className: "en", text: "International · " + n }));
    head.title = "Built outside the region, or by global teams. Not placed on the map; bubbles use their own scale.";
    head.appendChild(el("span", { className: "dock-note", text: "Own bubble scale, dashed" }));
    var list = box.querySelector(".dock-list");
    list.textContent = "";
    var k = scaleFactor();
    types.forEach(function (t, i) {
      var r = bubbleRadius(intl[t].downloads, dmax) * k;
      var size = 2 * R_MAX * k + 4;
      var svg = d3.create("svg").attr("width", size).attr("height", size).attr("viewBox", [-size / 2, -size / 2, size, size].join(" ")).attr("aria-hidden", "true");
      svg.append("circle").attr("class", "over").attr("r", r + 3);
      var c = svg.append("circle").attr("class", "bubble").style("fill", S.opts.colors[t]).attr("r", animate && dur(300) ? 0 : r);
      if (animate && dur(300)) c.transition().duration(300).delay(i * 18).ease(d3.easeCubicOut).attr("r", r);
      var b = el("button", { type: "button", className: "dock-item", "aria-label": S.opts.typeLabels[t] + ", international, " + intl[t].n + " entries" }, [
        svg.node(),
        el("span", { className: "di-txt" }, [
          el("span", { className: "di-t", text: S.opts.typeLabels[t] }),
          el("span", { className: "di-n", text: intl[t].n + (intl[t].downloads ? ", " + fmt(intl[t].downloads) + " downloads" : "") })
        ])
      ]);
      b.addEventListener("click", function () { select("INTL", t); });
      b.addEventListener("pointerenter", function (ev) { hover(ev, "INTL", t); });
      b.addEventListener("pointermove", moveTip);
      b.addEventListener("pointerleave", unhover);
      list.appendChild(b);
    });
    if (!types.length) list.appendChild(el("span", { className: "dock-none", text: "No international entries match." }));
    var all = el("button", { type: "button", className: "dock-all linkish", text: "List all international" });
    all.addEventListener("click", function () { select("INTL"); });
    if (types.length) list.appendChild(all);
  }

  function legend(max, dmax) {
    var box = S.opts.stage.querySelector(".legend");
    box.textContent = "";
    if (MOBILE.matches) return;
    var steps = el("div", { className: "lg-steps" });
    // Lower bound of each step: smallest count that lands in it.
    var lows = [];
    for (var n = 1; n <= max; n++) { var s = choroplethStep(n, max); if (lows[s] === undefined) lows[s] = n; }
    for (var i = 0; i < 5; i++) {
      var lo = lows[i], hi = lows.slice(i + 1).find(function (v) { return v !== undefined; });
      var label = lo === undefined ? "" : (hi === undefined ? (lo === max ? String(lo) : lo + "–" + max) : (hi - 1 === lo ? String(lo) : lo + "–" + (hi - 1)));
      steps.appendChild(el("span", { className: "lg-step" + (lo === undefined ? " is-void" : ""), "data-step": i }, [el("i"), el("span", { text: label })]));
    }
    box.appendChild(el("p", { className: "lg-h", text: "Entries per country" }));
    box.appendChild(steps);
    box.appendChild(el("p", { className: "lg-hatch" }, [el("i"), "Arab League, nothing listed yet"]));
    box.appendChild(el("p", { className: "lg-h", text: "Bubble area: Hugging Face downloads per type" }));
    var refs = [1e3, Math.pow(10, Math.round(Math.log10(Math.max(dmax, 10)) - 1)), dmax].filter(function (v, i, a) { return v > 0 && v <= dmax && a.indexOf(v) === i; })
      .sort(function (a, b) { return a - b; });
    var k = scaleFactor();
    var svg = d3.create("svg").attr("class", "lg-sizes").attr("aria-hidden", "true");
    var x = 2, base = 2 * R_MAX * k + 2;
    refs.forEach(function (v) {
      var r = bubbleRadius(v, dmax) * k;
      var cx = x + Math.max(r, 14);
      svg.append("circle").attr("cx", cx).attr("cy", base - r).attr("r", r);
      svg.append("text").attr("x", cx).attr("y", base + 12).attr("text-anchor", "middle").text(fmt(v));
      x = cx + Math.max(r, 14) + 8;
    });
    svg.attr("width", x).attr("height", base + 16);
    var row = el("div", { className: "lg-size-row" }, [svg.node()]);
    box.appendChild(row);
  }

  /* panel: the selected country's entries, reusing the app's node rendering */
  function panel() {
    var p = S.opts.stage.querySelector(".map-panel");
    var st = S.data.state;
    if (!st.country.length || MOBILE.matches) { p.hidden = true; S.opts.stage.classList.remove("has-panel"); return; }
    p.hidden = false;
    S.opts.stage.classList.add("has-panel");
    var visible = S.data.visible;
    var head = p.querySelector(".mp-head");
    head.textContent = "";
    var names = st.country.map(function (c) { var m = S.meta.countries[c]; return m ? m : { ar: "دولي", en: "International" }; });
    head.appendChild(el("h2", { className: "mp-title" }, [
      el("span", { className: "ar", lang: "ar", dir: "rtl", text: names.map(function (m) { return m.ar; }).join("، ") }),
      el("span", { className: "en", text: names.map(function (m) { return m.en; }).join(", ") })
    ]));
    head.appendChild(el("p", { className: "mp-n", text: plural(visible.length, "entry matches", "entries match") }));
    var close = el("button", { type: "button", className: "btn small mp-close", "aria-label": "Close the list and zoom out", text: "Close" });
    close.addEventListener("click", function () { reset(); });
    head.appendChild(close);
    var body = p.querySelector(".mp-body");
    body.textContent = "";
    TYPE_ORDER.forEach(function (t) {
      var rows = visible.filter(function (e) { return e.type === t; }).sort(function (a, b) {
        return ((b.metrics && b.metrics.downloads) || 0) - ((a.metrics && a.metrics.downloads) || 0) || a.name.localeCompare(b.name);
      });
      if (!rows.length) return;
      var sec = el("section", { className: "mp-sec" });
      sec.appendChild(el("h3", null, [el("span", { className: "swatch", style: "background:" + S.opts.colors[t] }), S.opts.typeLabels[t], el("span", { className: "n", text: String(rows.length) })]));
      var list = el("div", { className: "nodes" });
      rows.forEach(function (e) { list.appendChild(S.opts.makeNode(e)); });
      sec.appendChild(list);
      body.appendChild(sec);
    });
    if (!visible.length) body.appendChild(el("p", { className: "mp-none", text: "Nothing here matches the current filters. Clear a chip or the search to see more." }));
  }

  /* zoom */
  function zoomTo(code, smooth) {
    S.zoomedTo = code;
    if (MOBILE.matches || !S.svg) return;
    var t = d3.zoomIdentity;
    if (code) {
      var m = S.meta.countries[code];
      var b;
      var f = S.features[m.id];
      if (f && !m.point) b = S.path.bounds(f);
      else { var p = S.projection(m.lonlat); b = [[p[0] - 30, p[1] - 30], [p[0] + 30, p[1] + 30]]; }
      var panelW = S.opts.stage.classList.contains("has-panel") ? Math.min(380, S.w * 0.34) : 0;
      var aw = S.w - panelW, ah = S.h;
      var dx = b[1][0] - b[0][0], dy = b[1][1] - b[0][1];
      var k = Math.max(1, Math.min(8, 0.62 / Math.max(dx / aw, dy / ah)));
      var cx = (b[0][0] + b[1][0]) / 2, cy = (b[0][1] + b[1][1]) / 2;
      t = d3.zoomIdentity.translate(aw / 2, ah / 2).scale(k).translate(-cx, -cy);
    }
    if (smooth && dur(750)) S.svg.transition().duration(750).ease(d3.easeCubicInOut).call(S.zoom.transform, t);
    else S.svg.interrupt().call(S.zoom.transform, t);
  }

  // Ocean click, Esc, "Reset view": zoom out and clear the country.
  function reset() {
    if (!S.data || !S.data.state.country.length) { zoomTo(null, true); syncReset(); }
    S.opts.onReset();
  }

  function syncReset() {
    if (!S.data) return;
    S.opts.stage.querySelector(".map-reset").hidden = S.transform.k < 1.01 && Math.abs(S.transform.x) < 1 && Math.abs(S.transform.y) < 1 && !S.data.state.country.length;
  }

  function select(code, type) { S.opts.onSelect(code, type || null); }

  /* tooltip */
  function tip() { return S.opts.stage.querySelector(".map-tip"); }
  function hoverOther(ev, a) {
    if (ev.pointerType === "touch" || !a.m.en) return;
    var t = tip();
    t.textContent = "";
    t.appendChild(el("p", { className: "tt-name" }, [el("span", { className: "ar", lang: "ar", dir: "rtl", text: a.m.ar }), el("span", { className: "en", text: a.m.en })]));
    t.appendChild(el("p", { className: "tt-note", text: "Nothing listed from here yet. Know a project? Add it on GitHub." }));
    t.hidden = false;
    moveTip(ev);
  }
  function hover(ev, code, type) {
    S.gGeo.selectAll(".ctry").classed("is-hover", function () { return this.getAttribute("data-code") === code; });
    S.gMarks.selectAll("g.mark").classed("is-hover", function (x) { return x.code === code; });
    if (ev.pointerType === "touch") return;
    var t = tip();
    var m = code === "INTL" ? { ar: "دولي", en: "International" } : S.meta.countries[code];
    var rows = S.data.entries.filter(function (e) { return (e.country || "INTL") === code && (!type || e.type === type); });
    var byType = {};
    rows.forEach(function (e) { byType[e.type] = (byType[e.type] || 0) + 1; });
    t.textContent = "";
    t.appendChild(el("p", { className: "tt-name" }, [el("span", { className: "ar", lang: "ar", dir: "rtl", text: m.ar }), el("span", { className: "en", text: m.en + (type ? ", " + S.opts.typeLabels[type] : "") })]));
    t.appendChild(el("p", { className: "tt-n", text: plural(rows.length, "entry", "entries") }));
    var dl = el("ul", { className: "tt-types" });
    TYPE_ORDER.forEach(function (ty) {
      if (!byType[ty]) return;
      dl.appendChild(el("li", null, [el("span", { className: "swatch", style: "background:" + S.opts.colors[ty] }), el("span", { text: S.opts.typeLabels[ty] }), el("span", { className: "n", text: String(byType[ty]) })]));
    });
    if (rows.length) t.appendChild(dl);
    var top = rows.filter(function (e) { return e.metrics && e.metrics.downloads; })
      .sort(function (a, b) { return b.metrics.downloads - a.metrics.downloads; }).slice(0, 3);
    if (top.length) {
      t.appendChild(el("p", { className: "tt-h", text: "Most downloaded" }));
      var ol = el("ol", { className: "tt-top" });
      top.forEach(function (e) { ol.appendChild(el("li", null, [el("span", { dir: "auto", text: e.name }), el("span", { className: "n", text: fmt(e.metrics.downloads) })])); });
      t.appendChild(ol);
    }
    t.appendChild(el("p", { className: "tt-hint", text: type ? "Click to list these" : "Click to zoom in and list them" }));
    t.hidden = false;
    moveTip(ev);
  }
  function moveTip(ev) {
    var t = tip();
    if (t.hidden || !ev.clientX) return;
    var host = S.opts.stage.getBoundingClientRect();
    var x = ev.clientX - host.left + 16, y = ev.clientY - host.top + 16;
    var tw = t.offsetWidth, th = t.offsetHeight;
    if (x + tw > host.width - 8) x = ev.clientX - host.left - tw - 16;
    if (y + th > host.height - 8) y = Math.max(8, ev.clientY - host.top - th - 16);
    t.style.transform = "translate(" + Math.max(8, x) + "px," + y + "px)";
  }
  function unhover() {
    tip().hidden = true;
    S.gGeo.selectAll(".ctry.is-hover").classed("is-hover", false);
    S.gMarks.selectAll("g.mark.is-hover").classed("is-hover", false);
  }

  window.AtlasMap = { init: init, update: update, reset: function () { if (S.ready) reset(); }, api: api, isReady: function () { return S.ready; } };
})();
