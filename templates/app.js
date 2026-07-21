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

function bubble(role, text) {
  const d = document.createElement("div");
  d.className = "bubble " + (role === "user" ? "user" : "bot");
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function applyFilters() {
  const v = (q?.value || "").toLowerCase();
  list.querySelectorAll(".row").forEach((li) => {
    const okFolder = !activeFolder || li.dataset.folder === activeFolder;
    const okText = !v || (li.dataset.text || "").toLowerCase().includes(v);
    li.style.display = okFolder && okText ? "" : "none";
  });
}

// sidebar: filtro por carpeta
document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"));
    item.classList.add("active");
    activeFolder = item.dataset.folder || "";
    applyFilters();
  });
});

if (q && list) q.addEventListener("input", applyFilters);

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
