(() => {
  const STORAGE_KEY = "countgpt.chats.v1";
  const ACTIVE_KEY = "countgpt.chats.activeId";
  const SIDEBAR_KEY = "countgpt.chats.sidebarCollapsed";
  const MAX_SESSIONS = 40;
  const TITLE_LEN = 48;

  function now() {
    return Date.now();
  }

  function newId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return `chat-${now()}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function emptySession() {
    const ts = now();
    return {
      id: newId(),
      title: "New chat",
      createdAt: ts,
      updatedAt: ts,
      messages: [],
      lastTurn: null,
    };
  }

  function readJson(key, fallback) {
    try {
      const raw = window.localStorage.getItem(key);
      if (!raw) return fallback;
      return JSON.parse(raw);
    } catch {
      return fallback;
    }
  }

  function writeJson(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  }

  function normalizeSession(raw) {
    if (!raw || typeof raw !== "object") return null;
    const id = String(raw.id || "").trim();
    if (!id) return null;
    const messages = Array.isArray(raw.messages) ? raw.messages : [];
    return {
      id,
      title: String(raw.title || "New chat"),
      createdAt: Number(raw.createdAt) || now(),
      updatedAt: Number(raw.updatedAt) || now(),
      messages: messages.map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: String(msg.content || ""),
        error: Boolean(msg.error),
        matches: Array.isArray(msg.matches) ? msg.matches : undefined,
      })),
      lastTurn: raw.lastTurn && typeof raw.lastTurn === "object" ? raw.lastTurn : null,
    };
  }

  function loadAll() {
    const data = readJson(STORAGE_KEY, null);
    const list = Array.isArray(data)
      ? data
      : data && Array.isArray(data.sessions)
        ? data.sessions
        : [];
    return list.map(normalizeSession).filter(Boolean);
  }

  function saveAll(sessions) {
    const cleaned = (sessions || []).map(normalizeSession).filter(Boolean);
    cleaned.sort((a, b) => b.updatedAt - a.updatedAt);
    const trimmed = cleaned.slice(0, MAX_SESSIONS);
    writeJson(STORAGE_KEY, { version: 1, sessions: trimmed });
    return trimmed;
  }

  function getActiveId() {
    try {
      return window.localStorage.getItem(ACTIVE_KEY) || "";
    } catch {
      return "";
    }
  }

  function setActiveId(id) {
    try {
      if (id) window.localStorage.setItem(ACTIVE_KEY, id);
      else window.localStorage.removeItem(ACTIVE_KEY);
    } catch {
      /* ignore quota / private mode */
    }
  }

  function getSession(id) {
    if (!id) return null;
    return loadAll().find((item) => item.id === id) || null;
  }

  function upsertSession(session) {
    const next = normalizeSession(session);
    if (!next) return null;
    next.updatedAt = now();
    const others = loadAll().filter((item) => item.id !== next.id);
    saveAll([next, ...others]);
    setActiveId(next.id);
    return next;
  }

  function deleteSession(id) {
    const remaining = loadAll().filter((item) => item.id !== id);
    saveAll(remaining);
    if (getActiveId() === id) {
      setActiveId(remaining[0] ? remaining[0].id : "");
    }
    return remaining;
  }

  function titleFromMessages(messages) {
    const first = (messages || []).find((msg) => msg.role === "user" && String(msg.content || "").trim());
    if (!first) return "New chat";
    const compact = String(first.content).replace(/\s+/g, " ").trim();
    if (compact.length <= TITLE_LEN) return compact;
    return `${compact.slice(0, TITLE_LEN - 1).trim()}…`;
  }

  function formatTime(ts) {
    const date = new Date(Number(ts) || now());
    const diff = Date.now() - date.getTime();
    if (diff < 45 * 1000) return "Just now";
    if (diff < 60 * 60 * 1000) return `${Math.max(1, Math.round(diff / 60000))}m ago`;
    if (diff < 24 * 60 * 60 * 1000) return `${Math.max(1, Math.round(diff / 3600000))}h ago`;
    if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.max(1, Math.round(diff / 86400000))}d ago`;
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  function isSidebarCollapsed() {
    try {
      return window.localStorage.getItem(SIDEBAR_KEY) === "1";
    } catch {
      return false;
    }
  }

  function setSidebarCollapsed(collapsed) {
    try {
      window.localStorage.setItem(SIDEBAR_KEY, collapsed ? "1" : "0");
    } catch {
      /* ignore */
    }
  }

  window.CountGPTHistory = {
    STORAGE_KEY,
    emptySession,
    loadAll,
    saveAll,
    getActiveId,
    setActiveId,
    getSession,
    upsertSession,
    deleteSession,
    titleFromMessages,
    formatTime,
    isSidebarCollapsed,
    setSidebarCollapsed,
  };
})();
