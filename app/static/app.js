import { initializeApp } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "https://www.gstatic.com/firebasejs/12.2.1/firebase-auth.js";

const elements = {
  landing: document.querySelector("#landing"),
  dashboard: document.querySelector("#dashboard"),
  account: document.querySelector("#account"),
  userName: document.querySelector("#user-name"),
  signIn: document.querySelector("#sign-in"),
  signOut: document.querySelector("#sign-out"),
  form: document.querySelector("#chat-form"),
  message: document.querySelector("#message"),
  send: document.querySelector("#send"),
  status: document.querySelector("#status"),
  conversation: document.querySelector("#conversation"),
  history: document.querySelector("#history-list"),
  newReflection: document.querySelector("#new-reflection"),
  clearHistory: document.querySelector("#clear-history"),
  toast: document.querySelector("#toast"),
};

let auth;
let currentUser;
let currentMode = "clarity";

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove("hidden");
  window.setTimeout(() => elements.toast.classList.add("hidden"), 5000);
}

function setSignedIn(signedIn) {
  elements.landing.classList.toggle("hidden", signedIn);
  elements.dashboard.classList.toggle("hidden", !signedIn);
  elements.account.classList.toggle("hidden", !signedIn);
}

async function api(path, options = {}) {
  if (!currentUser) throw new Error("Please sign in first.");
  const token = await currentUser.getIdToken();
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "The request could not be completed.");
  return body;
}

function messageCard(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const label = document.createElement("span");
  label.className = "message-label";
  label.textContent = role === "user" ? "You" : "Gemini";
  const content = document.createElement("p");
  content.textContent = text;
  article.append(label, content);
  return article;
}

function renderConversation(prompt, response) {
  elements.conversation.replaceChildren(
    messageCard("user", prompt),
    messageCard("assistant", response),
  );
}

function renderHistory(items) {
  elements.history.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "Your saved reflections will appear here.";
    elements.history.append(empty);
    return;
  }
  for (const item of items) {
    const button = document.createElement("button");
    button.className = "history-item";
    const title = document.createElement("strong");
    title.textContent = item.prompt.slice(0, 72);
    const meta = document.createElement("span");
    meta.textContent = `${item.mode} · ${new Date(item.created_at).toLocaleDateString()}`;
    button.append(title, meta);
    button.addEventListener("click", () => renderConversation(item.prompt, item.response));
    elements.history.append(button);
  }
}

async function loadHistory() {
  try {
    renderHistory(await api("/api/history"));
  } catch (error) {
    showToast(error.message);
  }
}

document.querySelectorAll(".mode").forEach((button) => {
  button.addEventListener("click", () => {
    currentMode = button.dataset.mode;
    document.querySelectorAll(".mode").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
  });
});

elements.newReflection.addEventListener("click", () => {
  elements.conversation.innerHTML = `<div class="welcome-card"><span class="spark">✦</span><h3>A fresh page</h3><p>Start wherever you are. Your next exchange will be saved privately.</p></div>`;
  elements.message.focus();
});

elements.clearHistory.addEventListener("click", async () => {
  if (!window.confirm("Permanently delete every saved reflection in this account?")) return;
  elements.clearHistory.disabled = true;
  try {
    const result = await api("/api/history", { method: "DELETE" });
    renderHistory([]);
    elements.conversation.replaceChildren();
    elements.status.textContent = "Private history cleared";
    showToast(`${result.deleted} saved reflection${result.deleted === 1 ? "" : "s"} deleted.`);
  } catch (error) {
    showToast(error.message);
  } finally {
    elements.clearHistory.disabled = false;
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = elements.message.value.trim();
  if (!prompt) return;
  elements.send.disabled = true;
  elements.message.disabled = true;
  elements.status.textContent = "Gemini is reflecting…";
  elements.conversation.replaceChildren(messageCard("user", prompt));
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message: prompt, mode: currentMode }),
    });
    elements.conversation.append(messageCard("assistant", result.response));
    elements.message.value = "";
    elements.status.textContent = "Saved securely to your private history";
    await loadHistory();
  } catch (error) {
    elements.status.textContent = "Not saved—please retry";
    showToast(error.message);
  } finally {
    elements.send.disabled = false;
    elements.message.disabled = false;
  }
});

async function boot() {
  try {
    const response = await fetch("/api/config");
    const config = await response.json();
    if (!response.ok) throw new Error(config.detail || "Firebase configuration failed.");
    const firebaseApp = initializeApp(config.firebase);
    auth = getAuth(firebaseApp);
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });

    elements.signIn.addEventListener("click", async () => {
      try {
        await signInWithPopup(auth, provider);
      } catch (error) {
        showToast(error.message || "Google sign-in could not be completed.");
      }
    });
    elements.signOut.addEventListener("click", () => signOut(auth));

    onAuthStateChanged(auth, async (user) => {
      currentUser = user;
      setSignedIn(Boolean(user));
      if (user) {
        elements.userName.textContent = user.displayName || user.email || "Signed in";
        await loadHistory();
      }
    });
  } catch (error) {
    showToast(error.message);
  }
}

boot();
