/* Arabic AI Atlas: the family tree view. d3 (vendored) for layout and pan/zoom.
 * buildHierarchy() is pure and exported for Node tests; the DOM part registers window.AtlasTree
 * and is driven by app.js, which passes the visible entry ids so filters dim, never remove. */
(function () {
  "use strict";

  /* ---------- pure helpers ---------- */

  function downloads(e) { return (e && e.metrics && e.metrics.downloads) || 0; }
  function shortId(id) { var s = String(id), i = s.lastIndexOf("/"); return i === -1 ? s : s.slice(i + 1); }
  var HF = "https://huggingface.co/";
  function hfUrl(id) { return HF + String(id).split("/").map(encodeURIComponent).join("/"); }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }

  // Downloads desc, then name; an external base ranks by the busiest entry beneath it.
  function byRank(a, b) {
    return b.rank - a.rank || a.name.toLowerCase().localeCompare(b.name.toLowerCase()) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  }

  // lineage = {roots: [{id, label, label_ar, count}], edges: [[parent, child]], root_of: {id: rootId}}.
  // Returns {id: "root", children: [family...]} in lineage.roots order. Inside a family, atlas entries
  // nest under atlas parents of the same family; parents outside the atlas (Hugging Face ids) become
  // intermediate nodes with `external: true`. Every atlas id appears at most once (a visited set
  // breaks cycles and picks one parent for multi-parent entries); anything unreachable hangs off the family.
  function buildHierarchy(lineage, entries) {
    lineage = lineage || {};
    var roots = lineage.roots || [], edges = lineage.edges || [], rootOf = lineage.root_of || {};
    var byId = {}, rootIds = {}, kidsOf = {}, parentsOf = {}, visited = {};
    (entries || []).forEach(function (e) { if (e && e.id) byId[e.id] = e; });
    roots.forEach(function (r) { rootIds[r.id] = true; });
    edges.forEach(function (pc) {
      (kidsOf[pc[0]] = kidsOf[pc[0]] || []).push(pc[1]);
      (parentsOf[pc[1]] = parentsOf[pc[1]] || []).push(pc[0]);
    });
    function inAtlas(id) { return has(rootOf, id) || has(byId, id); }
    // "same": atlas parent in this family; "ext": outside the atlas; null: the family root or another family.
    function parentKind(p, fam) {
      if (inAtlas(p)) return rootOf[p] === fam ? "same" : null;
      return rootIds[p] ? null : "ext";
    }
    function finish(n) {
      n.children.sort(byRank);
      n.children.forEach(function (c) { n.rank = Math.max(n.rank, c.rank); });
      return n;
    }
    function entryNode(id, fam) {
      visited[id] = true;
      var e = byId[id] || {};
      var n = { id: id, name: e.name || id, type: e.type || null, downloads: downloads(e), rank: downloads(e), entry: byId[id] || null, children: [] };
      (kidsOf[id] || []).slice().sort().forEach(function (c) {
        if (!visited[c] && rootOf[c] === fam) n.children.push(entryNode(c, fam));
      });
      return finish(n);
    }

    var families = roots.map(function (r) {
      var fam = { id: r.id, label: r.label || r.id, label_ar: r.label_ar || "", count: r.count || 0, family: true, name: r.label || r.id, rank: 0, children: [] };
      var members = Object.keys(rootOf).filter(function (id) { return rootOf[id] === r.id; }).sort();
      var top = [], ext = {};
      members.forEach(function (id) {
        var kinds = (parentsOf[id] || []).map(function (p) { return { p: p, k: parentKind(p, r.id) }; });
        kinds.forEach(function (x) { if (x.k === "ext") ext[x.p] = true; });
        if (!kinds.some(function (x) { return x.k; })) top.push(id);
      });
      top.forEach(function (id) { if (!visited[id]) fam.children.push(entryNode(id, r.id)); });
      Object.keys(ext).sort().forEach(function (p) {
        var n = { id: p, name: shortId(p), external: true, url: hfUrl(p), downloads: 0, rank: 0, children: [] };
        (kidsOf[p] || []).slice().sort().forEach(function (c) {
          if (!visited[c] && rootOf[c] === r.id) n.children.push(entryNode(c, r.id));
        });
        if (n.children.length) fam.children.push(finish(n));
      });
      // Two bases with the same short name (qwen/x and unsloth/x): spell out the full id.
      var seen = {};
      fam.children.forEach(function (c) { if (c.external) seen[c.name] = (seen[c.name] || 0) + 1; });
      fam.children.forEach(function (c) { if (c.external && seen[c.name] > 1) c.name = c.id; });
      // Whatever is left sits on a cycle: hang it off the family root.
      members.forEach(function (id) { if (!visited[id]) fam.children.push(entryNode(id, r.id)); });
      return finish(fam);
    });
    return { id: "root", children: families };
  }

  var api = { buildHierarchy: buildHierarchy, shortId: shortId, hfUrl: hfUrl };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  if (typeof document === "undefined") return;

  /* ---------- DOM ---------- */

  var d3 = window.d3;
  var SVGNS = d3.namespaces.svg;
  var MOBILE = window.matchMedia ? window.matchMedia("(max-width: 899px)") : { matches: false };
  var REDUCED = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };
  var ROW = 22, COL = 232, FAMILY_GAP = 34, PAD = 28;       // desktop: horizontal tree
  var M_ROW = 30, M_INDENT = 16, M_PAD = 12;                 // phones: top-down outline
  var BIG_FAMILY = 40, CLICK_DELAY = 230;
  var FONT = '"IBM Plex Sans Arabic", "Noto Sans Arabic", "Segoe UI", Tahoma, system-ui, sans-serif';

  var S = {
    opts: null, families: [], collapsed: {}, visible: null, filtering: false, total: 0,
    svg: null, gView: null, gBands: null, gLinks: null, gNodes: null, zoom: null, home: null,
    width: 0, height: 0, mobile: null, clickTimer: null, measure: null
  };

  function dur(ms) { return REDUCED.matches ? 0 : ms; }
  function trans(sel, ms) { return dur(ms) ? sel.transition().duration(ms).ease(d3.easeCubicOut) : sel; }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

  function textWidth(text, size, weight) {
    if (!S.measure) S.measure = document.createElement("canvas").getContext("2d");
    S.measure.font = (weight || 400) + " " + size + "px " + FONT;
    return S.measure.measureText(text).width;
  }
  function fit(text, max, size, weight) {
    if (textWidth(text, size, weight) <= max) return text;
    var lo = 1, hi = text.length;
    while (lo < hi) {
      var mid = (lo + hi + 1) >> 1;
      if (textWidth(text.slice(0, mid) + "\u2026", size, weight) <= max) lo = mid; else hi = mid - 1;
    }
    return text.slice(0, lo).replace(/[\s._-]+$/, "") + "\u2026";
  }

  // Give each raw node a stable key and a descendant count; fold the busiest families to depth 1.
  function prepare(raw) {
    var fams = raw.children.slice();
    // "Other" is the miscellany: it reads better after the named families.
    fams.sort(function (a, b) { return (a.id === "other") - (b.id === "other"); });
    function walk(n, key, depth, parent) {
      n.key = key; n.depth = depth; n.parent = parent; n.desc = 0;
      n.children.forEach(function (c) { walk(c, key + ">" + c.id, depth + 1, n); n.desc += 1 + c.desc; });
    }
    fams.forEach(function (f) {
      walk(f, f.id, 0, null);
      if (f.desc > BIG_FAMILY) f.children.forEach(function (c) { if (c.children.length) S.collapsed[c.key] = true; });
    });
    return fams;
  }

  function isMatch(n) {
    if (!S.filtering) return true;
    if (n.entry) return !!S.visible[n.id];
    return n.matches > 0;
  }
  function countMatches(n) {
    var m = 0;
    n.children.forEach(function (c) { m += countMatches(c) + (c.entry && S.visible[c.id] ? 1 : 0); });
    n.matches = m;
    return m;
  }

  function init(opts) {
    S.opts = opts;
    S.total = (opts.entries || []).length;
    S.families = prepare(buildHierarchy(opts.lineage, opts.entries));
    var stage = opts.stage;
    var svgNode = stage.querySelector("svg.tree");
    S.svg = d3.select(svgNode);
    S.svg.selectAll("*").remove();
    S.gView = S.svg.append("g").attr("class", "tree-view");
    S.gBands = S.gView.append("g").attr("class", "bands");
    S.gLinks = S.gView.append("g").attr("class", "links");
    S.gNodes = S.gView.append("g").attr("class", "tnodes");
    S.home = d3.zoomIdentity.translate(PAD, PAD);
    S.zoom = d3.zoom().scaleExtent([0.5, 4])
      // Plain wheel scrolls the tree; ctrl/cmd + wheel (and trackpad pinch) zooms.
      .filter(function (ev) { return ev.type === "wheel" ? (ev.ctrlKey || ev.metaKey) : (!ev.ctrlKey && !ev.button); })
      .on("zoom", function (ev) { S.gView.attr("transform", ev.transform); syncReset(); });
    svgNode.addEventListener("wheel", function (ev) {
      if (S.mobile || ev.ctrlKey || ev.metaKey) return;
      var before = d3.zoomTransform(svgNode);
      S.zoom.translateBy(S.svg, -ev.deltaX / before.k, -ev.deltaY / before.k);
      var after = d3.zoomTransform(svgNode);
      if (after.x !== before.x || after.y !== before.y) ev.preventDefault(); // at the edge the page scrolls on
    }, { passive: false });
    stage.querySelector(".tree-reset").addEventListener("click", function () {
      trans(S.svg, 450).call(S.zoom.transform, S.home);
    });
    (MOBILE.addEventListener ? MOBILE.addEventListener.bind(MOBILE, "change") : MOBILE.addListener.bind(MOBILE))(function () {
      if (!stage.hidden) draw(true);
    });
    var ro = new ResizeObserver(function () {
      var w = Math.round(svgNode.parentNode.clientWidth);
      if (w && Math.abs(w - S.width) > 1 && !stage.hidden) draw(false);
    });
    ro.observe(svgNode.parentNode);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!stage.hidden) draw(false); });
  }

  function render(visibleIds) {
    if (!S.opts) return;
    var ids = visibleIds || [];
    S.visible = {};
    ids.forEach(function (id) { S.visible[id] = true; });
    S.filtering = !!visibleIds && ids.length < S.total;
    S.families.forEach(countMatches);
    draw(false);
  }

  /* layout: returns {nodes: [{n, x, y, kids}], links: [{s, t}], bands: [y], w, h} */
  function visibleKids(n) { return S.collapsed[n.key] ? [] : n.children; }

  function layoutDesktop() {
    var out = { nodes: [], links: [], bands: [], w: 0, h: 0 }, top = 0, maxDepth = 0;
    var tree = d3.tree().nodeSize([ROW, COL]).separation(function (a, b) { return a.parent === b.parent ? 1 : 1.3; });
    S.families.forEach(function (f, i) {
      var h = tree(d3.hierarchy(f, function (n) { var k = visibleKids(n); return k.length ? k : null; }));
      var minX = Infinity, maxX = -Infinity;
      h.each(function (d) { minX = Math.min(minX, d.x); maxX = Math.max(maxX, d.x); maxDepth = Math.max(maxDepth, d.depth); });
      if (i) { out.bands.push(top - FAMILY_GAP / 2); }
      var pos = {};
      h.each(function (d) {
        var p = { n: d.data, x: d.depth * COL, y: top + d.x - minX, depth: d.depth };
        pos[d.data.key] = p;
        out.nodes.push(p);
        if (d.parent) out.links.push({ s: pos[d.parent.data.key], t: p });
      });
      top += maxX - minX + FAMILY_GAP;
    });
    out.w = (maxDepth + 1) * COL;
    out.h = top - FAMILY_GAP;
    return out;
  }

  function layoutMobile() {
    var out = { nodes: [], links: [], bands: [], w: S.width, h: 0 }, top = 0;
    S.families.forEach(function (f, i) {
      if (i) { out.bands.push(top - M_ROW / 2 + 2); top += 6; }
      var pos = {};
      (function walk(n, depth, parentPos) {
        var p = { n: n, x: M_PAD + depth * M_INDENT, y: top, depth: depth };
        top += M_ROW;
        pos[n.key] = p;
        out.nodes.push(p);
        if (parentPos) out.links.push({ s: parentPos, t: p });
        visibleKids(n).forEach(function (c) { walk(c, depth + 1, p); });
      })(f, 0, null);
    });
    out.h = top - M_ROW + 14;
    return out;
  }

  function radius(n) {
    if (n.family) return 6;
    if (n.external) return 4.5;
    return 3 + 5 * window.Atlas.sizeScore(n.downloads);
  }

  // Label pieces for a node: [{text, cls, lang}], plus its width, fitted to `max` pixels.
  function labelParts(n, max) {
    var hidden = S.collapsed[n.key] ? n.desc : 0;
    var badge = "";
    if (hidden) badge = "+" + hidden + (S.filtering && n.matches ? " (" + n.matches + " match)" : "");
    var badgeW = badge ? textWidth(badge, 11, 600) + 8 : 0;
    if (n.family) {
      var tail = String(n.count || n.desc);
      var fixed = textWidth(" · " + n.label_ar + "  " + tail, 14, 600) + badgeW;
      var parts = [
        { text: fit(n.label, Math.max(40, max - fixed), 14, 600), cls: "l-en" },
        { text: " · ", cls: "l-sep" },
        { text: n.label_ar, cls: "l-ar", lang: "ar" },
        { text: "\u200E\u2002" + tail, cls: "l-n" }
      ];
      if (badge) parts.push({ text: "\u2002" + badge, cls: "l-badge" });
      return parts;
    }
    var parts2 = [{ text: fit(n.name, Math.max(30, max - badgeW), 12, n.external ? 400 : 500), cls: "l-name" }];
    if (badge) parts2.push({ text: "\u2002" + badge, cls: "l-badge" });
    return parts2;
  }
  function partsWidth(n, parts) {
    return parts.reduce(function (w, p) {
      var size = n.family ? (p.cls === "l-badge" ? 11 : 14) : (p.cls === "l-badge" ? 11 : 12);
      return w + textWidth(p.text, size, n.family || p.cls === "l-badge" ? 600 : 500);
    }, 0);
  }

  function draw(resetView) {
    if (!S.svg) return;
    var frame = S.svg.node().parentNode;
    var mobile = MOBILE.matches;
    var modeChanged = mobile !== S.mobile;
    S.mobile = mobile;
    S.width = Math.round(frame.clientWidth) || 800;
    var L = mobile ? layoutMobile() : layoutDesktop();

    L.nodes.forEach(function (p) {
      var r = radius(p.n);
      var max = mobile ? S.width - p.x - r - 18 : COL - r - 30;
      p.r = r;
      p.parts = labelParts(p.n, max);
      p.lw = partsWidth(p.n, p.parts);
    });

    if (mobile) {
      S.svg.on(".zoom", null).attr("width", S.width).attr("height", L.h).attr("viewBox", null);
      S.svg.property("__zoom", d3.zoomIdentity);
      S.gView.attr("transform", "translate(0," + (M_ROW / 2 + 4) + ")");
    } else {
      S.svg.attr("width", null).attr("height", null);
      S.zoom.extent([[0, 0], [S.width, frame.clientHeight || 600]])
        .translateExtent([[-PAD * 4, -PAD * 2], [Math.max(L.w + PAD * 6, S.width / 0.5), L.h + PAD * 4]]);
      S.svg.call(S.zoom).on("dblclick.zoom", null);
      if (modeChanged || resetView) S.svg.call(S.zoom.transform, S.home);
    }

    // family separators
    var bands = S.gBands.selectAll("line").data(L.bands);
    bands.exit().remove();
    bands.enter().append("line").merge(bands)
      .attr("x1", mobile ? 0 : -PAD).attr("x2", mobile ? S.width : L.w + PAD)
      .attr("y1", function (y) { return y; }).attr("y2", function (y) { return y; });

    var animate = !modeChanged;
    // links: desktop curves start past the parent's label; phones use elbows from the parent's dot
    function linkPath(l) {
      if (mobile) return "M" + l.s.x + "," + (l.s.y + l.s.r) + "V" + l.t.y + "H" + (l.t.x - l.t.r - 2);
      var sx = Math.min(l.s.x + l.s.r + 6 + l.s.lw + 8, l.t.x - l.t.r - 10), tx = l.t.x - l.t.r - 2, mx = (sx + tx) / 2;
      return "M" + sx + "," + l.s.y + "C" + mx + "," + l.s.y + " " + mx + "," + l.t.y + " " + tx + "," + l.t.y;
    }
    var links = S.gLinks.selectAll("path").data(L.links, function (l) { return l.t.n.key; });
    links.exit().remove();
    var linksIn = links.enter().append("path").attr("d", linkPath).style("opacity", animate ? 0 : null);
    var linksAll = linksIn.merge(links).classed("is-dimmed", function (l) { return !isMatch(l.t.n); });
    trans(linksAll, animate ? 280 : 0).attr("d", linkPath).style("opacity", null);

    var nodes = S.gNodes.selectAll("g.tn").data(L.nodes, function (p) { return p.n.key; });
    nodes.exit().remove();
    var nodesIn = nodes.enter().append("g")
      .attr("tabindex", "0")
      .attr("transform", function (p) { return "translate(" + p.x + "," + p.y + ")"; })
      .style("opacity", animate ? 0 : null)
      .each(function (p) { buildNode(this, p.n); });
    var all = nodesIn.merge(nodes);
    all.attr("class", function (p) {
      var n = p.n;
      return "tn " + (n.family ? "tn-family" : n.external ? "tn-ext" : "tn-entry") +
        (n.children.length ? " has-kids" : "") + (S.collapsed[n.key] ? " is-folded" : "") + (isMatch(n) ? "" : " is-dimmed");
    }).each(function (p) { paintNode(this, p); });
    trans(all, animate ? 280 : 0)
      .attr("transform", function (p) { return "translate(" + p.x + "," + p.y + ")"; })
      .style("opacity", null);
    S.layout = L;
    syncReset();
  }

  function svgEl(tag, attrs) {
    var n = document.createElementNS(SVGNS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  function buildNode(g, n) {
    g.appendChild(svgEl("rect", { class: "tn-hit" }));
    if (n.family) {
      // a survey trig point: triangle with a centre dot
      g.appendChild(svgEl("path", { class: "tn-mark", d: "M0,-7L6.5,4.5H-6.5Z" }));
      g.appendChild(svgEl("circle", { class: "tn-dot", r: 1.6, cy: 0.6 }));
    } else {
      g.appendChild(svgEl("circle", { class: "tn-mark" }));
      if (n.entry) g.querySelector(".tn-mark").style.fill = S.opts.colors[n.type] || "var(--muted)";
    }
    g.appendChild(svgEl("text", { class: "tn-label", dy: "0.34em" }));
    var card = n.entry || (n.external ? externalCard(n) : null);
    if (card) {
      g.addEventListener("mouseenter", function () { S.opts.showCard(card, g, false); });
      g.addEventListener("mouseleave", function () { S.opts.scheduleHide(); });
      g.addEventListener("focus", function () { S.opts.showCard(card, g, true); });
      g.addEventListener("blur", function () { S.opts.scheduleHide(); });
    }
    g.addEventListener("focus", function () { ensureVisible(g); });
    g.addEventListener("click", function (ev) {
      if (ev.detail > 1) return;
      clearTimeout(S.clickTimer);
      if (n.children.length) S.clickTimer = setTimeout(function () { toggle(n); }, CLICK_DELAY);
    });
    g.addEventListener("dblclick", function () { clearTimeout(S.clickTimer); open(n); });
    g.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" || ev.key === " ") {
        ev.preventDefault();
        // Shift+Enter always opens the page; plain Enter folds a parent and opens a leaf.
        if (ev.key === "Enter" && (ev.shiftKey || !n.children.length)) open(n); else if (n.children.length) toggle(n);
      }
    });
  }

  function paintNode(g, p) {
    var n = p.n, r = p.r;
    var mark = g.querySelector(".tn-mark");
    if (!n.family) mark.setAttribute("r", r.toFixed(2));
    var text = g.querySelector(".tn-label");
    text.setAttribute("x", (r + 6).toFixed(1));
    text.textContent = "";
    p.parts.forEach(function (part) {
      var ts = svgEl("tspan", { class: part.cls });
      if (part.lang) ts.setAttribute("lang", part.lang);
      ts.textContent = part.text;
      text.appendChild(ts);
    });
    var hit = g.querySelector(".tn-hit");
    var h = S.mobile ? M_ROW - 4 : ROW - 2;
    hit.setAttribute("x", -r - 4); hit.setAttribute("y", -h / 2);
    hit.setAttribute("width", (r * 2 + 10 + p.lw + 4).toFixed(1)); hit.setAttribute("height", h);
    hit.setAttribute("rx", 4);
    var label = n.family ? n.label + " (" + n.label_ar + "), family of " + plural(n.desc, "model", "models")
      : n.external ? n.id + ", base model outside the atlas, on Hugging Face" : n.name;
    if (n.children.length) {
      label += S.collapsed[n.key] ? ", folded, " + plural(n.desc, "descendant", "descendants") + " hidden" : ", " + plural(n.children.length, "child", "children");
      g.setAttribute("role", "button");
      g.setAttribute("aria-expanded", S.collapsed[n.key] ? "false" : "true");
    } else {
      g.setAttribute("role", n.external || (n.entry && S.opts.primaryLink(n.entry)) ? "link" : "img");
      g.removeAttribute("aria-expanded");
    }
    if (S.filtering && !isMatch(n)) label += ", outside the current filters";
    g.setAttribute("aria-label", label);
  }

  function toggle(n) {
    if (!n.children.length) return;
    if (S.collapsed[n.key]) delete S.collapsed[n.key]; else S.collapsed[n.key] = true;
    S.opts.scheduleHide();
    draw(false);
  }

  // The hover card for a base model outside the atlas: its id, its Hugging Face page, who builds on it.
  function externalCard(n) {
    var owner = n.id.indexOf("/") === -1 ? null : n.id.slice(0, n.id.indexOf("/"));
    return {
      id: n.id, name: n.id, type: "Base model outside the atlas", external: true, org: owner,
      notes: "On Hugging Face at " + n.url.replace(/^https:\/\//, "") + ". " +
        plural(n.desc, "atlas entry builds", "atlas entries build") + " on it.",
      links: { hf: n.url }
    };
  }

  function open(n) {
    var href = n.external ? n.url : n.entry && S.opts.primaryLink(n.entry);
    if (href) window.open(href, "_blank", "noopener");
  }

  // Keyboard focus pans the tree so the focused node is on screen.
  function ensureVisible(g) {
    if (S.mobile || !S.layout) return;
    var p = d3.select(g).datum();
    var frame = S.svg.node().parentNode, w = frame.clientWidth, h = frame.clientHeight;
    var t = d3.zoomTransform(S.svg.node());
    var sx = t.applyX(p.x), sy = t.applyY(p.y);
    if (sx < 20 || sx > w - 160 || sy < 20 || sy > h - 20) {
      S.svg.call(S.zoom.transform, d3.zoomIdentity.translate(Math.min(PAD, w / 3 - p.x * t.k), h / 2 - p.y * t.k).scale(t.k));
    }
  }

  function syncReset() {
    var btn = S.opts && S.opts.stage.querySelector(".tree-reset");
    if (!btn || !S.svg) return;
    var t = d3.zoomTransform(S.svg.node());
    btn.hidden = S.mobile || (Math.abs(t.k - 1) < 0.01 && Math.abs(t.x - S.home.x) < 1 && Math.abs(t.y - S.home.y) < 1);
  }

  window.AtlasTree = { init: init, render: render, api: api };
})();
