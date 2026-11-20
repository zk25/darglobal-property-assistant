(() => {
  "use strict";

  // ---------------------------------------------------------------------------
  // Icons
  // ---------------------------------------------------------------------------
  const svg = (paths, extra = "") =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ${extra}>${paths}</svg>`;
  const I = {
    pin: svg('<path d="M12 21s-7-6.1-7-11.5a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    bed: svg('<path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6M3 14h18M3 18v2M21 18v2M7 10V7a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v3"/>'),
    area: svg('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>'),
    calendar: svg('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
    spark: svg('<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/>'),
    heart: svg('<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>'),
    arrow: svg('<path d="M7 17 17 7M9 7h8v8"/>'),
    close: svg('<path d="M18 6 6 18M6 6l12 12"/>'),
    external: svg('<path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>'),
    chat: svg('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>'),
    copy: svg('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>'),
    check: svg('<path d="m5 12 5 5 9-10"/>'),
    building: svg('<path d="M4 21V5l8-3v19M12 8l8 3v10M8 7v.01M8 11v.01M8 15v.01M16 14v.01M16 18v.01M2 21h20"/>'),
    gem: svg('<path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20M12 21 8 9l4-6 4 6z"/>'),
    passport: svg('<rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="10" r="3"/><path d="M9 17h6"/>'),
    search: svg('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'),
    tag: svg('<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>'),
    back: svg('<path d="m15 18-6-6 6-6"/>'),
    pool: svg('<path d="M2 17c2 0 2-1.5 4-1.5S8 17 10 17s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M2 21c2 0 2-1.5 4-1.5S8 21 10 21s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M8 14V5a2 2 0 0 1 4 0M16 14V5a2 2 0 0 0-4 0M8 9h8"/>'),
    golf: svg('<path d="M12 18V3l7 3.5-7 3.5"/><ellipse cx="12" cy="19" rx="7" ry="2"/>'),
    sun: svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    drop: svg('<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>'),
    gym: svg('<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>'),
    bell: svg('<path d="M4 18h16M6 18a6 6 0 0 1 12 0M12 9V7M10 7h4"/>'),
    star: svg('<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'),
    eye: svg('<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
    film: svg('<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>'),
    shield: svg('<path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/>'),
    smart: svg('<path d="M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 19.5h.01M2 9a14 14 0 0 1 20 0"/>'),
  };

  // Amenity icons derived from each project's published highlights.
  const AMENITIES = [
    [/pool/i, "Pool", "pool"],
    [/golf/i, "Golf", "golf"],
    [/beach|seafront|oceanfront/i, "Beach", "sun"],
    [/spa|sauna/i, "Spa", "drop"],
    [/gym|fitness/i, "Gym", "gym"],
    [/concierge|porterage/i, "Concierge", "bell"],
    [/club|lounge/i, "Club", "star"],
    [/view/i, "Views", "eye"],
    [/cinema/i, "Cinema", "film"],
    [/security|gated/i, "Security", "shield"],
    [/smart|lutron|sonos/i, "Smart home", "smart"],
    [/residency|freehold/i, "Ownership", "passport"],
  ];

  function amenitiesOf(p) {
    const text = p.highlights.join(" | ");
    return AMENITIES.filter(([re]) => re.test(text)).slice(0, 5);
  }
  const HOUSE = '<svg viewBox="0 0 24 24"><path d="M5 20V10l7-5 7 5v10h-5v-6h-4v6z" fill="#fff"/></svg>';
  const TOPIC_ICONS = [I.building, I.gem, I.passport, I.search];

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const state = {
    projects: [],
    byId: {},
    saved: new Set(readSaved()),
    filter: "All",
    query: "",
    selected: null,
    history: [],
    busy: false,
    map: null,
    markers: {},
  };
  const FEATURED = ["trump-tower-jeddah", "the-astera", "da-vinci-tower", "les-vagues", "aida", "tierra-viva"];
  const COUNTRIES = ["All", "UAE", "Saudi Arabia", "Oman", "Qatar", "Spain", "UK"];

  function readSaved() {
    try { return JSON.parse(localStorage.getItem("pa:saved") || "[]"); } catch { return []; }
  }
  function writeSaved() {
    try { localStorage.setItem("pa:saved", JSON.stringify([...state.saved])); } catch { /* storage unavailable */ }
  }

  // ---------------------------------------------------------------------------
  // Illustrated covers (generated SVG, varies by project type and market)
  // ---------------------------------------------------------------------------
  const SKIES = {
    "UAE": ["#b9cdff", "#eef3ff", "#e6ecfb"],
    "Saudi Arabia": ["#ffd2ad", "#fff2e6", "#f4e6d6"],
    "Oman": ["#b6e2ee", "#effafc", "#d9ecdf"],
    "Qatar": ["#c3d2ff", "#f3f6ff", "#e8ecf8"],
    "Spain": ["#ffd9b8", "#fff6ec", "#e3ecd5"],
    "UK": ["#cfd7e8", "#f2f4f9", "#e3e7ee"],
  };
  let coverCount = 0;

  function seeded(str) {
    let h = 2166136261;
    for (const ch of str) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
    return () => {
      h = Math.imul(h ^ (h >>> 15), 2246822507);
      h = Math.imul(h ^ (h >>> 13), 3266489909);
      return ((h ^= h >>> 16) >>> 0) / 4294967296;
    };
  }

  function palm(x, y, s = 1) {
    return `<g transform="translate(${x} ${y}) scale(${s})" stroke-linecap="round">
      <path d="M0 0 C 2 -18, 4 -30, 2 -44" stroke="#5b4a3a" stroke-width="3" fill="none"/>
      <path d="M2 -44 q -14 -6 -24 4 M2 -44 q 14 -8 26 2 M2 -44 q -6 -14 -20 -12 M2 -44 q 8 -14 22 -10" stroke="#2f8f6a" stroke-width="4" fill="none"/>
    </g>`;
  }

  function cover(p) {
    const r = seeded(p.id);
    const uid = `c${++coverCount}`;
    const [skyTop, skyBottom, ground] = SKIES[p.country] || SKIES.UAE;
    let skyline = "";
    for (let i = 0; i < 15; i++) {
      const h = 24 + r() * 70;
      skyline += `<rect x="${i * 28 - 6}" y="${196 - h}" width="${18 + r() * 10}" height="${h}" rx="2"/>`;
    }
    const defs = `<defs>
      <linearGradient id="${uid}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${skyTop}"/><stop offset="1" stop-color="${skyBottom}"/></linearGradient>
      <linearGradient id="${uid}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5f86ff"/><stop offset="1" stop-color="#1f3db8"/></linearGradient>
      <linearGradient id="${uid}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b84ff"/><stop offset="1" stop-color="#2e5bff"/></linearGradient>
    </defs>`;
    const base = `<rect width="400" height="240" fill="url(#${uid}s)"/>
      <circle cx="${290 + r() * 70}" cy="${48 + r() * 24}" r="28" fill="#fff" opacity=".6"/>
      <g fill="#0e1834" opacity=".07">${skyline}</g>`;

    let scene = "";
    if (p.type === "tower") {
      const top = 22 + r() * 26;
      const x = 130 + Math.floor(r() * 70);
      const variant = Math.floor(r() * 3);
      let lines = "";
      for (let y = top + 22; y < 196; y += 13) lines += `<path d="M${x} ${y}H${x + 72}"/>`;
      let main;
      if (variant === 0) {
        // slanted crown
        main = `<path d="M${x} 200V${top + 12}L${x + 72} ${top}V200Z" fill="url(#${uid}g)"/>
          <path d="M${x} ${top + 12}L${x + 72} ${top}" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>`;
      } else if (variant === 1) {
        // rounded top with spire
        main = `<path d="M${x} 200V${top + 30}a36 30 0 0 1 72 0V200Z" fill="url(#${uid}g)"/>
          <path d="M${x + 36} ${top}V${top - 16}" stroke="#1f3db8" stroke-width="3"/>`;
      } else {
        // stepped setbacks
        main = `<path d="M${x} 200V${top + 44}H${x + 10}V${top + 20}H${x + 22}V${top}H${x + 50}V${top + 20}H${x + 62}V${top + 44}H${x + 72}V200Z" fill="url(#${uid}g)"/>`;
      }
      scene = `
        <rect x="${x - 58}" y="${112 + r() * 20}" width="50" height="100" rx="3" fill="#9db4ff"/>
        <rect x="${x + 128}" y="${128 + r() * 20}" width="36" height="80" rx="3" fill="#c3d2ff"/>
        <rect x="${x + 78}" y="${80 + r() * 24}" width="46" height="130" rx="3" fill="#0e1834" opacity=".86"/>
        ${main}
        <g stroke="#fff" stroke-opacity=".2" stroke-width="1">${lines}<path d="M${x + 24} ${top + 30}V200M${x + 48} ${top + 30}V200"/></g>
        <rect x="0" y="198" width="400" height="42" fill="${ground}"/>
        <rect x="0" y="198" width="400" height="3" fill="#0e1834" opacity=".08"/>`;
    } else if (p.type === "beach") {
      scene = `
        <rect x="120" y="96" width="70" height="104" rx="6" fill="#fff"/>
        <rect x="186" y="74" width="80" height="126" rx="6" fill="#f4f7ff"/>
        <rect x="262" y="110" width="58" height="90" rx="6" fill="#fff"/>
        <g fill="url(#${uid}g)" opacity=".85">
          ${[0, 1, 2, 3, 4, 5].map((i) => `<rect x="196" y="${86 + i * 18}" width="60" height="8" rx="2"/>`).join("")}
          ${[0, 1, 2, 3].map((i) => `<rect x="130" y="${108 + i * 22}" width="50" height="8" rx="2"/><rect x="270" y="${122 + i * 18}" width="42" height="7" rx="2"/>`).join("")}
        </g>
        <rect x="0" y="192" width="400" height="12" fill="#f3e4c6"/>
        <rect x="0" y="204" width="400" height="36" fill="url(#${uid}w)"/>
        <path d="M20 216q15-6 30 0t30 0M150 224q15-6 30 0t30 0M280 214q15-6 30 0t30 0" stroke="#fff" stroke-opacity=".5" stroke-width="2" fill="none"/>
        ${palm(92, 196, 0.9)}${palm(338, 196, 1)}`;
    } else if (p.type === "villas") {
      const villa = (x, w) => `
        <rect x="${x}" y="152" width="${w}" height="46" rx="3" fill="#fff"/>
        <rect x="${x + 10}" y="128" width="${w * 0.55}" height="26" rx="2" fill="#fff"/>
        <rect x="${x - 6}" y="148" width="${w + 12}" height="6" rx="2" fill="#0e1834"/>
        <rect x="${x + 4}" y="124" width="${w * 0.55 + 12}" height="5" rx="2" fill="#0e1834"/>
        <rect x="${x + 10}" y="162" width="${w * 0.3}" height="26" rx="2" fill="url(#${uid}g)" opacity=".85"/>
        <rect x="${x + w * 0.5}" y="162" width="${w * 0.36}" height="18" rx="2" fill="url(#${uid}g)" opacity=".7"/>`;
      scene = `
        <rect x="0" y="196" width="400" height="44" fill="${ground}"/>
        ${villa(36, 96)}${villa(160, 100)}${villa(286, 88)}
        <rect x="150" y="206" width="110" height="14" rx="7" fill="url(#${uid}w)" opacity=".85"/>
        ${palm(146, 198, 0.75)}${palm(276, 198, 0.85)}`;
    } else if (p.type === "masterplan") {
      let houses = "";
      for (let i = 0; i < 9; i++) {
        const x = 30 + i * 40 + r() * 10, y = 150 + Math.sin(i * 0.9) * 14 + r() * 8;
        houses += `<rect x="${x}" y="${y}" width="22" height="13" rx="2" fill="#fff"/><rect x="${x - 2}" y="${y - 3}" width="26" height="4" rx="1" fill="#0e1834" opacity=".8"/>`;
      }
      scene = `
        <path d="M0 150 Q 90 96 190 136 T 400 118 V240 H0Z" fill="#a9d4b8"/>
        ${houses}
        <path d="M0 196 Q 120 168 230 190 T 400 182 V240 H0Z" fill="#7fbf98"/>
        <ellipse cx="300" cy="206" rx="46" ry="10" fill="#9fd6b0"/>
        <path d="M300 206V176" stroke="#0e1834" stroke-width="2"/><path d="M300 176l16 5-16 5z" fill="#2e5bff"/>
        ${palm(70, 210, 0.8)}`;
    } else {
      let windows = "";
      for (let row = 0; row < 5; row++) for (let col = 0; col < 6; col++) {
        windows += `<rect x="${124 + col * 26}" y="${74 + row * 22}" width="12" height="14" rx="1.5" fill="#0e1834" opacity=".72"/>`;
      }
      scene = `
        <rect x="110" y="58" width="180" height="142" fill="#efe6d6"/>
        <rect x="104" y="52" width="192" height="8" fill="#ddd1bb"/>
        ${windows}
        <path d="M188 200v-24a12 12 0 0 1 24 0v24z" fill="#0e1834"/>
        <circle cx="70" cy="168" r="30" fill="#7fae8c"/><rect x="67" y="180" width="6" height="22" fill="#5b4a3a"/>
        <circle cx="336" cy="170" r="26" fill="#8cbb98"/><rect x="333" y="182" width="6" height="20" fill="#5b4a3a"/>
        <rect x="0" y="198" width="400" height="42" fill="${ground}"/>`;
    }
    return `<svg viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${defs}${base}${scene}</svg>`;
  }

  // ---------------------------------------------------------------------------
  // Project cards, hearts, sheet
  // ---------------------------------------------------------------------------
  const isDone = (p) => /completed|sold out/i.test(p.status);
  const shortPrice = (p) => (p.price === "Price on request" ? "On request" : p.price);
  const place = (p) => (p.area && p.area !== p.city ? `${p.area}, ${p.city}` : `${p.city}, ${p.country}`);

  function heartButton(id) {
    const on = state.saved.has(id);
    return `<button type="button" class="heart${on ? " on" : ""}" data-heart="${esc(id)}" aria-pressed="${on}" aria-label="${on ? "Remove from saved" : "Save project"}">${I.heart}</button>`;
  }

  function projectCard(p, { mini = false } = {}) {
    const el = document.createElement("article");
    el.className = "card";
    el.dataset.id = p.id;
    el.tabIndex = 0;
    el.setAttribute("aria-label", `${p.name}, ${place(p)}`);
    el.innerHTML = `
      <div class="cover">${cover(p)}<span class="badge${isDone(p) ? " done" : ""}">${esc(p.status)}</span>${heartButton(p.id)}</div>
      <div class="card-body">
        <div class="title-row"><h3>${esc(p.short)}</h3>${mini ? "" : `<span class="price">${esc(shortPrice(p))}</span>`}</div>
        <p class="loc">${I.pin}${esc(place(p))}</p>
        ${mini ? "" : `
        <div class="specs"><span class="spec">${I.bed}${esc(p.bedrooms)}</span><span class="spec">${I.area}${esc(p.size)}</span></div>
        <p class="partner">${I.spark}${esc(p.brand)}</p>`}
      </div>`;
    el.addEventListener("click", (e) => { if (!e.target.closest(".heart")) openSheet(p.id); });
    el.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target === el) openSheet(p.id); });
    return el;
  }

  function toggleSaved(id) {
    if (state.saved.has(id)) state.saved.delete(id); else state.saved.add(id);
    writeSaved();
    const on = state.saved.has(id);
    $$(`[data-heart="${CSS.escape(id)}"]`).forEach((b) => {
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", String(on));
      b.setAttribute("aria-label", on ? "Remove from saved" : "Save project");
    });
    renderSaved();
  }

  document.addEventListener("click", (e) => {
    const heart = e.target.closest("[data-heart]");
    if (heart) { e.stopPropagation(); toggleSaved(heart.dataset.heart); return; }
    const nav = e.target.closest("[data-nav]");
    if (nav) go(nav.dataset.nav);
  });

  const sheetBackdrop = $("#sheet");
  const sheet = $(".sheet", sheetBackdrop);
  let lastFocus = null;

  function insightQuestions(p) {
    const where = p.country === "UAE" ? "the UAE" : p.country === "UK" ? "London" : p.country;
    return [
      [I.star, `What amenities does ${p.short} have?`],
      [I.calendar, isDone(p) ? `Can I still buy at ${p.short}?` : `When will ${p.short} be completed?`],
      p.country === "UK"
        ? [I.pin, "Where else does DarGlobal build in Europe?"]
        : [I.passport, `What residency comes with buying in ${where}?`],
    ];
  }

  function openSheet(id) {
    const p = state.byId[id];
    if (!p) return;
    lastFocus = document.activeElement;
    const facts = [
      [I.bed, "Bedrooms", p.bedrooms],
      [I.area, "Size", p.size],
      [I.calendar, "Completion", p.completion],
      [I.tag, "Partner", p.brand],
    ];
    const amenities = amenitiesOf(p);
    sheet.innerHTML = `
      <div class="sheet-top">
        <button type="button" class="round-btn" data-close aria-label="Close">${I.back}</button>
        <h3>Project details</h3>
        ${heartButton(p.id)}
      </div>
      <div class="sheet-grid">
        <div class="sheet-main">
          <div class="sheet-cover">${cover(p)}<span class="badge${isDone(p) ? " done" : ""}">${esc(p.status)}</span></div>
          <div class="sheet-head">
            <div class="sheet-title">
              <div><h2 id="sheet-title">${esc(p.name)}</h2><p class="loc">${I.pin}${esc(place(p))}, ${esc(p.country)}</p></div>
            </div>
            <div class="price-line"><b>${esc(p.price)}</b><span>${p.price === "Price on request" ? "from DarGlobal's sales team" : ""}</span></div>
          </div>
          <div class="facts">${facts.map(([icon, label, value]) => `<div class="fact"><span class="fi">${icon}</span><small>${label}</small><b>${esc(value)}</b></div>`).join("")}</div>
        </div>
        <div class="sheet-side">
          <section class="insights">
            <header>${I.spark}Ask the assistant<small>Answers cite the source</small></header>
            <div class="insight-grid">${insightQuestions(p).map(([icon, q]) => `<button type="button" data-ask="${esc(q)}"><span class="ii">${icon}</span>${esc(q)}</button>`).join("")}</div>
          </section>
          ${amenities.length ? `<h4>Amenities</h4><div class="amenities">${amenities.map(([, label, icon]) => `<div class="amenity">${I[icon]}${label}</div>`).join("")}</div>` : ""}
          <h4>Highlights</h4>
          <div class="highlights">${p.highlights.map((h) => `<span>${esc(h)}</span>`).join("")}</div>
          <div class="sheet-actions">
            <a class="btn ghost" href="${esc(p.url)}" target="_blank" rel="noopener noreferrer">${I.external}Official page</a>
            <button type="button" class="btn primary" data-ask="Tell me about ${esc(p.short)}">${I.chat}Ask about this project</button>
          </div>
        </div>
      </div>`;
    sheetBackdrop.hidden = false;
    sheet.scrollTop = 0;
    $("[data-close]", sheet).focus();
    if (state.map) selectProject(id, { fly: false });
  }

  function closeSheet() {
    if (sheetBackdrop.hidden) return;
    sheetBackdrop.hidden = true;
    if (lastFocus && lastFocus.isConnected) lastFocus.focus();
  }

  sheetBackdrop.addEventListener("click", (e) => {
    if (e.target === sheetBackdrop || e.target.closest("[data-close]")) { closeSheet(); return; }
    const askBtn = e.target.closest("[data-ask]");
    if (askBtn) { closeSheet(); go("assistant"); ask(askBtn.dataset.ask); }
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSheet(); });

  // ---------------------------------------------------------------------------
  // Views
  // ---------------------------------------------------------------------------
  function go(view) {
    if (!["assistant", "explore", "saved"].includes(view)) view = "assistant";
    $$(".view").forEach((v) => { v.hidden = v.dataset.view !== view; });
    $$(".dock [data-nav]").forEach((b) => b.classList.toggle("active", b.dataset.nav === view));
    if (location.hash !== `#${view}`) history.replaceState(null, "", `#${view}`);
    if (view === "explore") ensureMap();
    if (view === "assistant") setTimeout(() => input.focus(), 50);
  }
  window.addEventListener("hashchange", () => go(location.hash.slice(1)));

  // ---------------------------------------------------------------------------
  // Explore: filters, list, map
  // ---------------------------------------------------------------------------
  function visibleProjects() {
    const q = state.query.trim().toLowerCase();
    return state.projects.filter((p) =>
      (state.filter === "All" || p.country === state.filter) &&
      (!q || [p.name, p.city, p.country, p.area, p.brand, p.type].join(" ").toLowerCase().includes(q)));
  }

  function renderFilters() {
    const box = $("#filters");
    box.innerHTML = "";
    COUNTRIES.forEach((c) => {
      const n = c === "All" ? state.projects.length : state.projects.filter((p) => p.country === c).length;
      if (!n) return;
      const b = document.createElement("button");
      b.type = "button";
      b.className = c === state.filter ? "active" : "";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(c === state.filter));
      b.innerHTML = `${esc(c)} <span>${n}</span>`;
      b.addEventListener("click", () => setMarket(c));
      box.appendChild(b);
    });
  }

  // Market picker in the header; shares its selection with the Explore filters.
  const marketBtn = $("#market-btn"), marketMenu = $("#market-menu");

  function setMarket(c) {
    state.filter = c;
    $("#market-label").textContent = c === "All" ? "All markets" : c;
    renderFilters();
    renderExplore(true);
    renderFeatured();
  }

  function toggleMarketMenu(open) {
    marketMenu.hidden = !open;
    marketBtn.setAttribute("aria-expanded", String(open));
    if (!open) return;
    marketMenu.innerHTML = "";
    COUNTRIES.forEach((c) => {
      const n = c === "All" ? state.projects.length : state.projects.filter((p) => p.country === c).length;
      if (!n) return;
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("role", "option");
      b.setAttribute("aria-selected", String(c === state.filter));
      b.innerHTML = `${esc(c === "All" ? "All markets" : c)}<span>${n} project${n === 1 ? "" : "s"}</span>`;
      b.addEventListener("click", () => { toggleMarketMenu(false); setMarket(c); go("explore"); });
      marketMenu.appendChild(b);
    });
    marketMenu.firstElementChild?.focus();
  }

  marketBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleMarketMenu(marketMenu.hidden); });
  document.addEventListener("click", (e) => { if (!marketMenu.hidden && !e.target.closest(".market")) toggleMarketMenu(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !marketMenu.hidden) { toggleMarketMenu(false); marketBtn.focus(); } });

  function renderExplore(refit = false) {
    const list = visibleProjects();
    $("#result-count").textContent = `${list.length} project${list.length === 1 ? "" : "s"}${state.filter === "All" ? "" : ` in ${state.filter}`}`;
    const cards = $("#cards");
    cards.innerHTML = "";
    list.forEach((p) => {
      const el = projectCard(p);
      el.addEventListener("mouseenter", () => highlightMarker(p.id));
      cards.appendChild(el);
    });
    if (!list.length) cards.innerHTML = '<p class="lede">No projects match your search.</p>';
    if (state.map) {
      const ids = new Set(list.map((p) => p.id));
      Object.entries(state.markers).forEach(([id, m]) => {
        if (ids.has(id)) m.addTo(state.map); else m.remove();
      });
      if (refit) fitTo(list);
    }
  }

  function fitTo(list) {
    if (!state.map || !list.length) return;
    const bounds = L.latLngBounds(list.map((p) => [p.lat, p.lng]));
    state.map.fitBounds(bounds, { padding: [60, 60], maxZoom: 12 });
  }

  function ensureMap() {
    if (typeof L === "undefined") { $(".map-panel").hidden = true; return; }
    if (state.map) { setTimeout(() => state.map.invalidateSize(), 60); return; }
    const map = L.map("map", { zoomControl: false, worldCopyJump: true, minZoom: 2 });
    L.control.zoom({ position: "topright" }).addTo(map);
    map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
    // Smaller pins when zoomed out, so nearby projects (e.g. in Dubai) overlap less.
    const sizePins = () => map.getContainer().classList.toggle("zoomed-out", map.getZoom() < 10);
    map.on("zoomend", sizePins);
    map.whenReady(sizePins);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      subdomains: "abcd",
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(map);
    state.map = map;
    state.projects.forEach((p) => {
      const icon = L.divIcon({ className: "pin", html: `<span class="pin-thumb">${cover(p)}</span>`, iconSize: [46, 46], iconAnchor: [23, 23] });
      const marker = L.marker([p.lat, p.lng], { icon, title: p.short, keyboard: true });
      marker.on("click", () => selectProject(p.id, { fly: true }));
      state.markers[p.id] = marker;
    });
    renderExplore(true);
    setTimeout(() => { map.invalidateSize(); fitTo(visibleProjects()); }, 80);
  }

  function highlightMarker(id) {
    Object.entries(state.markers).forEach(([pid, m]) => {
      const el = m.getElement();
      if (el) el.classList.toggle("active", pid === id);
      m.setZIndexOffset(pid === id ? 1000 : 0);
    });
  }

  function selectProject(id, { fly }) {
    const p = state.byId[id];
    if (!p) return;
    state.selected = id;
    highlightMarker(id);
    $$(".list-panel .card").forEach((c) => c.classList.toggle("selected", c.dataset.id === id));
    if (fly && state.map) state.map.flyTo([p.lat, p.lng], Math.max(state.map.getZoom(), 11), { duration: 0.8 });
    const box = $("#map-card");
    box.innerHTML = `
      <div class="thumb">${cover(p)}</div>
      <div class="info"><h3>${esc(p.short)}</h3><div class="meta">${esc(place(p))}</div><div class="meta"><b style="color:var(--primary)">${esc(shortPrice(p))}</b> · ${esc(p.status)}</div></div>
      <button type="button" class="go" aria-label="Open ${esc(p.short)}">${I.arrow}</button>`;
    box.hidden = false;
    box.onclick = () => openSheet(id);
  }

  $("#search").addEventListener("input", (e) => { state.query = e.target.value; renderExplore(true); });

  // ---------------------------------------------------------------------------
  // Saved
  // ---------------------------------------------------------------------------
  function renderSaved() {
    const list = state.projects.filter((p) => state.saved.has(p.id));
    const box = $("#saved-cards");
    box.innerHTML = "";
    list.forEach((p) => box.appendChild(projectCard(p)));
    $("#saved-empty").hidden = list.length > 0;
    $$("[data-saved-count]").forEach((el) => { el.hidden = !list.length; el.textContent = list.length; });
    $$("[data-saved-dot]").forEach((el) => { el.hidden = !list.length; });
  }

  // ---------------------------------------------------------------------------
  // Assistant
  // ---------------------------------------------------------------------------
  const thread = $("#thread"), scroller = $("#scroller"), form = $("#form"), input = $("#input"), sendBtn = $("#send"), welcome = $("#welcome");

  function inline(text, sources, hideCites) {
    const html = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
    return html.replace(/\s?\[(\d{1,2})\]/g, (m, n) => {
      if (hideCites) return "";
      const src = sources && sources[Number(n) - 1];
      return src ? `<a class="cite" href="${esc(src.url)}" target="_blank" rel="noopener noreferrer" title="${esc(src.title)}">${n}</a>` : "";
    });
  }

  // Safe Markdown subset: paragraphs, headings, lists, bold, code and citations.
  function renderMarkdown(text, sources, hideCites) {
    const lines = esc(text).split(/\r?\n/);
    let html = "", list = null, para = [];
    const flush = () => { if (para.length) { html += `<p>${inline(para.join(" "), sources, hideCites)}</p>`; para = []; } };
    const close = () => { if (list) { html += `</${list}>`; list = null; } };
    for (const raw of lines) {
      const line = raw.trim();
      const bullet = line.match(/^[-*•]\s+(.*)/);
      const numbered = line.match(/^\d+[.)]\s+(.*)/);
      const heading = line.match(/^#{1,6}\s+(.*)/) || line.match(/^\*\*([^*]+)\*\*:?$/);
      if (bullet || numbered) {
        flush();
        const type = bullet ? "ul" : "ol";
        if (list !== type) { close(); html += `<${type}>`; list = type; }
        html += `<li>${inline((bullet || numbered)[1], sources, hideCites)}</li>`;
      } else if (heading) {
        flush(); close();
        html += `<div class="h">${inline(heading[1], sources, hideCites)}</div>`;
      } else if (!line) {
        flush(); close();
      } else {
        close(); para.push(line);
      }
    }
    flush(); close();
    return html;
  }

  const plainText = (t) => t.replace(/\s?\[\d{1,2}\]/g, "").replace(/\*\*(.+?)\*\*/g, "$1");
  const domainOf = (url) => { try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return ""; } };
  const scrollDown = () => { scroller.scrollTop = scroller.scrollHeight; };

  function chip(text, onClick) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = text;
    b.addEventListener("click", onClick);
    return b;
  }

  function addUserMessage(text) {
    welcome.hidden = true;
    const row = document.createElement("div");
    row.className = "msg-user";
    const bubble = document.createElement("div");
    bubble.className = "bubble"; bubble.dir = "auto"; bubble.textContent = text;
    row.appendChild(bubble);
    thread.appendChild(row);
    scrollDown();
  }

  function addBotMessage() {
    const row = document.createElement("div");
    row.className = "msg-bot";
    row.innerHTML = `<span class="avatar" aria-hidden="true">${HOUSE}</span>
      <div class="body"><div class="answer-card">
        <div class="status"><span class="spinner"></span>Searching DarGlobal and Wasalt pages…</div>
        <div class="answer" dir="auto" hidden></div>
      </div></div>`;
    thread.appendChild(row);
    scrollDown();
    const body = $(".body", row), card = $(".answer-card", row), answerEl = $(".answer", row), statusEl = $(".status", row);
    let text = "", frame = 0;

    return {
      append(piece) {
        text += piece;
        if (statusEl.isConnected) { statusEl.remove(); answerEl.hidden = false; }
        if (!frame) frame = requestAnimationFrame(() => {
          frame = 0;
          answerEl.innerHTML = renderMarkdown(text, null, true) + '<span class="caret"></span>';
          scrollDown();
        });
      },
      finish(data) {
        cancelAnimationFrame(frame);
        statusEl.remove();
        answerEl.hidden = false;
        answerEl.innerHTML = renderMarkdown(data.answer, data.sources, false);

        const named = (data.projects || []).map((id) => state.byId[id]).filter(Boolean);
        if (named.length) {
          const rail = document.createElement("div");
          rail.className = "rail mini answer-projects";
          named.forEach((p) => rail.appendChild(projectCard(p, { mini: true })));
          card.appendChild(rail);
        }
        if (data.sources && data.sources.length) {
          const box = document.createElement("div");
          box.className = "sources";
          box.innerHTML = "<small>Sources</small>";
          data.sources.forEach((s, i) => {
            const a = document.createElement("a");
            a.className = "source"; a.href = s.url; a.target = "_blank"; a.rel = "noopener noreferrer";
            a.innerHTML = `<span class="n">${i + 1}</span><b></b><span></span>`;
            $("b", a).textContent = s.title;
            $("span:last-child", a).textContent = domainOf(s.url);
            box.appendChild(a);
          });
          card.appendChild(box);
        }

        const actions = document.createElement("div");
        actions.className = "actions";
        const copy = document.createElement("button");
        copy.type = "button"; copy.className = "action"; copy.innerHTML = `${I.copy}<span>Copy</span>`;
        copy.addEventListener("click", async () => {
          try { await navigator.clipboard.writeText(plainText(data.answer)); } catch { return; }
          copy.innerHTML = `${I.check}<span>Copied</span>`;
          setTimeout(() => { copy.innerHTML = `${I.copy}<span>Copy</span>`; }, 1600);
        });
        actions.appendChild(copy);
        body.appendChild(actions);

        if (data.follow_ups && data.follow_ups.length) {
          const wrap = document.createElement("div");
          wrap.className = "followups";
          data.follow_ups.forEach((q) => wrap.appendChild(chip(q, () => ask(q))));
          body.appendChild(wrap);
        }
        scrollDown();
      },
      fail(message, retry) {
        cancelAnimationFrame(frame);
        row.remove();
        const box = document.createElement("div");
        box.className = "notice";
        box.innerHTML = "<span></span>";
        $("span", box).textContent = message;
        if (retry) box.appendChild(chip("Try again", () => { box.remove(); retry(); }));
        thread.appendChild(box);
        scrollDown();
      },
    };
  }

  async function streamAnswer(question, view) {
    const res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question, history: state.history }),
    });
    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      const error = new Error(typeof data.detail === "string" ? data.detail : "Something went wrong. Please try again.");
      error.status = res.status;
      throw error;
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "", final = null;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let cut;
      while ((cut = buffer.indexOf("\n\n")) >= 0) {
        const block = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 2);
        const event = (block.match(/^event: (.*)$/m) || [])[1];
        const dataLine = (block.match(/^data: (.*)$/m) || [])[1];
        if (!event || !dataLine) continue;
        const data = JSON.parse(dataLine);
        if (event === "delta") view.append(data.text);
        if (event === "done") final = data;
      }
    }
    if (!final) throw new Error("The answer was interrupted. Please try again.");
    return final;
  }

  async function ask(question) {
    question = (question || "").trim();
    if (!question || state.busy) return;
    state.busy = true; updateSend();
    $$(".followups", thread).forEach((el) => el.remove());
    addUserMessage(question);
    input.value = ""; autosize();
    const view = addBotMessage();
    try {
      const data = await streamAnswer(question, view);
      view.finish(data);
      state.history.push({ role: "user", content: question }, { role: "assistant", content: plainText(data.answer) });
      state.history = state.history.slice(-12);
    } catch (err) {
      const offline = err instanceof TypeError;
      view.fail(
        offline ? "Couldn't reach the server. Check your connection and try again." : err.message,
        err.status === 429 ? null : () => {
          const last = thread.lastElementChild;
          if (last && last.classList.contains("msg-user")) last.remove();
          ask(question);
        });
    } finally {
      state.busy = false; updateSend();
    }
  }

  function autosize() { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 150) + "px"; }
  function updateSend() { sendBtn.disabled = state.busy || !input.value.trim(); }

  form.addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); ask(input.value); }
  });
  input.addEventListener("input", () => { autosize(); updateSend(); });
  $("#new-chat").addEventListener("click", () => {
    if (state.busy) return;
    state.history = [];
    $$(".msg-user, .msg-bot, .notice", thread).forEach((n) => n.remove());
    welcome.hidden = false;
    go("assistant");
  });

  // ---------------------------------------------------------------------------
  // Start-up
  // ---------------------------------------------------------------------------
  function renderHome(topics, more) {
    const quick = $("#topics");
    quick.innerHTML = "";
    topics.forEach((t, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = `<span class="qi">${TOPIC_ICONS[i % TOPIC_ICONS.length]}</span><b></b><span></span>`;
      $("b", b).textContent = t.title;
      $("span:last-child", b).textContent = t.question;
      b.addEventListener("click", () => ask(t.question));
      quick.appendChild(b);
    });
    const moreBox = $("#more");
    moreBox.innerHTML = more.length ? "<small>Or ask</small>" : "";
    more.forEach((q) => moreBox.appendChild(chip(q, () => ask(q))));
  }

  function renderFeatured() {
    const rail = $("#featured");
    rail.innerHTML = "";
    const list = state.filter === "All"
      ? FEATURED.map((id) => state.byId[id]).filter(Boolean)
      : state.projects.filter((p) => p.country === state.filter);
    list.forEach((p) => rail.appendChild(projectCard(p)));
    $(".home .section-head h2").textContent = state.filter === "All" ? "Featured projects" : `Projects in ${state.filter}`;
  }

  async function init() {
    const [projectsRes, suggestionsRes] = await Promise.allSettled([
      fetch("/api/projects").then((r) => r.json()),
      fetch("/api/suggestions").then((r) => r.json()),
    ]);
    if (projectsRes.status === "fulfilled") {
      state.projects = projectsRes.value.projects || [];
      state.byId = Object.fromEntries(state.projects.map((p) => [p.id, p]));
    }
    const s = suggestionsRes.status === "fulfilled" ? suggestionsRes.value : {};
    renderHome(s.topics || [], s.more || []);
    renderFeatured();
    renderFilters();
    renderExplore();
    renderSaved();
    go(location.hash.slice(1) || "assistant");
  }

  init();
})();
