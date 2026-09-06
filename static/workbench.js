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

  const els = {
    health: document.getElementById("health-pill"),
    exportMd: document.getElementById("btn-export-md"),
    exportCsv: document.getElementById("btn-export-csv"),
    sourcesList: document.getElementById("sources-list"),
    sourcesEmpty: document.getElementById("sources-empty"),
    sourcesMode: document.getElementById("sources-mode"),
    sourcesPanel: document.getElementById("sources-panel"),
    sourcesBackdrop: document.getElementById("sources-backdrop"),
    formPoam: document.getElementById("form-poam"),
    formSsp: document.getElementById("form-ssp"),
    draftEmpty: document.getElementById("draft-empty"),
    draftOutput: document.getElementById("draft-output"),
    draftMeta: document.getElementById("draft-meta"),
    generatePoam: document.getElementById("btn-generate-poam"),
    generateSsp: document.getElementById("btn-generate-ssp"),
  };

  const state = {
    mode: "poam",
    last: null,
    busy: false,
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

  function renderSources(matches, modeLabel) {
    const list = matches || [];
    if (!list.length) {
      els.sourcesList.hidden = true;
      els.sourcesList.replaceChildren();
      els.sourcesEmpty.hidden = false;
      els.sourcesMode.classList.add("hidden");
      return;
    }
    els.sourcesEmpty.hidden = true;
    els.sourcesList.hidden = false;
    els.sourcesMode.classList.remove("hidden");
    els.sourcesMode.textContent = modeLabel || "drafting";
    els.sourcesList.replaceChildren();
    for (const match of list) {
      const card = document.createElement("article");
      card.className = "source-card";
      const text = (match.text || "").trim();
      const clipped = text.length > 420 ? `${text.slice(0, 420).trim()}…` : text;
      card.innerHTML = `
        <div class="source-meta">
          <span class="source-id">${escapeHtml(match.id || "")}</span>
          <span class="source-score">${Number(match.score || 0).toFixed(2)}</span>
          <span class="source-kind">${escapeHtml(match.source || "")}</span>
        </div>
        <p class="source-title">${escapeHtml(match.title || "")}</p>
        <p class="source-text">${escapeHtml(clipped || "No statement text.")}</p>
      `;
      els.sourcesList.appendChild(card);
    }
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
      };
      showDraft(data.draft || "", data.meta);
      renderSources(data.matches, mode);
      setExportEnabled(Boolean((data.draft || "").trim()));
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
    els.sourcesBackdrop.hidden = !open;
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

  els.exportMd.addEventListener("click", () => exportTurn("md"));
  els.exportCsv.addEventListener("click", () => exportTurn("csv"));

  document.querySelectorAll(".sources-toggle").forEach((btn) => {
    btn.addEventListener("click", () => toggleSources());
  });
  els.sourcesBackdrop.addEventListener("click", () => toggleSources(false));

  refreshHealth();
})();
