const log = document.getElementById("log");
const pending = document.getElementById("pending");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-in");
const q = document.getElementById("q");
const list = document.getElementById("list");
let history = [];
let lastActions = [];

function bubble(role, text) {
  const d = document.createElement("div");
  d.className = "bubble " + (role === "user" ? "user" : "bot");
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function showPending(actions) {
  lastActions = actions || [];
  if (!lastActions.length) {
    pending.classList.add("hidden");
    pending.innerHTML = "";
    return;
  }
  pending.classList.remove("hidden");
  pending.innerHTML =
    "<strong>Propuesta: " +
    lastActions.length +
    " a Trash</strong><ul>" +
    lastActions
      .slice(0, 30)
      .map((a) => "<li><code>" + a.id + "</code> — " + (a.reason || "") + "</li>")
      .join("") +
    "</ul><button type='button' id='confirm-trash'>Confirmar Trash</button> " +
    "<button type='button' id='cancel-trash'>Cancelar</button>";
  document.getElementById("confirm-trash").onclick = async () => {
    const ids = lastActions.map((a) => a.id);
    const r = await fetch("/api/confirm-trash", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids }),
    });
    const data = await r.json();
    bubble("bot", "Trash: " + data.trashed + (data.errors?.length ? " · errs: " + data.errors.join("; ") : ""));
    showPending([]);
    setTimeout(() => location.reload(), 800);
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

if (q && list) {
  q.addEventListener("input", () => {
    const v = q.value.toLowerCase();
    list.querySelectorAll(".house").forEach((li) => {
      li.style.display = !v || (li.dataset.text || "").toLowerCase().includes(v) ? "" : "none";
    });
  });
}

const btnSync = document.getElementById("btn-sync");
if (btnSync) {
  btnSync.onclick = async () => {
    btnSync.disabled = true;
    btnSync.textContent = "Sync…";
    try {
      const r = await fetch("/api/sync", { method: "POST" });
      const d = await r.json();
      bubble("bot", "Sync: +" + d.fetched + " (total " + d.total + ")");
      setTimeout(() => location.reload(), 600);
    } catch (err) {
      bubble("bot", "Sync falló: " + err);
    } finally {
      btnSync.disabled = false;
      btnSync.textContent = "Sync IMAP";
    }
  };
}
