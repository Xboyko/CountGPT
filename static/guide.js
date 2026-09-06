(() => {
  const els = {
    health: document.getElementById("health-pill"),
    search: document.getElementById("glossary-search"),
    status: document.getElementById("glossary-status"),
    list: document.getElementById("glossary-list"),
    tocLinks: [...document.querySelectorAll(".guide-toc nav a")],
    chapters: [...document.querySelectorAll(".guide-chapter")],
  };

  const state = {
    terms: [],
    byId: new Map(),
  };

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function termHaystack(term) {
    return [
      term.term,
      term.full,
      term.definition,
      ...(term.aliases || []),
    ]
      .join(" ")
      .toLowerCase();
  }

  function renderGlossary(filter) {
    const q = (filter || "").trim().toLowerCase();
    const matches = state.terms.filter((term) => !q || termHaystack(term).includes(q));
    els.list.replaceChildren();
    if (!matches.length) {
      els.status.hidden = false;
      els.status.textContent = q
        ? `No glossary entries match “${filter.trim()}”.`
        : "Glossary is empty.";
      return;
    }
    els.status.hidden = true;
    for (const term of matches) {
      const card = document.createElement("article");
      card.className = "glossary-card";
      card.id = `term-${term.id}`;
      const full = term.full && term.full !== term.term ? ` · ${escapeHtml(term.full)}` : "";
      card.innerHTML = `
        <h3><span class="glossary-term">${escapeHtml(term.term)}</span>${full}</h3>
        <p>${escapeHtml(term.definition)}</p>
      `;
      els.list.appendChild(card);
    }
  }

  function closeTermPop(chip) {
    const pop = chip.nextElementSibling;
    if (pop && pop.classList.contains("term-pop")) pop.remove();
    chip.setAttribute("aria-expanded", "false");
  }

  function bindTermChips() {
    document.querySelectorAll(".term-chip[data-term]").forEach((chip) => {
      chip.addEventListener("click", () => {
        const id = chip.getAttribute("data-term");
        const term = state.byId.get(id);
        if (!term) {
          document.getElementById("glossary")?.scrollIntoView({ behavior: "smooth" });
          if (els.search) {
            els.search.value = chip.textContent.trim();
            renderGlossary(els.search.value);
          }
          return;
        }
        const open = chip.getAttribute("aria-expanded") === "true";
        document.querySelectorAll(".term-chip[aria-expanded='true']").forEach(closeTermPop);
        if (open) return;
        const pop = document.createElement("span");
        pop.className = "term-pop";
        pop.setAttribute("role", "note");
        pop.innerHTML = `<strong>${escapeHtml(term.term)}</strong> — ${escapeHtml(term.definition)}`;
        chip.insertAdjacentElement("afterend", pop);
        chip.setAttribute("aria-expanded", "true");
      });
    });
  }

  function setActiveToc() {
    const marker = 140;
    let current = els.chapters[0];
    for (const chapter of els.chapters) {
      const rect = chapter.getBoundingClientRect();
      if (rect.top <= marker && rect.bottom > marker) {
        current = chapter;
        break;
      }
    }
    const id = current ? `#${current.id}` : "";
    for (const link of els.tocLinks) {
      link.classList.toggle("active", link.getAttribute("href") === id);
    }
  }

  async function loadGlossary() {
    try {
      const res = await fetch("/api/glossary");
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Glossary failed to load");
      state.terms = data.terms || [];
      state.byId = new Map(state.terms.map((term) => [term.id, term]));
      renderGlossary("");
      bindTermChips();
    } catch (err) {
      els.status.hidden = false;
      els.status.textContent =
        err && err.message
          ? err.message
          : "Could not load the glossary. Check that the server is running.";
    }
  }

  async function refreshHealth() {
    if (!els.health) return;
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

  els.search?.addEventListener("input", () => renderGlossary(els.search.value));
  document.querySelector(".guide-main")?.addEventListener("scroll", setActiveToc);
  window.addEventListener("hashchange", setActiveToc);

  loadGlossary();
  refreshHealth();
  setActiveToc();
})();
