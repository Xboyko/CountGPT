(() => {
  const EXAMPLES = [
    "What is an SSP?",
    "What does AC-2 require?",
    "SSP vs POA&M?",
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
    sourcesStatus: document.getElementById("sources-status"),
    sourcesMode: document.getElementById("sources-mode"),
    sourcesPanel: document.getElementById("sources-panel"),
    sourcesBackdrop: document.getElementById("sources-backdrop"),
    sourcesCount: document.getElementById("sources-count"),
    sourcesToggle: document.getElementById("btn-sources"),
    health: document.getElementById("health-pill"),
    chatShell: document.getElementById("chat-shell"),
    historySidebar: document.getElementById("history-sidebar"),
    historyList: document.getElementById("history-list"),
    historyOpen: document.getElementById("btn-history-open"),
    historyClose: document.getElementById("btn-history-close"),
    historyExpand: document.getElementById("btn-history-expand"),
    historyBackdrop: document.getElementById("history-backdrop"),
  };

  const store = window.CountGPTHistory;

  const state = {
    sessionId: "",
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
      <h2>Ask a control question</h2>
      <p>Answers cite retrieved NIST SP 800-53 controls. Open Sources to inspect them. New to the terms? Start with the <a href="/guide">learning guide</a>. For a structured draft, use the <a href="/workbench">workbench</a>.</p>
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
        const md = bubble.querySelector(".md");
        if (md && msg.matches && window.CountGPTSources) {
          window.CountGPTSources.decorateCitations(md, msg.matches, (id) => {
            toggleSources(true);
            window.CountGPTSources.highlightSource(els.sourcesList, id);
          });
        }
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

  function updateSourcesCount(matches) {
    const n = (matches || []).length;
    if (!els.sourcesCount) return;
    if (n) {
      els.sourcesCount.hidden = false;
      els.sourcesCount.classList.remove("hidden");
      els.sourcesCount.textContent = String(n);
    } else {
      els.sourcesCount.hidden = true;
      els.sourcesCount.classList.add("hidden");
      els.sourcesCount.textContent = "";
    }
  }

  function renderSources(matches, drafting, explain, retrieval) {
    const info = retrieval || {};
    if (window.CountGPTSources) {
      window.CountGPTSources.renderSources(els, matches, {
        afterTurn: Boolean(state.lastTurn),
        explain,
        modeLabel: drafting ? "drafting" : explain ? "explain" : state.lastTurn ? "lookup" : "",
        retrievalStatus: info.status,
        retrievalNote: info.note,
      });
    } else {
      els.sourcesEmpty.hidden = Boolean(matches && matches.length);
      els.sourcesList.hidden = !els.sourcesEmpty.hidden;
    }
    updateSourcesCount(matches);
  }

  function persistCurrent() {
    if (!store || !state.sessionId) return;
    const session = {
      id: state.sessionId,
      title: store.titleFromMessages(state.history),
      createdAt: (store.getSession(state.sessionId) || {}).createdAt,
      messages: state.history,
      lastTurn: state.lastTurn,
    };
    if (!session.createdAt) session.createdAt = Date.now();
    if (!session.messages.length) return;
    store.upsertSession(session);
    renderHistoryList();
  }

  function applySession(session) {
    state.sessionId = session.id;
    state.history = Array.isArray(session.messages) ? session.messages : [];
    state.lastTurn = session.lastTurn || null;
    if (store) store.setActiveId(session.id);
    renderMessages();
    const matches = (state.lastTurn && state.lastTurn.matches) || [];
    renderSources(
      matches,
      Boolean(state.lastTurn && state.lastTurn.drafting),
      Boolean(state.lastTurn && state.lastTurn.explain),
      {
        status: (state.lastTurn && state.lastTurn.retrieval_status) || "",
        note: (state.lastTurn && state.lastTurn.retrieval_note) || "",
      }
    );
    setExportEnabled(Boolean(state.lastTurn && (state.lastTurn.answer || "").trim()));
    renderHistoryList();
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
    persistCurrent();
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
      state.history.push({
        role: "assistant",
        content: data.answer || "",
        matches: data.matches || [],
      });
      state.lastTurn = {
        question: message,
        answer: data.answer || "",
        matches: data.matches || [],
        drafting: Boolean(data.drafting),
        explain: Boolean(data.explain),
        retrieval_status: data.retrieval_status || "",
        retrieval_note: data.retrieval_note || "",
      };
      renderSources(data.matches, data.drafting, data.explain, {
        status: data.retrieval_status,
        note: data.retrieval_note,
      });
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
      persistCurrent();
      removeTyping();
      renderMessages();
      setBusy(false);
      els.input.focus();
    }
  }

  function newChat() {
    if (store && !state.history.length && store.getSession(state.sessionId)) {
      els.input.focus();
      return;
    }
    const session = store ? store.emptySession() : { id: `chat-${Date.now()}`, messages: [], lastTurn: null };
    if (store) store.setActiveId(session.id);
    applySession(session);
    toggleHistory(false);
    els.input.focus();
  }

  function selectSession(id) {
    if (!store || !id || id === state.sessionId) {
      toggleHistory(false);
      return;
    }
    const session = store.getSession(id);
    if (!session) return;
    applySession(session);
    toggleHistory(false);
    els.input.focus();
  }

  function deleteSession(id) {
    if (!store || !id) return;
    store.deleteSession(id);
    if (id === state.sessionId) {
      const next = store.loadAll()[0] || store.emptySession();
      applySession(next);
    } else {
      renderHistoryList();
    }
  }

  function renderHistoryList() {
    if (!els.historyList) return;
    const sessions = store ? store.loadAll() : [];
    const visible = sessions.filter((item) => item.messages && item.messages.length);
    els.historyList.replaceChildren();
    if (!visible.length) {
      const empty = document.createElement("p");
      empty.className = "history-empty";
      empty.textContent = "No saved chats yet.";
      els.historyList.appendChild(empty);
      return;
    }
    for (const session of visible) {
      const row = document.createElement("div");
      row.className = "history-item";
      if (session.id === state.sessionId) row.classList.add("active");

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "history-item-main";
      btn.title = session.title;
      btn.innerHTML = `
        <span class="history-item-title">${escapeHtml(session.title)}</span>
        <span class="history-item-time">${escapeHtml(store.formatTime(session.updatedAt))}</span>
      `;
      btn.addEventListener("click", () => selectSession(session.id));

      const del = document.createElement("button");
      del.type = "button";
      del.className = "btn icon history-item-delete";
      del.setAttribute("aria-label", `Delete ${session.title}`);
      del.title = "Delete chat";
      del.textContent = "×";
      del.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        deleteSession(session.id);
      });

      row.append(btn, del);
      els.historyList.appendChild(row);
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
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

  function isMobile() {
    return window.matchMedia("(max-width: 880px)").matches;
  }

  function toggleSources(force) {
    const open = typeof force === "boolean" ? force : !els.sourcesPanel.classList.contains("open");
    els.sourcesPanel.classList.toggle("open", open);
    els.sourcesPanel.setAttribute("aria-hidden", open ? "false" : "true");
    els.sourcesBackdrop.hidden = !open;
    if (els.sourcesToggle) els.sourcesToggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function applySidebarCollapsed(collapsed) {
    els.chatShell.classList.toggle("history-collapsed", collapsed);
    els.historySidebar.classList.toggle("collapsed", collapsed);
    if (store) store.setSidebarCollapsed(collapsed);
  }

  function toggleHistory(force) {
    if (!isMobile()) {
      if (typeof force === "boolean") {
        applySidebarCollapsed(!force);
        return;
      }
      applySidebarCollapsed(!els.chatShell.classList.contains("history-collapsed"));
      return;
    }
    const open = typeof force === "boolean" ? force : !els.historySidebar.classList.contains("open");
    els.historySidebar.classList.toggle("open", open);
    if (els.historyBackdrop) els.historyBackdrop.hidden = !open;
  }

  function loraHealthNote(data) {
    const lora = data.lora || {};
    if (lora.loaded) return " · LoRA loaded (drafts)";
    if (lora.available) return " · LoRA available (drafts)";
    if (lora.force_ollama) return " · LoRA disabled (FORCE_OLLAMA)";
    if (lora.adapter_present && !lora.cuda_available) return " · LoRA on disk, no CUDA";
    return " · drafts on Ollama";
  }

  async function refreshHealth() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      const storeOk = Boolean(data.store_loaded);
      const ollamaOk = Boolean(data.ollama && data.ollama.reachable);
      const loraLoaded = Boolean(data.lora && data.lora.loaded);
      if (data.ok) {
        els.health.className = "pill pill-ok";
        els.health.textContent = data.dry_run
          ? "Ready (dry-run)"
          : loraLoaded
            ? "Ready · LoRA"
            : "Ready";
        els.health.title = data.dry_run
          ? `${data.model} · store loaded · dry-run (Ollama skipped)${loraHealthNote(data)}`
          : `${data.model} · store loaded · Ollama reachable${loraHealthNote(data)}`;
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

  function restoreOrCreate() {
    if (!store) {
      applySession({ id: `chat-${Date.now()}`, messages: [], lastTurn: null });
      return;
    }
    const activeId = store.getActiveId();
    const existing = activeId && store.getSession(activeId);
    if (existing) {
      applySession(existing);
      return;
    }
    const newest = store.loadAll().find((item) => item.messages && item.messages.length);
    applySession(newest || store.emptySession());
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

  els.newChat.addEventListener("click", newChat);
  els.exportMd.addEventListener("click", () => exportTurn("md"));
  els.exportCsv.addEventListener("click", () => exportTurn("csv"));

  document.querySelectorAll(".sources-toggle").forEach((btn) => {
    btn.addEventListener("click", () => toggleSources());
  });
  els.sourcesBackdrop.addEventListener("click", () => toggleSources(false));
  els.historyOpen?.addEventListener("click", () => toggleHistory(true));
  els.historyClose?.addEventListener("click", () => toggleHistory(false));
  els.historyExpand?.addEventListener("click", () => toggleHistory(true));
  els.historyBackdrop?.addEventListener("click", () => toggleHistory(false));

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    toggleSources(false);
    if (isMobile()) toggleHistory(false);
  });

  window.addEventListener("resize", () => {
    if (!isMobile()) {
      els.historySidebar.classList.remove("open");
      if (els.historyBackdrop) els.historyBackdrop.hidden = true;
    }
  });

  if (store && store.isSidebarCollapsed()) {
    applySidebarCollapsed(true);
  }

  restoreOrCreate();
  prefillFromQuery();
  refreshHealth();
})();
