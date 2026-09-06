(() => {
  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function statusCopy(status, note, { afterTurn, explain } = {}) {
    if (!afterTurn) {
      return {
        kind: "idle",
        title: "",
        body:
          note ||
          "No retrieval yet. Ask a question or name a control ID (for example AC-2).",
      };
    }
    if (status === "empty") {
      return {
        kind: "empty",
        title: "No confident match",
        body:
          note ||
          "Retrieval was empty or below the similarity floor. No control citations were invented.",
      };
    }
    if (status === "weak") {
      return {
        kind: "weak",
        title: "Weak / low-confidence match",
        body:
          note ||
          "Only tentative semantic matches were found. Treat IDs as unverified.",
      };
    }
    if (explain && !(status === "ok")) {
      return {
        kind: "empty",
        title: "No catalog citation",
        body: note || "This looks like a process question, not a named control.",
      };
    }
    return { kind: "ok", title: "", body: "" };
  }

  function renderSources(els, matches, options) {
    const opts = options || {};
    const list = matches || [];
    const status = opts.retrievalStatus || (list.length ? "ok" : "empty");
    const copy = statusCopy(status, opts.retrievalNote, {
      afterTurn: Boolean(opts.afterTurn),
      explain: Boolean(opts.explain),
    });

    if (els.sourcesMode) {
      if (opts.modeLabel) {
        els.sourcesMode.classList.remove("hidden");
        els.sourcesMode.textContent = opts.modeLabel;
      } else {
        els.sourcesMode.classList.add("hidden");
      }
    }

    if (els.sourcesStatus) {
      if (copy.title || (copy.body && copy.kind !== "idle")) {
        els.sourcesStatus.hidden = false;
        els.sourcesStatus.className = `sources-status sources-status-${copy.kind}`;
        els.sourcesStatus.innerHTML = copy.title
          ? `<strong>${escapeHtml(copy.title)}.</strong> ${escapeHtml(copy.body)}`
          : escapeHtml(copy.body);
      } else {
        els.sourcesStatus.hidden = true;
        els.sourcesStatus.replaceChildren();
      }
    }

    if (!list.length) {
      els.sourcesList.hidden = true;
      els.sourcesList.replaceChildren();
      if (els.sourcesEmpty) {
        els.sourcesEmpty.hidden = Boolean(els.sourcesStatus && !els.sourcesStatus.hidden);
        if (!els.sourcesEmpty.hidden) {
          els.sourcesEmpty.textContent = copy.body;
        }
      }
      return;
    }

    if (els.sourcesEmpty) els.sourcesEmpty.hidden = true;
    els.sourcesList.hidden = false;
    els.sourcesList.replaceChildren();
    for (const match of list) {
      const card = document.createElement("article");
      card.className = "source-card";
      if (match.used_in_answer) card.classList.add("used");
      const cid = match.id || "";
      if (cid) card.dataset.controlId = cid;
      const snippet = (match.snippet || match.text || "").trim();
      const clipped =
        snippet.length > 360 ? `${snippet.slice(0, 360).trim()}…` : snippet;
      const used = match.used_in_answer
        ? '<span class="source-used">used in answer</span>'
        : '<span class="source-unused">retrieved</span>';
      card.innerHTML = `
        <div class="source-meta">
          <span class="source-id">${escapeHtml(cid)}</span>
          <span class="source-score">${Number(match.score || 0).toFixed(2)}</span>
          <span class="source-kind">${escapeHtml(match.source || "")}</span>
          ${used}
        </div>
        <p class="source-title">${escapeHtml(match.title || "")}</p>
        <blockquote class="source-quote">${escapeHtml(clipped || "No statement text.")}</blockquote>
      `;
      card.addEventListener("click", () => highlightSource(els.sourcesList, cid));
      els.sourcesList.appendChild(card);
    }
  }

  function highlightSource(listEl, controlId) {
    if (!listEl || !controlId) return;
    listEl.querySelectorAll(".source-card").forEach((card) => {
      const on = card.dataset.controlId === controlId;
      card.classList.toggle("highlight", on);
      if (on) card.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  }

  function decorateCitations(container, matches, onChip) {
    if (!container) return;
    const ids = [...new Set((matches || []).map((m) => m.id).filter(Boolean))].sort(
      (a, b) => b.length - a.length
    );
    if (!ids.length) return;

    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest("button, a, .cite-chip, script, style")) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);

    const pattern = new RegExp(
      `\\[?(${ids.map(escapeRegExp).join("|")})\\]?`,
      "gi"
    );

    for (const node of nodes) {
      const text = node.nodeValue || "";
      if (!pattern.test(text)) continue;
      pattern.lastIndex = 0;
      const frag = document.createDocumentFragment();
      let last = 0;
      text.replace(pattern, (full, id, offset) => {
        if (offset > last) frag.appendChild(document.createTextNode(text.slice(last, offset)));
        const canonical = ids.find((item) => item.toLowerCase() === String(id).toLowerCase()) || id;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "cite-chip";
        btn.dataset.controlId = canonical;
        btn.textContent = `[${canonical}]`;
        btn.title = `Show retrieved ${canonical}`;
        btn.addEventListener("click", (event) => {
          event.preventDefault();
          if (typeof onChip === "function") onChip(canonical);
        });
        frag.appendChild(btn);
        last = offset + full.length;
        return full;
      });
      if (last < text.length) {
        frag.appendChild(document.createTextNode(text.slice(last)));
      }
      node.parentNode.replaceChild(frag, node);
    }
  }

  window.CountGPTSources = {
    escapeHtml,
    renderSources,
    highlightSource,
    decorateCitations,
    statusCopy,
  };
})();
