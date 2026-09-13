(() => {
  const PRESETS = {
    high: {
      severity: "High",
      status: "Open",
      guidance:
        "High-severity timeline: remediate within 30 days of discovery. Include the planned fix (patch, configuration change, or compensating control) and follow-up scan validation. Do not invent plugin IDs or dates.",
    },
    moderate: {
      severity: "Moderate",
      status: "Open",
      guidance:
        "Moderate-severity timeline: remediate within 90 days of discovery. Stage the change, deploy, then validate with a follow-up scan before the 90-day mark. Do not invent plugin IDs or dates.",
    },
    low: {
      severity: "Low",
      status: "Open",
      guidance:
        "Low-severity timeline: remediate within 180 days of discovery. Keep milestone dates current; do not leave a stale open item without justification. Do not invent plugin IDs or dates.",
    },
    fp: {
      severity: "Moderate",
      status: "Pending",
      vendor_dependency: "no",
      guidance:
        "Document as a False Positive or Risk Adjustment starter — not a confirmed open weakness until assessor validation. State what the scanner reported, what investigation showed (service not installed, compensating control, residual risk), and mark validation Pending. Do not invent CVE/plugin IDs or close the item outright.",
    },
  };

  const SSP_STARTERS = {
    "AU-2": {
      system_context:
        "DoD web application. Name the logging/SIEM platform only if known; otherwise keep [SIEM]. Describe events logged, review cadence, and retention.",
      guidance:
        "Make the statement assessor-testable: events, reviewer role, retention, and customer responsibility.",
    },
    "IA-2": {
      system_context:
        "System requires multi-factor authentication for users and privileged access. Name the identity provider only if known; otherwise keep [identity provider].",
      guidance:
        "Cover privileged vs. standard users, remote access, and any temporary exception process as placeholders if unknown.",
    },
    "RA-5": {
      system_context:
        "Vulnerability monitoring program. Name the scanner only if the organization actually uses it; otherwise keep [vulnerability scanner].",
      guidance:
        "Include scan frequency, who triages findings, and how High/Moderate/Low items feed the POA&M (30/90/180).",
    },
    "SC-7": {
      system_context:
        "Network boundary protection for the system. Name firewall/WAF products only if known; otherwise keep [boundary protection mechanism].",
      guidance:
        "Describe default-deny, allowed flows, segmentation, and monitoring without inventing vendor products.",
    },
  };

  const POAM_FIELDS = {
    finding: "poam-finding",
    severity: "poam-severity",
    system_name: "poam-system",
    poc: "poam-poc",
    detector_source: "poam-detector",
    plugin_id: "poam-plugin",
    discovery_date: "poam-date",
    control_id: "poam-control",
    vendor_dependency: "poam-vendor",
    vendor_notes: "poam-vendor-notes",
    status: "poam-status",
    guidance: "poam-guidance",
  };

  const SSP_FIELDS = {
    control_id: "ssp-control",
    system_name: "ssp-system",
    system_context: "ssp-context",
    guidance: "ssp-guidance",
  };

  const els = {
    health: document.getElementById("health-pill"),
    exportMd: document.getElementById("btn-export-md"),
    exportCsv: document.getElementById("btn-export-csv"),
    sourcesList: document.getElementById("sources-list"),
    sourcesEmpty: document.getElementById("sources-empty"),
    sourcesStatus: document.getElementById("sources-status"),
    sourcesMode: document.getElementById("sources-mode"),
    sourcesPanel: document.getElementById("sources-panel"),
    sourcesBackdrop: document.getElementById("sources-backdrop"),
    findingsPaste: document.getElementById("findings-paste"),
    findingsFile: document.getElementById("findings-file"),
    findingsNote: document.getElementById("findings-import-note"),
    findingsRows: document.getElementById("findings-rows"),
    parseFindings: document.getElementById("btn-parse-findings"),
    formPoam: document.getElementById("form-poam"),
    formSsp: document.getElementById("form-ssp"),
    draftEmpty: document.getElementById("draft-empty"),
    draftOutput: document.getElementById("draft-output"),
    draftMeta: document.getElementById("draft-meta"),
    generatePoam: document.getElementById("btn-generate-poam"),
    generateSsp: document.getElementById("btn-generate-ssp"),
    scenarioSelect: document.getElementById("scenario-select"),
    scenarioBanner: document.getElementById("scenario-banner"),
    scenarioTitle: document.getElementById("scenario-title"),
    scenarioGoal: document.getElementById("scenario-goal"),
    scenarioLinks: document.getElementById("scenario-links"),
    goodLooks: document.getElementById("good-looks"),
    goodLooksList: document.getElementById("good-looks-list"),
  };

  const state = {
    mode: "poam",
    last: null,
    busy: false,
    fieldHelp: { poam: {}, ssp: {} },
    scenarios: [],
    scenario: null,
    findingsFilename: "",
  };

  function renderMarkdown(text) {
    const raw = window.marked.parse(text || "", { gfm: true, breaks: true });
    return window.DOMPurify.sanitize(raw);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function setExportEnabled(on) {
    els.exportMd.disabled = !on;
    els.exportCsv.disabled = !on;
  }

  function setBusy(busy) {
    state.busy = busy;
    els.generatePoam.disabled = busy;
    els.generateSsp.disabled = busy;
  }

  function renderSources(matches, modeLabel, retrieval) {
    const info = retrieval || {};
    if (window.CountGPTSources) {
      window.CountGPTSources.renderSources(els, matches, {
        afterTurn: Boolean(state.last),
        modeLabel: modeLabel || "drafting",
        retrievalStatus: info.status,
        retrievalNote: info.note,
      });
      return;
    }
    els.sourcesEmpty.hidden = Boolean(matches && matches.length);
    els.sourcesList.hidden = !els.sourcesEmpty.hidden;
  }

  function showDraft(text, meta) {
    const md = els.draftOutput.querySelector(".md");
    if (!text) {
      els.draftEmpty.classList.remove("hidden");
      els.draftOutput.classList.add("hidden");
      els.draftMeta.classList.add("hidden");
      return;
    }
    els.draftEmpty.classList.add("hidden");
    els.draftOutput.classList.remove("hidden");
    md.innerHTML = renderMarkdown(text);
    if (window.CountGPTSources && state.last && state.last.matches) {
      window.CountGPTSources.decorateCitations(md, state.last.matches, (id) => {
        toggleSources(true);
        window.CountGPTSources.highlightSource(els.sourcesList, id);
      });
    }
    if (meta && meta.mode) {
      const days = meta.severity_timeline_days;
      els.draftMeta.classList.remove("hidden");
      els.draftMeta.textContent = days
        ? `${meta.mode} · ${days}d`
        : meta.mode;
    }
  }

  function showError(message) {
    showDraft(`I could not complete that draft.\n\n${message}`, { mode: state.mode });
    els.draftOutput.querySelector(".md")?.classList.add("error");
    hideGoodLooks();
  }

  function helpEntry(key) {
    const [mode, field] = String(key || "").split(".");
    const group = state.fieldHelp[mode] || {};
    return group[field] || null;
  }

  function closeAllHelp(exceptBtn) {
    document.querySelectorAll(".field-help-pop").forEach((pop) => pop.remove());
    document.querySelectorAll(".field-help-btn[aria-expanded='true']").forEach((btn) => {
      if (btn !== exceptBtn) btn.setAttribute("aria-expanded", "false");
    });
  }

  function toggleHelp(btn) {
    const open = btn.getAttribute("aria-expanded") === "true";
    closeAllHelp(btn);
    if (open) {
      btn.setAttribute("aria-expanded", "false");
      return;
    }
    const tip = helpEntry(btn.getAttribute("data-help"));
    if (!tip) return;
    const pop = document.createElement("div");
    pop.className = "field-help-pop";
    pop.setAttribute("role", "note");
    const links = [];
    if (tip.guide) {
      links.push(`<a href="${escapeHtml(tip.guide)}">Read more in the Guide</a>`);
    }
    if (tip.glossary) {
      links.push(
        `<a href="/guide#term-${encodeURIComponent(tip.glossary)}">${escapeHtml(tip.glossary.replaceAll("-", " "))}</a>`
      );
    }
    pop.innerHTML = `
      <p><strong>${escapeHtml(tip.title || "Why this field?")}</strong></p>
      <p>${escapeHtml(tip.body || "")}</p>
      ${links.length ? `<p class="field-help-links">${links.join(" · ")}</p>` : ""}
    `;
    const field = btn.closest(".field");
    const label = field?.querySelector(".field-label");
    (label || btn).insertAdjacentElement("afterend", pop);
    btn.setAttribute("aria-expanded", "true");
  }

  function hideGoodLooks() {
    if (!els.goodLooks) return;
    els.goodLooks.classList.add("hidden");
    els.goodLooks.open = false;
    els.goodLooksList?.replaceChildren();
  }

  function showGoodLooks(items) {
    if (!els.goodLooks || !els.goodLooksList) return;
    const list = Array.isArray(items) ? items.filter(Boolean) : [];
    if (!list.length) {
      hideGoodLooks();
      return;
    }
    els.goodLooksList.replaceChildren();
    for (const item of list) {
      const li = document.createElement("li");
      const label = document.createElement("label");
      label.className = "good-looks-item";
      const box = document.createElement("input");
      box.type = "checkbox";
      const span = document.createElement("span");
      span.textContent = item;
      label.append(box, span);
      li.appendChild(label);
      els.goodLooksList.appendChild(li);
    }
    els.goodLooks.classList.remove("hidden");
    els.goodLooks.open = true;
  }

  function syncScenarioUrl(slug) {
    const url = new URL(window.location.href);
    if (slug) url.searchParams.set("scenario", slug);
    else url.searchParams.delete("scenario");
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }

  function fillFields(map, values) {
    const data = values || {};
    for (const [key, id] of Object.entries(map)) {
      const node = document.getElementById(id);
      if (!node) continue;
      node.value = data[key] != null ? String(data[key]) : "";
    }
  }

  function renderScenarioBanner(scenario) {
    if (!els.scenarioBanner) return;
    if (!scenario) {
      els.scenarioBanner.classList.add("hidden");
      if (els.scenarioTitle) els.scenarioTitle.textContent = "";
      if (els.scenarioGoal) els.scenarioGoal.textContent = "";
      els.scenarioLinks?.replaceChildren();
      return;
    }
    els.scenarioBanner.classList.remove("hidden");
    if (els.scenarioTitle) {
      els.scenarioTitle.textContent = `${scenario.title} · ${scenario.difficulty || "intro"} · ${String(scenario.mode || "").toUpperCase()}`;
    }
    if (els.scenarioGoal) {
      els.scenarioGoal.textContent = scenario.learning_goal || "";
    }
    if (els.scenarioLinks) {
      els.scenarioLinks.replaceChildren();
      if (scenario.guide) {
        const guide = document.createElement("a");
        guide.href = scenario.guide;
        guide.textContent = "Guide chapter";
        els.scenarioLinks.appendChild(guide);
      }
      if (scenario.chat_question) {
        const chat = document.createElement("a");
        chat.href = `/?q=${encodeURIComponent(scenario.chat_question)}`;
        chat.textContent = "Ask in Chat";
        els.scenarioLinks.appendChild(chat);
      }
    }
  }

  function applyScenario(slug, options) {
    const opts = options || {};
    if (!slug) {
      state.scenario = null;
      renderScenarioBanner(null);
      hideGoodLooks();
      if (!opts.keepUrl) syncScenarioUrl("");
      if (els.scenarioSelect) els.scenarioSelect.value = "";
      return;
    }
    const scenario = state.scenarios.find((item) => item.slug === slug);
    if (!scenario) return;
    state.scenario = scenario;
    setMode(scenario.mode);
    if (scenario.mode === "ssp") {
      fillFields(SSP_FIELDS, scenario.fields || {});
    } else {
      fillFields(POAM_FIELDS, scenario.fields || {});
    }
    renderScenarioBanner(scenario);
    hideGoodLooks();
    if (els.draftEmpty) els.draftEmpty.classList.remove("hidden");
    if (els.draftOutput) els.draftOutput.classList.add("hidden");
    if (els.draftMeta) els.draftMeta.classList.add("hidden");
    state.last = null;
    setExportEnabled(false);
    if (els.scenarioSelect) els.scenarioSelect.value = slug;
    if (!opts.keepUrl) syncScenarioUrl(slug);
  }

  function populateScenarioSelect() {
    if (!els.scenarioSelect) return;
    const current = els.scenarioSelect.value;
    els.scenarioSelect.replaceChildren();
    const blank = document.createElement("option");
    blank.value = "";
    blank.textContent = "Choose a practice scenario…";
    els.scenarioSelect.appendChild(blank);
    for (const item of state.scenarios) {
      const opt = document.createElement("option");
      opt.value = item.slug;
      const mode = item.mode === "ssp" ? "SSP" : "POA&M";
      const level = item.difficulty === "intermediate" ? "Intermediate" : "Intro";
      opt.textContent = `${item.title} · ${level} · ${mode}`;
      els.scenarioSelect.appendChild(opt);
    }
    if (current) els.scenarioSelect.value = current;
  }

  function applyPreset(name) {
    const preset = PRESETS[name];
    if (!preset) return;
    if (preset.severity) {
      document.getElementById("poam-severity").value = preset.severity;
    }
    if (preset.status) {
      document.getElementById("poam-status").value = preset.status;
    }
    if (preset.vendor_dependency) {
      document.getElementById("poam-vendor").value = preset.vendor_dependency;
    }
    document.getElementById("poam-guidance").value = preset.guidance || "";
  }

  function applySspStarter(controlId) {
    const starter = SSP_STARTERS[controlId];
    document.getElementById("ssp-control").value = controlId;
    if (!starter) return;
    const context = document.getElementById("ssp-context");
    const guidance = document.getElementById("ssp-guidance");
    if (!context.value.trim()) context.value = starter.system_context || "";
    if (!guidance.value.trim()) guidance.value = starter.guidance || "";
  }

  function setMode(mode) {
    state.mode = mode === "ssp" ? "ssp" : "poam";
    closeAllHelp();
    document.querySelectorAll(".mode-tabs .tab").forEach((tab) => {
      const active = tab.dataset.mode === state.mode;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    els.formPoam.classList.toggle("hidden", state.mode !== "poam");
    els.formSsp.classList.toggle("hidden", state.mode !== "ssp");
  }

  function poamPayload() {
    return {
      finding: document.getElementById("poam-finding").value.trim(),
      severity: document.getElementById("poam-severity").value,
      system_name: document.getElementById("poam-system").value.trim(),
      poc: document.getElementById("poam-poc").value.trim(),
      detector_source: document.getElementById("poam-detector").value.trim(),
      plugin_id: document.getElementById("poam-plugin").value.trim(),
      discovery_date: document.getElementById("poam-date").value.trim(),
      control_id: document.getElementById("poam-control").value.trim(),
      vendor_dependency: document.getElementById("poam-vendor").value,
      vendor_notes: document.getElementById("poam-vendor-notes").value.trim(),
      status: document.getElementById("poam-status").value,
      guidance: document.getElementById("poam-guidance").value.trim(),
    };
  }

  function sspPayload() {
    return {
      control_id: document.getElementById("ssp-control").value.trim(),
      system_name: document.getElementById("ssp-system").value.trim(),
      system_context: document.getElementById("ssp-context").value.trim(),
      guidance: document.getElementById("ssp-guidance").value.trim(),
    };
  }

  async function generate(mode) {
    if (state.busy) return;
    const payload = mode === "ssp" ? sspPayload() : poamPayload();
    if (mode === "poam" && !payload.finding) {
      window.alert("Finding / weakness is required.");
      return;
    }
    if (mode === "ssp" && !payload.control_id) {
      window.alert("Control ID is required.");
      return;
    }

    setBusy(true);
    hideGoodLooks();
    showDraft("_Generating draft…_", { mode });
    els.draftOutput.querySelector(".md")?.classList.remove("error");

    try {
      const res = await fetch(mode === "ssp" ? "/api/ssp" : "/api/poam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail || res.statusText || "Request failed";
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      state.last = {
        question: (data.meta && data.meta.question) || "",
        answer: data.draft || "",
        draft: data.draft || "",
        matches: data.matches || [],
        drafting: true,
        mode,
        fields: (data.meta && data.meta.fields) || payload,
        retrieval_status: data.retrieval_status || (data.meta && data.meta.retrieval_status) || "",
        retrieval_note: data.retrieval_note || (data.meta && data.meta.retrieval_note) || "",
      };
      showDraft(data.draft || "", data.meta);
      renderSources(data.matches, mode, {
        status: state.last.retrieval_status,
        note: state.last.retrieval_note,
      });
      setExportEnabled(Boolean((data.draft || "").trim()));
      if (state.scenario && state.scenario.mode === mode) {
        showGoodLooks(state.scenario.what_good_looks_like);
      } else {
        hideGoodLooks();
      }
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      showError(msg);
      state.last = null;
      setExportEnabled(false);
    } finally {
      setBusy(false);
    }
  }

  function downloadBlob(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function exportTurn(format) {
    if (!state.last || !state.last.answer) return;
    const res = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...state.last, format }),
    });
    if (!res.ok) {
      window.alert("Export failed. Generate a draft first.");
      return;
    }
    const text = await res.text();
    const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const kind = state.last.mode === "ssp" ? "ssp-draft" : "poam-draft";
    const ext = format === "csv" ? "csv" : "md";
    const type = format === "csv" ? "text/csv;charset=utf-8" : "text/markdown;charset=utf-8";
    downloadBlob(`countgpt-${kind}-${stamp}.${ext}`, text, type);
  }

  function toggleSources(force) {
    const open = typeof force === "boolean" ? force : !els.sourcesPanel.classList.contains("open");
    els.sourcesPanel.classList.toggle("open", open);
    els.sourcesPanel.setAttribute("aria-hidden", open ? "false" : "true");
    els.sourcesBackdrop.hidden = !open;
    document.getElementById("btn-sources")?.setAttribute("aria-expanded", open ? "true" : "false");
  }

  async function refreshHealth() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      const storeOk = Boolean(data.store_loaded);
      const ollamaOk = Boolean(data.ollama && data.ollama.reachable);
      if (data.ok) {
        els.health.className = "pill pill-ok";
        els.health.textContent = data.dry_run ? "Ready (dry-run)" : "Ready";
        els.health.title = data.dry_run
          ? `${data.model} · store loaded · dry-run (Ollama skipped)`
          : `${data.model} · store loaded · Ollama reachable`;
      } else if (storeOk && !ollamaOk) {
        els.health.className = "pill pill-warn";
        els.health.textContent = "Ollama offline";
        els.health.title = (data.ollama && data.ollama.error) || "Ollama is not reachable";
      } else if (!storeOk) {
        els.health.className = "pill pill-warn";
        els.health.textContent = "Setup needed";
        els.health.title = data.store_error || "Run python setup_data.py";
      } else {
        els.health.className = "pill pill-bad";
        els.health.textContent = "Unavailable";
      }
    } catch {
      els.health.className = "pill pill-bad";
      els.health.textContent = "Offline";
    }
  }

  async function loadFieldHelp() {
    try {
      const res = await fetch("/api/field-help");
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "field help failed");
      state.fieldHelp = {
        poam: data.poam || {},
        ssp: data.ssp || {},
      };
    } catch {
      state.fieldHelp = { poam: {}, ssp: {} };
    }
  }

  async function loadScenarios() {
    try {
      const res = await fetch("/api/scenarios");
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "scenarios failed");
      state.scenarios = Array.isArray(data.scenarios) ? data.scenarios : [];
    } catch {
      state.scenarios = [];
    }
    populateScenarioSelect();
    // Query param: /workbench?scenario=<slug> loads a practice scenario
    // from GET /api/scenarios and prefills the form. It does not auto-generate.
    const params = new URLSearchParams(window.location.search);
    const slug = (params.get("scenario") || "").trim();
    if (slug) applyScenario(slug, { keepUrl: true });
  }

  function findingsToForm(row) {
    const mapped = {
      finding: row.finding || row.synopsis || row.plugin_name || "",
      severity: row.severity || document.getElementById("poam-severity").value,
      system_name: row.system_name || row.host || "",
      detector_source: row.detector_source || "ACAS/Nessus",
      plugin_id: row.plugin_id || "",
      discovery_date: row.discovery_date || "",
      control_id: row.control_id || "",
    };
    for (const [key, value] of Object.entries(mapped)) {
      const node = document.getElementById(POAM_FIELDS[key]);
      if (node && value) node.value = value;
    }
    if (els.findingsRows) {
      els.findingsRows.querySelectorAll(".finding-row").forEach((item) => {
        item.classList.toggle("selected", item.dataset.rowId === String(row._rowId || ""));
      });
    }
  }

  function renderFindingRows(result) {
    if (!els.findingsRows || !els.findingsNote) return;
    const rows = (result && result.rows) || [];
    els.findingsNote.classList.remove("hidden");
    els.findingsNote.textContent =
      result.warning ||
      result.disclaimer ||
      "Best-effort / learning aid. Select a row to fill the form.";
    if (!rows.length) {
      els.findingsRows.hidden = true;
      els.findingsRows.replaceChildren();
      return;
    }
    els.findingsRows.hidden = false;
    els.findingsRows.replaceChildren();
    rows.forEach((row, index) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "finding-row";
      row._rowId = String(index);
      item.dataset.rowId = String(index);
      const plugin = row.plugin_id ? `Plugin ${row.plugin_id}` : "No plugin ID in paste";
      const sev = row.severity || "Severity not mapped";
      const host = row.host || row.system_name || "Host not mapped";
      item.innerHTML = `
        <span class="finding-row-meta">${escapeHtml(plugin)} · ${escapeHtml(sev)} · ${escapeHtml(host)}</span>
        <span class="finding-row-text">${escapeHtml(row.finding || row.synopsis || row.plugin_name || "Untitled row")}</span>
      `;
      item.addEventListener("click", () => findingsToForm(row));
      els.findingsRows.appendChild(item);
    });
  }

  async function parsePastedFindings() {
    const text = (els.findingsPaste && els.findingsPaste.value) || "";
    if (!text.trim()) {
      window.alert("Paste scan lines or a CSV first.");
      return;
    }
    try {
      const res = await fetch("/api/parse-findings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, filename: state.findingsFilename || "" }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail || res.statusText || "Parse failed";
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      renderFindingRows(data);
    } catch (err) {
      if (els.findingsNote) {
        els.findingsNote.classList.remove("hidden");
        els.findingsNote.textContent = err && err.message ? err.message : String(err);
      }
    }
  }

  document.querySelectorAll(".mode-tabs .tab").forEach((tab) => {
    tab.addEventListener("click", () => setMode(tab.dataset.mode));
  });

  document.querySelectorAll("#form-poam .preset").forEach((btn) => {
    btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
  });

  document.querySelectorAll("#form-ssp .preset").forEach((btn) => {
    btn.addEventListener("click", () => applySspStarter(btn.dataset.ssp));
  });

  els.formPoam.addEventListener("submit", (event) => {
    event.preventDefault();
    generate("poam");
  });
  els.formSsp.addEventListener("submit", (event) => {
    event.preventDefault();
    generate("ssp");
  });
  els.formPoam.addEventListener("reset", () => {
    queueMicrotask(() => applyScenario(""));
  });
  els.formSsp.addEventListener("reset", () => {
    queueMicrotask(() => applyScenario(""));
  });

  document.querySelectorAll(".field-help-btn").forEach((btn) => {
    btn.addEventListener("mousedown", (event) => event.preventDefault());
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggleHelp(btn);
    });
  });
  document.addEventListener("click", (event) => {
    if (event.target.closest(".field-help-btn") || event.target.closest(".field-help-pop")) {
      return;
    }
    closeAllHelp();
  });

  els.scenarioSelect?.addEventListener("change", () => {
    applyScenario(els.scenarioSelect.value);
  });

  els.parseFindings?.addEventListener("click", parsePastedFindings);
  els.findingsFile?.addEventListener("change", async () => {
    const file = els.findingsFile.files && els.findingsFile.files[0];
    if (!file) return;
    state.findingsFilename = file.name || "";
    const text = await file.text();
    if (els.findingsPaste) els.findingsPaste.value = text;
    parsePastedFindings();
  });

  els.exportMd.addEventListener("click", () => exportTurn("md"));
  els.exportCsv.addEventListener("click", () => exportTurn("csv"));

  document.querySelectorAll(".sources-toggle").forEach((btn) => {
    btn.addEventListener("click", () => toggleSources());
  });
  els.sourcesBackdrop.addEventListener("click", () => toggleSources(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") toggleSources(false);
  });

  loadFieldHelp();
  loadScenarios();
  refreshHealth();
})();
