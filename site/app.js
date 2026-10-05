/* Arabic AI Atlas: interactive map. Vanilla JS, no build step.
 * The pure part (filtering, hash state, recommend string) is exported for Node tests;
 * everything touching the DOM runs only when `document` exists. */
(function () {
  "use strict";

  var COLORS = {
    llm: "#4F46E5", asr: "#0891B2", tts: "#0E7490", ocr: "#B45309", embedding: "#7C3AED",
    tool: "#475569", benchmark: "#B91C1C", dataset: "#047857", org: "#334155", "agent-skill": "#9D174D", paper: "#6B7280"
  };
  var TYPE_LABELS = {
    llm: "LLM", asr: "ASR", tts: "TTS", ocr: "OCR", embedding: "Embedding", tool: "Tool",
    benchmark: "Benchmark", dataset: "Dataset", org: "Organisation", "agent-skill": "Agent skill", paper: "Paper"
  };
  var TYPE_ORDER = ["llm", "asr", "tts", "ocr", "embedding", "tool", "benchmark", "dataset", "org", "agent-skill", "paper"];
  var COUNTRY_NAMES = {
    SA: "Saudi Arabia", AE: "UAE", EG: "Egypt", QA: "Qatar", MA: "Morocco", JO: "Jordan", TN: "Tunisia",
    LB: "Lebanon", KW: "Kuwait", OM: "Oman", BH: "Bahrain",
    DZ: "Algeria", LY: "Libya", SD: "Sudan", IQ: "Iraq", SY: "Syria", YE: "Yemen", PS: "Palestine", MR: "Mauritania",
    SO: "Somalia", DJ: "Djibouti", KM: "Comoros", INTL: "International"
  };
  var COUNTRY_ORDER = ["SA", "AE", "EG", "QA", "MA", "JO", "TN", "LB", "KW", "OM", "BH",
    "DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM", "INTL"];
  var OTHER = ["JO", "TN", "LB", "KW", "OM", "BH", "DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM"];
  var COLUMNS = [
    { code: "SA", en: "Saudi Arabia", ar: "السعودية" },
    { code: "AE", en: "UAE", ar: "الإمارات" },
    { code: "EG", en: "Egypt", ar: "مصر" },
    { code: "QA", en: "Qatar", ar: "قطر" },
    { code: "MA", en: "Morocco", ar: "المغرب" },
    { code: "OTHER", en: "Jordan, Tunisia +15", ar: "دول أخرى" },
    { code: "INTL", en: "International", ar: "دولي" }
  ];
  var BANDS = [
    { name: "LLMs", ar: "نماذج لغوية", types: ["llm"] },
    { name: "Speech", ar: "الكلام", types: ["asr", "tts"] },
    { name: "Vision", ar: "الرؤية", types: ["ocr"] },
    { name: "Embeddings & Tools", ar: "التضمين والأدوات", types: ["embedding", "tool", "benchmark"] },
    { name: "Datasets", ar: "البيانات", types: ["dataset"] }
  ];
  var DIALECT_LABELS = {
    msa: "MSA", classical: "Classical", egy: "Egyptian", gulf: "Gulf", lev: "Levantine", magh: "Maghrebi",
    iraqi: "Iraqi", yemeni: "Yemeni", sudanese: "Sudanese", mixed: "Mixed"
  };
  var LICENSE_LABELS = { open: "Open", nc: "Non-commercial", unknown: "Unknown" };
  var TASK_FOR_TYPE = { llm: "chat", asr: "asr", tts: "tts", ocr: "ocr", embedding: "embedding",
    dataset: "pretraining", benchmark: "evaluation", tool: "nlp-toolkit", "agent-skill": "agent-skill", org: "research", paper: "survey" };
  var LINK_ORDER = [["hf", "Hugging Face"], ["github", "GitHub"], ["paper", "Paper"], ["website", "Website"]];
  var CELL_LIMIT = 8;

  /* ---------- pure helpers ---------- */

  function licenseClass(license) {
    var l = String(license || "unknown").toLowerCase();
    if (/(^|[-_.\s])nc([-_.\s]|$)/.test(l) || l.indexOf("noncommercial") !== -1 || l.indexOf("non-commercial") !== -1) return "nc";
    if (l === "unknown" || l === "proprietary" || l === "") return "unknown";
    return "open";
  }

  function column(entry) {
    var c = entry.country || "INTL";
    if (OTHER.indexOf(c) !== -1) return "OTHER";
    for (var i = 0; i < COLUMNS.length; i++) if (COLUMNS[i].code === c) return c;
    return "INTL";
  }

  function downloads(entry) { return (entry.metrics && entry.metrics.downloads) || 0; }

  // Case-insensitive, and forgiving of Arabic diacritics, tatweel and alef/yaa/taa-marbuta variants.
  function fold(s) {
    return String(s || "").toLowerCase()
      .replace(/[ً-ْٰـ]/g, "")
      .replace(/[آأإٱ]/g, "ا")
      .replace(/ى/g, "ي")
      .replace(/ة/g, "ه");
  }

  function asList(v) {
    if (v === undefined || v === null || v === "") return [];
    if (Array.isArray(v)) return v.filter(Boolean);
    return String(v).split(",").map(function (x) { return x.trim(); }).filter(Boolean);
  }

  function normalizeState(s) {
    s = s || {};
    return {
      q: String(s.q || "").trim(),
      type: asList(s.type),
      country: asList(s.country),
      dialect: asList(s.dialect),
      license: asList(s.license),
      on_device: s.on_device === true || s.on_device === "1" || s.on_device === "true",
      view: s.view === "grid" || s.view === "tree" ? s.view : "map"
    };
  }

  function matches(e, st) {
    if (st.type.length && st.type.indexOf(e.type) === -1) return false;
    if (st.country.length && st.country.indexOf(e.country || "INTL") === -1) return false;
    if (st.dialect.length) {
      var ds = e.dialects || [];
      if (!st.dialect.some(function (d) { return ds.indexOf(d) !== -1; })) return false;
    }
    if (st.license.length && st.license.indexOf(licenseClass(e.license)) === -1) return false;
    if (st.on_device && e.on_device !== true) return false;
    if (st.q) {
      var hay = fold([e.id, e.name, e.org, e.notes].concat(e.tasks || []).join("\n"));
      var words = fold(st.q).split(/\s+/).filter(Boolean);
      for (var i = 0; i < words.length; i++) if (hay.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function filterEntries(entries, state) {
    var st = normalizeState(state);
    return entries.filter(function (e) { return matches(e, st); });
  }

  function parseHash(hash) {
    var h = String(hash || "").replace(/^#/, "");
    var raw = {};
    h.split("&").forEach(function (pair) {
      if (!pair) return;
      var i = pair.indexOf("=");
      var k = decodeURIComponent(i === -1 ? pair : pair.slice(0, i));
      var v = i === -1 ? "1" : decodeURIComponent(pair.slice(i + 1).replace(/\+/g, " "));
      raw[k] = v;
    });
    return normalizeState(raw);
  }

  function serializeHash(state) {
    var st = normalizeState(state);
    var parts = [];
    if (st.q) parts.push("q=" + encodeURIComponent(st.q));
    ["type", "country", "dialect", "license"].forEach(function (k) {
      if (st[k].length) parts.push(k + "=" + st[k].map(encodeURIComponent).join(","));
    });
    if (st.on_device) parts.push("on_device=1");
    if (st.view !== "map") parts.push("view=" + st.view);
    return parts.length ? "#" + parts.join("&") : "";
  }

  function pyStr(s) { return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"'; }

  function recommendCall(state) {
    var st = normalizeState(state);
    var task = st.q ? st.q.split(/\s+/)[0].toLowerCase()
      : st.type.length === 1 ? TASK_FOR_TYPE[st.type[0]] || st.type[0] : "chat";
    var args = ["task=" + pyStr(task)];
    if (st.type.length === 1) args.push("type=" + pyStr(st.type[0]));
    if (st.dialect.length === 1) args.push("dialect=" + pyStr(st.dialect[0]));
    if (st.on_device) args.push("on_device=True");
    if (st.license.length === 1 && st.license[0] === "open") args.push('license_filter="open"');
    return "recommend(" + args.join(", ") + ")";
  }

  // With a country selected the MCP `search` tool is the one that takes a country.
  function searchCall(state) {
    var st = normalizeState(state);
    var args = ["query=" + pyStr(st.q)];
    if (st.country.length === 1) args.push("country=" + pyStr(st.country[0]));
    if (st.type.length === 1) args.push("type=" + pyStr(st.type[0]));
    return "search(" + args.join(", ") + ")";
  }

  function fmtDownloads(n) {
    if (!n) return "—";
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return Math.floor(n / 1e3) + "K";
    return String(n);
  }

  // 0..1 position on a log scale; 10M downloads and above is the top.
  function sizeScore(n) { return Math.min(Math.log10((n || 0) + 1) / 7, 1); }

  // Split the "wanted" list from atlas.json into open gaps (link = the filters that show the gap)
  // and recently filled ones (link = the entry that filled it). Pure; tolerates a missing list.
  function wantedRows(wanted) {
    var out = { open: [], recent: [] };
    (Array.isArray(wanted) ? wanted : []).forEach(function (w) {
      if (!w || !w.id) return;
      var base = { id: w.id, title: w.title || w.id, why: w.why || "" };
      if (w.status === "open") {
        out.open.push(Object.assign(base, { href: w.hash || "#" }));
      } else if (w.recent) {
        var by = (w.by || [])[0];
        out.recent.push(Object.assign(base, { href: by ? "#q=" + encodeURIComponent(by) : "#", filled_on: w.filled_on || "" }));
      }
    });
    return out;
  }

  var api = {
    wantedRows: wantedRows,
    COLUMNS: COLUMNS, BANDS: BANDS, COLORS: COLORS, licenseClass: licenseClass, column: column, fold: fold,
    normalizeState: normalizeState, matches: matches, filterEntries: filterEntries, filter: filterEntries,
    parseHash: parseHash, serializeHash: serializeHash, recommendCall: recommendCall, searchCall: searchCall,
    sizeScore: sizeScore
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.Atlas = api;
  if (typeof document === "undefined") return;

  /* ---------- DOM ---------- */

  var ENTRIES = [];
  var STATE = normalizeState({});
  var EXPANDED = {};
  var DATA_BASE = "./dist/";
  var $ = function (id) { return document.getElementById(id); };

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] === null || attrs[k] === undefined || attrs[k] === false) continue;
      if (k === "text") n.textContent = attrs[k];
      else if (k === "className") n.className = attrs[k];
      else n.setAttribute(k, attrs[k] === true ? "" : attrs[k]);
    }
    (children || []).forEach(function (c) { if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }

  function primaryLink(e) {
    var l = e.links || {};
    for (var i = 0; i < LINK_ORDER.length; i++) if (l[LINK_ORDER[i][0]]) return l[LINK_ORDER[i][0]];
    return null;
  }

  function byDownloads(a, b) {
    return downloads(b) - downloads(a) || a.name.toLowerCase().localeCompare(b.name.toLowerCase());
  }

  function loadData() {
    var tries = ["./dist/atlas.json", "../dist/atlas.json"];
    function attempt(i) {
      if (i >= tries.length) return Promise.reject(new Error("no data"));
      return fetch(tries[i]).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        DATA_BASE = tries[i].replace("atlas.json", "");
        return r.json();
      }).catch(function () { return attempt(i + 1); });
    }
    return attempt(0);
  }

  /* chips */
  function buildChips(groupId, key, options) {
    var box = $(groupId);
    box.textContent = "";
    options.forEach(function (o) {
      var b = el("button", { type: "button", className: "chip", "data-key": key, "data-value": o.value, "aria-pressed": "false" }, []);
      if (o.color) b.appendChild(el("span", { className: "swatch", style: "background:" + o.color, "aria-hidden": "true" }));
      b.appendChild(el("span", { className: "chip-label", text: o.label }));
      b.appendChild(el("span", { className: "chip-n" }));
      b.addEventListener("click", function () {
        var list = STATE[key].slice();
        var i = list.indexOf(o.value);
        if (i === -1) list.push(o.value); else list.splice(i, 1);
        STATE[key] = list;
        commit();
      });
      box.appendChild(b);
    });
  }

  function countBy(list, fn) {
    var m = {};
    list.forEach(function (e) { [].concat(fn(e)).forEach(function (k) { m[k] = (m[k] || 0) + 1; }); });
    return m;
  }

  function setupChips() {
    var types = countBy(ENTRIES, function (e) { return e.type; });
    buildChips("chips-type", "type", TYPE_ORDER.filter(function (t) { return types[t]; }).map(function (t) {
      return { value: t, label: TYPE_LABELS[t], color: COLORS[t] };
    }));
    var countries = countBy(ENTRIES, function (e) { return e.country || "INTL"; });
    buildChips("chips-country", "country", COUNTRY_ORDER.filter(function (c) { return countries[c]; }).map(function (c) {
      return { value: c, label: COUNTRY_NAMES[c] };
    }));
    var dialects = countBy(ENTRIES, function (e) { return e.dialects || []; });
    buildChips("chips-dialect", "dialect", Object.keys(dialects).sort(function (a, b) { return dialects[b] - dialects[a]; }).map(function (d) {
      return { value: d, label: DIALECT_LABELS[d] || d };
    }));
    buildChips("chips-license", "license", ["open", "nc", "unknown"].map(function (c) {
      return { value: c, label: LICENSE_LABELS[c] };
    }));
  }

  // Facet count for one chip: matches with every other filter applied, this facet swapped for the chip's value.
  function syncChips() {
    document.querySelectorAll(".chip").forEach(function (b) {
      var key = b.getAttribute("data-key"), val = b.getAttribute("data-value");
      var on = STATE[key].indexOf(val) !== -1;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      var st = {}; for (var k in STATE) st[k] = STATE[k];
      st[key] = [val];
      var n = 0;
      for (var i = 0; i < ENTRIES.length; i++) if (matches(ENTRIES[i], st)) n++;
      b.querySelector(".chip-n").textContent = n;
      b.classList.toggle("empty", n === 0 && !on);
    });
    $("q").value !== STATE.q && ($("q").value = STATE.q);
    $("on-device").checked = STATE.on_device;
  }

  /* nodes */
  function node(e) {
    var s = sizeScore(downloads(e));
    var href = primaryLink(e);
    var a = el(href ? "a" : "span", {
      className: "node t-" + e.type, href: href, dir: "auto", tabindex: href ? null : "0",
      "data-id": e.id, style: "--s:" + s.toFixed(3) + ";--c:" + COLORS[e.type],
      "aria-describedby": "card", rel: href ? "noopener" : null, target: null
    }, [e.name]);
    a.addEventListener("mouseenter", function () { showCard(e, a, false); });
    a.addEventListener("mouseleave", scheduleHide);
    a.addEventListener("focus", function () { showCard(e, a, true); });
    a.addEventListener("blur", scheduleHide);
    return a;
  }

  function renderGrid(visible) {
    var grid = $("grid");
    grid.textContent = "";
    var gridTypes = {};
    BANDS.forEach(function (b) { b.types.forEach(function (t) { gridTypes[t] = true; }); });
    var inGrid = visible.filter(function (e) { return gridTypes[e.type]; });
    var colCount = countBy(inGrid, column);

    var head = el("div", { className: "plate-head", role: "presentation" }, [el("div", { className: "corner" })]);
    COLUMNS.forEach(function (c) {
      head.appendChild(el("div", { className: "colhead c-" + c.code }, [
        el("span", { className: "ar", lang: "ar", dir: "rtl", text: c.ar }),
        el("span", { className: "en", text: c.en }),
        el("span", { className: "n", text: String(colCount[c.code] || 0) })
      ]));
    });
    grid.appendChild(head);

    BANDS.forEach(function (band) {
      var rows = inGrid.filter(function (e) { return band.types.indexOf(e.type) !== -1; });
      var sec = el("section", { className: "band", "aria-label": band.name + ", " + rows.length + " entries" });
      sec.appendChild(el("h2", { className: "bandhead" }, [
        el("span", { className: "en", text: band.name }),
        el("span", { className: "ar", lang: "ar", dir: "rtl", text: band.ar }),
        el("span", { className: "n", text: rows.length + (rows.length === 1 ? " entry" : " entries") }),
        el("span", { className: "keys" }, band.types.map(function (t) {
          return el("span", { className: "key" }, [el("span", { className: "swatch", style: "background:" + COLORS[t] }), TYPE_LABELS[t]]);
        }))
      ]));
      COLUMNS.forEach(function (c) {
        var cellEntries = rows.filter(function (e) { return column(e) === c.code; }).sort(byDownloads);
        var key = band.name + "|" + c.code;
        var cell = el("div", { className: "cell c-" + c.code + (cellEntries.length ? "" : " is-empty") });
        cell.appendChild(el("h3", { className: "cellhead" }, [
          el("span", { className: "en", text: c.en }),
          el("span", { className: "ar", lang: "ar", dir: "rtl", text: c.ar }),
          el("span", { className: "n", text: String(cellEntries.length) })
        ]));
        var list = el("div", { className: "nodes" });
        var limit = EXPANDED[key] ? cellEntries.length : CELL_LIMIT;
        cellEntries.slice(0, limit).forEach(function (e) { list.appendChild(node(e)); });
        if (cellEntries.length > limit) {
          var more = el("button", { type: "button", className: "more", text: "Show " + (cellEntries.length - limit) + " more" });
          more.addEventListener("click", function () { EXPANDED[key] = true; render(); focusFirstNew(key, limit); });
          list.appendChild(more);
        } else if (EXPANDED[key] && cellEntries.length > CELL_LIMIT) {
          var less = el("button", { type: "button", className: "more", text: "Show fewer" });
          less.addEventListener("click", function () { EXPANDED[key] = false; render(); });
          list.appendChild(less);
        }
        if (!cellEntries.length) list.appendChild(el("span", { className: "none", "aria-hidden": "true", text: "·" }));
        cell.setAttribute("data-key", key);
        cell.appendChild(list);
        sec.appendChild(cell);
      });
      grid.appendChild(sec);
    });
  }

  function focusFirstNew(key, index) {
    var cell = document.querySelector('.cell[data-key="' + key.replace(/"/g, '\\"') + '"]');
    var nodes = cell ? cell.querySelectorAll(".node") : [];
    if (nodes[index]) nodes[index].focus();
  }

  function renderRoster(sectionId, listId, countId, entries) {
    var list = $(listId);
    list.textContent = "";
    entries.sort(function (a, b) { return a.name.toLowerCase().localeCompare(b.name.toLowerCase()); }).forEach(function (e) {
      var li = el("li", null, [node(e), el("span", { className: "where", text: COUNTRY_NAMES[e.country || "INTL"] || e.country })]);
      list.appendChild(li);
    });
    $(countId).textContent = String(entries.length);
    $(sectionId).hidden = entries.length === 0;
  }

  // Papers are literature, not located artifacts: a list sorted by year, never on the map or grid.
  function renderPapers(entries) {
    var list = $("papers-list");
    list.textContent = "";
    entries.sort(function (a, b) {
      return (b.year || 0) - (a.year || 0) || (b.citations || 0) - (a.citations || 0) || a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    }).forEach(function (e) {
      var meta = [e.venue, e.citations ? e.citations + " citations" : null].filter(Boolean).join(" · ");
      list.appendChild(el("li", null, [node(e), el("span", { className: "where", text: meta })]));
    });
    $("papers-count").textContent = String(entries.length);
    $("papers").hidden = entries.length === 0;
  }

  function hasFilters(st) {
    var c = {}; for (var k in st) c[k] = st[k];
    c.view = "map";
    return serializeHash(c) !== "";
  }

  function mapOn() { return STATE.view === "map" && !!window.AtlasMap; }
  function treeOn() { return STATE.view === "tree" && !!window.AtlasTree; }

  function syncView() {
    var map = mapOn(), tree = treeOn();
    $("plate").classList.toggle("is-map", map);
    $("plate").classList.toggle("is-tree", tree);
    $("mapview").hidden = !map;
    $("treeview").hidden = !tree;
    document.querySelectorAll("#view-toggle [data-view]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-view") === STATE.view ? "true" : "false");
    });
  }

  function render() {
    var visible = filterEntries(ENTRIES, STATE);
    syncView();
    if (mapOn()) {
      // The map shows every country under the other filters, so picking another one stays possible.
      var facet = {}; for (var k in STATE) facet[k] = STATE[k];
      facet.country = [];
      var located = function (e) { return e.type !== "paper"; };
      window.AtlasMap.update({ entries: filterEntries(ENTRIES, facet).filter(located), visible: visible.filter(located), state: normalizeState(STATE) });
    }
    if (treeOn()) window.AtlasTree.render(visible.map(function (e) { return e.id; }));
    renderGrid(visible);
    renderRoster("orgs", "orgs-list", "orgs-count", visible.filter(function (e) { return e.type === "org"; }));
    renderRoster("skills", "skills-list", "skills-count", visible.filter(function (e) { return e.type === "agent-skill"; }));
    renderPapers(visible.filter(function (e) { return e.type === "paper"; }));
    syncChips();
    syncFoldSummary();
    var n = visible.length;
    $("result-count").textContent = n === ENTRIES.length ? "Showing all " + n + " entries" : n + " of " + ENTRIES.length + " entries match";
    $("clear").hidden = !hasFilters(STATE);
    $("cmd-recommend").textContent = recommendCall(STATE);
    $("cmd-search").textContent = searchCall(STATE);
    $("search-box").hidden = STATE.country.length !== 1;
    $("status").hidden = n !== 0;
    if (n === 0) $("status").textContent = "Nothing matches these filters. Remove a chip or shorten the search.";
  }

  function commit() {
    var h = serializeHash(STATE);
    var url = location.pathname + location.search + h;
    try { history.replaceState(null, "", url); } catch (e) { location.hash = h; }
    hideCard(true);
    render();
  }

  /* hover / focus card */
  var hideTimer = null, cardOwner = null;
  function scheduleHide() { clearTimeout(hideTimer); hideTimer = setTimeout(function () { hideCard(false); }, 180); }
  function hideCard(force) {
    var card = $("card");
    if (!force && (card.matches(":hover") || card.contains(document.activeElement))) return;
    card.hidden = true;
    cardOwner = null;
  }

  function row(label, value, opts) {
    if (value === undefined || value === null || value === "" || (Array.isArray(value) && !value.length)) return null;
    return el("div", { className: "row" }, [el("dt", { text: label }), el("dd", opts || null, [String(value)])]);
  }

  function showCard(e, anchor, viaKeyboard) {
    clearTimeout(hideTimer);
    var card = $("card");
    cardOwner = anchor;
    card.textContent = "";
    // e.external: a base model outside the atlas (from the tree view), with no country or license of ours.
    var color = COLORS[e.type] || "var(--rule-strong)";
    card.style.setProperty("--c", color);
    var m = e.metrics || {};
    card.appendChild(el("p", { className: "card-type" }, [el("span", { className: "swatch", style: "background:" + color }), TYPE_LABELS[e.type] || e.type]));
    card.appendChild(el("h3", { id: "card-name", dir: "auto", text: e.name }));
    var dl = el("dl", null, [
      row("Org", e.org, { dir: "auto" }),
      e.external ? null : row("Country", COUNTRY_NAMES[e.country || "INTL"] || e.country),
      e.external ? null : row("License", (e.license || "unknown") + " (" + LICENSE_LABELS[licenseClass(e.license)].toLowerCase() + ")"),
      row("Dialects", (e.dialects || []).map(function (d) { return DIALECT_LABELS[d] || d; }).join(", ")),
      row("Size", e.size),
      row("Downloads", m.downloads ? fmtDownloads(m.downloads) : null),
      row("Venue", e.venue),
      row("Citations", e.citations),
      row("Updated", m.lastModified || (e.year ? String(e.year) : null)),
      row("On device", e.on_device ? "Yes" : null)
    ]);
    card.appendChild(dl);
    if (e.notes) card.appendChild(el("p", { className: "notes", dir: "auto", text: e.notes }));
    var links = el("div", { className: "links" });
    LINK_ORDER.forEach(function (pair) {
      var href = (e.links || {})[pair[0]];
      if (href) links.appendChild(el("a", { className: "btn small", href: href, rel: "noopener" }, [e.external ? "Open on " + pair[1] : pair[1]]));
    });
    if (links.childNodes.length) card.appendChild(links);
    card.hidden = false;
    position(card, anchor);
  }

  function position(card, anchor) {
    var r = anchor.getBoundingClientRect();
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var cw = card.offsetWidth, ch = card.offsetHeight;
    var left = Math.min(Math.max(8, r.left), vw - cw - 8);
    var top = r.bottom + 8;
    if (top + ch > vh - 8) top = r.top - ch - 8;
    if (top < 8) top = Math.max(8, vh - ch - 8);
    card.style.left = left + "px";
    card.style.top = top + "px";
  }

  /* misc UI */
  function toast(msg) {
    var t = $("toast");
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { t.classList.remove("on"); }, 1800);
  }

  function copyText(text, done) {
    function fallback() {
      var ta = el("textarea", { style: "position:fixed;opacity:0" });
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); toast(done); } catch (e) { toast("Copy failed. Select the text and copy it manually."); }
      ta.remove();
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { toast(done); }, fallback);
    else fallback();
  }

  function currentTheme() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function syncThemeButton() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    var b = $("theme-toggle");
    b.textContent = next === "dark" ? "Dark" : "Light";
    b.setAttribute("aria-label", "Switch to " + next + " theme");
  }

  function wire() {
    var qTimer;
    $("q").addEventListener("input", function () {
      clearTimeout(qTimer);
      var v = this.value;
      qTimer = setTimeout(function () { STATE.q = v.trim(); commit(); }, 140);
    });
    $("on-device").addEventListener("change", function () { STATE.on_device = this.checked; commit(); });
    $("clear").addEventListener("click", function () { STATE = normalizeState({ view: STATE.view }); commit(); $("q").focus(); });
    document.querySelectorAll("#view-toggle [data-view]").forEach(function (b) {
      b.addEventListener("click", function () { STATE.view = b.getAttribute("data-view"); commit(); });
    });
    $("copy-link").addEventListener("click", function () { copyText(location.href, "Link copied"); });
    document.querySelectorAll("[data-copy]").forEach(function (b) {
      b.addEventListener("click", function () { copyText($(b.getAttribute("data-copy")).textContent, "Copied to clipboard"); });
    });
    $("theme-toggle").addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("atlas-theme", next); } catch (e) {}
      syncThemeButton();
    });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      (mq.addEventListener ? mq.addEventListener.bind(mq, "change") : mq.addListener.bind(mq))(syncThemeButton);
    }
    var card = $("card");
    card.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
    card.addEventListener("mouseleave", scheduleHide);
    card.addEventListener("focusout", scheduleHide);
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && card.hidden && mapOn() && !/INPUT|TEXTAREA/.test((document.activeElement || {}).tagName || "")) {
        window.AtlasMap.reset();
      }
      if (ev.key === "Escape" && !card.hidden) {
        var owner = cardOwner;
        hideCard(true);
        if (owner && card.contains(document.activeElement)) owner.focus();
      }
      // From a focused node, ArrowDown moves into its card so keyboard users can reach every link.
      if (ev.key === "ArrowDown" && !card.hidden && document.activeElement === cardOwner) {
        var first = card.querySelector("a");
        if (first) { ev.preventDefault(); first.focus(); }
      }
    });
    window.addEventListener("scroll", function () { if (!card.hidden && cardOwner) position(card, cardOwner); }, { passive: true });
    window.addEventListener("hashchange", function () { STATE = parseHash(location.hash); hideCard(true); render(); });
  }

  // On phones the chip groups start folded unless the link already carries filters.
  function setupFold() {
    var d = $("more-filters");
    var small = window.matchMedia && window.matchMedia("(max-width: 899px)");
    function apply() {
      var active = STATE.type.length + STATE.country.length + STATE.dialect.length + STATE.license.length + (STATE.on_device ? 1 : 0);
      d.open = !(small && small.matches) || active > 0;
    }
    apply();
    if (small) (small.addEventListener ? small.addEventListener.bind(small, "change") : small.addListener.bind(small))(apply);
  }

  function syncFoldSummary() {
    var active = STATE.type.length + STATE.country.length + STATE.dialect.length + STATE.license.length + (STATE.on_device ? 1 : 0);
    $("fold-n").textContent = active ? active + " active" : "";
  }

  function renderWanted(wanted) {
    var rows = wantedRows(wanted);
    var sec = $("wanted");
    sec.hidden = rows.open.length === 0 && rows.recent.length === 0;
    if (sec.hidden) return;
    $("wanted-n").textContent = "(" + rows.open.length + " open)";
    var list = $("wanted-list"), recent = $("wanted-recent");
    list.textContent = ""; recent.textContent = "";
    rows.open.forEach(function (r) {
      list.appendChild(el("li", {}, [
        el("a", { href: r.href, dir: "auto", text: r.title }),
        el("span", { className: "why", dir: "auto", text: r.why })
      ]));
    });
    rows.recent.forEach(function (r) {
      recent.appendChild(el("li", {}, [
        el("a", { href: r.href, dir: "auto", text: r.title }),
        r.filled_on ? el("span", { className: "why", text: "Filled " + r.filled_on }) : null
      ]));
    });
    $("wanted-recent-box").hidden = rows.recent.length === 0;
    var d = $("wanted-fold");
    var small = window.matchMedia && window.matchMedia("(max-width: 899px)");
    d.open = !(small && small.matches);
  }

  function boot() {
    syncThemeButton();
    wire();
    STATE = parseHash(location.hash);
    setupFold();
    loadData().then(function (data) {
      ENTRIES = data.entries || [];
      $("gen-date").textContent = data.generated_at || "";
      $("gen-date").setAttribute("datetime", data.generated_at || "");
      $("gen-count").textContent = String(data.count || ENTRIES.length);
      $("llms-link").href = DATA_BASE + "llms.txt";
      $("json-link").href = DATA_BASE + "atlas.json";
      setupChips();
      renderWanted(data.wanted);
      $("grid").hidden = false;
      if (window.AtlasMap) {
        window.AtlasMap.init({
          stage: $("mapview"), base: "./", colors: COLORS, typeLabels: TYPE_LABELS, makeNode: node,
          onSelect: function (code, type) {
            if (STATE.country.length === 1 && STATE.country[0] === code && !type) STATE.country = [];
            else STATE.country = [code];
            if (type) STATE.type = [type];
            commit();
          },
          onReset: function () { if (!STATE.country.length) return; STATE.country = []; commit(); }
        });
      }
      if (window.AtlasTree) {
        window.AtlasTree.init({
          stage: $("treeview"), lineage: data.lineage || {}, entries: ENTRIES, colors: COLORS,
          showCard: showCard, scheduleHide: scheduleHide, primaryLink: primaryLink
        });
      }
      render();
    }).catch(function () {
      $("status").textContent = "The atlas data could not be loaded. Browsers block file:// requests, so serve the folder instead: python3 -m http.server, then open localhost:8000/site/ in the browser.";
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
