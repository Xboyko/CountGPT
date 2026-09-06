(() => {
  const EXAMPLES = [
    "What is an SSP?",
    "SSP vs POA&M?",
    "What is AC-2?",
    "What does AC-2 require?",
    "Draft a POA&M for a Moderate finding: weak cipher suite on a web server.",
  ];

  const els = {
    messages: document.getElementById("messages"),
    form: document.getElementById("composer"),
    input: document.getElementById("input"),
    send: document.getElementById("btn-send"),
    newChat: document.getElementById("btn-new"),
    exportMd: document.getElementById("btn-export-md"),
    exportCsv: document.getElementById("btn-export-csv"),
    sourcesList: document.getElementById("sources-list"),
    sourcesEmpty: document.getElementById("sources-empty"),
    sourcesMode: document.getElementById("sources-mode"),
    sourcesPanel: document.getElementById("sources-panel"),
    sourcesBackdrop: document.getElementById("sources-backdrop"),
    health: document.getElementById("health-pill"),
  };

  const state = {
    history: [],
    lastTurn: null,
    busy: false,
  };

  function renderMarkdown(text) {
    const raw = window.marked.parse(text || "", { gfm: true, breaks: true });
    return window.DOMPurify.sanitize(raw);
  }

  function scrollToBottom() {
    els.messages.scrollTop = els.messages.scrollHeight;
  }

  function setBusy(busy) {
    state.busy = busy;
    els.send.disabled = busy;
    els.input.disabled = busy;
  }

  function setExportEnabled(on) {
    els.exportMd.disabled = !on;
    els.exportCsv.disabled = !on;
  }

  function emptyState() {
    const wrap = document.createElement("div");
    wrap.className = "empty-state";
    wrap.innerHTML = `
      <h2>Ask a control question or request a draft</h2>
      <p>Answers are grounded in retrieved NIST SP 800-53 controls. Cite IDs stay on the right. New to the terms? Start with the <a href="/guide">learning guide</a>. For a structured POA&amp;M or SSP draft, open the <a href="/workbench">workbench</a>.</p>
    `;
    const row = document.createElement("div");
    row.className = "examples";
    EXAMPLES.forEach((text) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip";
      btn.textContent = text;
      btn.addEventListener("click", () => {
        els.input.value = text;
        els.input.focus();
        resizeInput();
      });
      row.appendChild(btn);
    });
    wrap.appendChild(row);
    return wrap;
  }

  function renderMessages() {
    els.messages.replaceChildren();
    if (!state.history.length) {
      els.messages.appendChild(emptyState());
      return;
    }
    for (const msg of state.history) {
      const row = document.createElement("div");
      row.className = `bubble-row ${msg.role}`;
      const bubble = document.createElement("div");
      bubble.className = `bubble ${msg.role}${msg.error ? " error" : ""}`;
      if (msg.role === "assistant") {
        bubble.innerHTML = `<div class="md">${renderMarkdown(msg.content)}</div>`;
      } else {
        bubble.textContent = msg.content;
      }
      row.appendChild(bubble);
      els.messages.appendChild(row);
    }
    scrollToBottom();
  }

  function addTyping() {
    const row = document.createElement("div");
    row.className = "bubble-row assistant";
    row.id = "typing-row";
    row.innerHTML =
      '<div class="bubble assistant"><div class="typing" aria-label="Thinking"><span></span><span></span><span></span></div></div>';
    els.messages.appendChild(row);
    scrollToBottom();
  }

  function removeTyping() {
    document.getElementById("typing-row")?.remove();
  }

  function renderSources(matches, drafting, explain) {
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
    els.sourcesMode.textContent = drafting ? "drafting" : explain ? "explain" : "lookup";
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

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function historyForApi() {
    return state.history
      .filter((m) => m.role === "user" || m.role === "assistant")
      .map((m) => ({ role: m.role, content: m.content }));
  }

  async function sendMessage(text) {
    const message = (text || "").trim();
    if (!message || state.busy) return;

    if (!state.history.length) {
      els.messages.replaceChildren();
    }

    const pendingHistory = historyForApi();
    state.history.push({ role: "user", content: message });
    renderMessages();
    els.input.value = "";
    resizeInput();
    setBusy(true);
    addTyping();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history: pendingHistory }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail || res.statusText || "Request failed";
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      state.history.push({ role: "assistant", content: data.answer || "" });
      state.lastTurn = {
        question: message,
        answer: data.answer || "",
        matches: data.matches || [],
        drafting: Boolean(data.drafting),
        explain: Boolean(data.explain),
      };
      renderSources(data.matches, data.drafting, data.explain);
      setExportEnabled(Boolean((data.answer || "").trim()));
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      state.history.push({
        role: "assistant",
        content: `I could not complete that turn.\n\n${msg}`,
        error: true,
      });
      setExportEnabled(false);
    } finally {
      removeTyping();
      renderMessages();
      setBusy(false);
      els.input.focus();
    }
  }

  function resetChat() {
    state.history = [];
    state.lastTurn = null;
    renderMessages();
    renderSources([], false, false);
    setExportEnabled(false);
    els.input.focus();
  }

  function prefillFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const q = (params.get("q") || "").trim();
    if (!q) return;
    els.input.value = q;
    resizeInput();
    els.input.focus();
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
    if (!state.lastTurn || !state.lastTurn.answer) return;
    const res = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...state.lastTurn, format }),
    });
    if (!res.ok) {
      window.alert("Export failed. Try again after a successful answer.");
      return;
    }
    const text = await res.text();
    const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const kind = state.lastTurn.drafting ? "poam-draft" : "lookup";
    const ext = format === "csv" ? "csv" : "md";
    const type = format === "csv" ? "text/csv;charset=utf-8" : "text/markdown;charset=utf-8";
    downloadBlob(`countgpt-${kind}-${stamp}.${ext}`, text, type);
  }

  function resizeInput() {
    els.input.style.height = "auto";
    els.input.style.height = `${Math.min(els.input.scrollHeight, 160)}px`;
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

  els.form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(els.input.value);
  });

  els.input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(els.input.value);
    }
  });
  els.input.addEventListener("input", resizeInput);

  els.newChat.addEventListener("click", resetChat);
  els.exportMd.addEventListener("click", () => exportTurn("md"));
  els.exportCsv.addEventListener("click", () => exportTurn("csv"));

  document.querySelectorAll(".sources-toggle").forEach((btn) => {
    btn.addEventListener("click", () => toggleSources());
  });
  els.sourcesBackdrop.addEventListener("click", () => toggleSources(false));

  resetChat();
  prefillFromQuery();
  refreshHealth();
})();
