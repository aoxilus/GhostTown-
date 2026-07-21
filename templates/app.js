const log = document.getElementById("log");
const pending = document.getElementById("pending");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-in");
const q = document.getElementById("q");
const list = document.getElementById("list");
const guardian = document.getElementById("guardian");
let history = [];
let lastActions = [];
let activeFolder = "";
let allMessages = [];
let currentPage = 1;
const PAGE_SIZE = 250;

function bubble(role, text) {
  const d = document.createElement("div");
  d.className = "bubble " + (role === "user" ? "user" : "bot");
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function filteredMessages() {
  const v = (q?.value || "").toLowerCase();
  const hasAllMail = allMessages.some((m) => m.folder === "[Gmail]/All Mail");
  return allMessages.filter((m) => {
    const okFolder = activeFolder
      ? m.folder === activeFolder
      : !hasAllMail || m.folder === "[Gmail]/All Mail";
    const haystack = `${m.from} ${m.subject} ${m.snippet}`.toLowerCase();
    return okFolder && (!v || haystack.includes(v));
  });
}

function addText(parent, tag, className, text) {
  const el = document.createElement(tag);
  el.className = className;
  el.textContent = text;
  parent.appendChild(el);
  return el;
}

function renderPage() {
  const rows = filteredMessages();
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(Math.max(1, currentPage), pageCount);
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageRows = rows.slice(start, start + PAGE_SIZE);
  list.replaceChildren();

  if (!pageRows.length) {
    addText(list, "li", "empty", activeFolder
      ? "Esta carpeta todavía no se ha descargado a la PC."
      : "No se encontraron correos.");
  }

  pageRows.forEach((m) => {
    const li = document.createElement("li");
    li.className = "row";
    const link = document.createElement("a");
    link.href = `/${m.href}`;
    const sender = (m.from.split("<")[0].trim() || m.from);
    addText(link, "span", "col-from", sender);
    const subject = document.createElement("span");
    subject.className = "col-subj";
    addText(subject, "strong", "", m.subject);
    addText(subject, "span", "snippet", ` — ${m.snippet}`);
    link.appendChild(subject);
    if (m.has_attachments) addText(link, "span", "clip", "📎");
    addText(link, "span", "col-date", m.date);
    li.appendChild(link);
    list.appendChild(li);
  });

  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  document.getElementById("page-info").textContent =
    `${first.toLocaleString()}–${last.toLocaleString()} de ${rows.length.toLocaleString()}`;
  ["page-prev", "page-prev-bottom"].forEach((id) => {
    document.getElementById(id).disabled = currentPage <= 1;
  });
  ["page-next", "page-next-bottom"].forEach((id) => {
    document.getElementById(id).disabled = currentPage >= pageCount;
  });
}

function changePage(delta) {
  currentPage += delta;
  renderPage();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// sidebar: filtro por carpeta
document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"));
    item.classList.add("active");
    activeFolder = item.dataset.folder || "";
    currentPage = 1;
    renderPage();
  });
});

if (q && list) q.addEventListener("input", () => {
  currentPage = 1;
  renderPage();
});

["page-prev", "page-prev-bottom"].forEach((id) => {
  document.getElementById(id).onclick = () => changePage(-1);
});
["page-next", "page-next-bottom"].forEach((id) => {
  document.getElementById(id).onclick = () => changePage(1);
});

fetch("/messages.json")
  .then((r) => r.json())
  .then((messages) => {
    allMessages = messages;
    renderPage();
  })
  .catch(() => addText(list, "li", "empty", "No se pudo cargar el índice local."));

const lastSync = document.getElementById("last-sync");
if (lastSync && lastSync.dateTime && lastSync.dateTime !== "Nunca") {
  const date = new Date(lastSync.dateTime);
  if (!Number.isNaN(date.getTime())) lastSync.textContent = date.toLocaleString();
}

// panel Guardián
const btnGuardian = document.getElementById("btn-guardian");
const btnClose = document.getElementById("btn-close-guardian");
if (btnGuardian) btnGuardian.onclick = () => guardian.classList.toggle("hidden");
if (btnClose) btnClose.onclick = () => guardian.classList.add("hidden");

function showPending(actions) {
  lastActions = actions || [];
  if (!lastActions.length) {
    pending.classList.add("hidden");
    pending.innerHTML = "";
    return;
  }
  pending.classList.remove("hidden");
  pending.innerHTML =
    "<strong>Propuesta: mover " + lastActions.length + " a la papelera</strong><ul>" +
    lastActions.slice(0, 30).map((a) => "<li>" + (a.reason || a.id) + "</li>").join("") +
    "</ul><button type='button' id='confirm-trash'>Confirmar</button> " +
    "<button type='button' id='cancel-trash'>Cancelar</button>";
  document.getElementById("confirm-trash").onclick = async () => {
    const ids = lastActions.map((a) => a.id);
    const r = await fetch("/api/confirm-trash", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids }),
    });
    const data = await r.json();
    bubble("bot", "Movidos a papelera: " + data.trashed + (data.errors?.length ? " · errores: " + data.errors.join("; ") : ""));
    showPending([]);
    setTimeout(() => location.reload(), 900);
  };
  document.getElementById("cancel-trash").onclick = () => showPending([]);
}

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    bubble("user", message);
    input.value = "";
    history.push({ role: "user", content: message });
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history: history.slice(-8) }),
    });
    const data = await r.json();
    bubble("bot", data.reply || "(sin respuesta)");
    history.push({ role: "assistant", content: data.reply || "" });
    showPending(data.actions || []);
  });
}

const btnSync = document.getElementById("btn-sync");
if (btnSync) {
  btnSync.onclick = async () => {
    btnSync.disabled = true;
    btnSync.textContent = "Bajando…";
    try {
      const r = await fetch("/api/sync", { method: "POST" });
      const d = await r.json();
      alert("Correos nuevos: " + d.fetched + " (total " + d.total + ")");
      location.reload();
    } catch (err) {
      alert("Sync falló: " + err);
      btnSync.disabled = false;
      btnSync.textContent = "Sync";
    }
  };
}
