/**
 * Saphira AI — Frontend Runtime
 * Minimal client for chat + voice button
 */
(function () {
  "use strict";

  const API_URL = window.SAPHIRA_API_URL || "/api";
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const talkBtn = document.getElementById("talkToSaphira");

  function appendMessage(role, text, label) {
    if (!chatMessages) return;
    const isUser = role === "user";
    const div = document.createElement("div");
    div.className = "msg " + (isUser ? "user" : "saphira");
    div.innerHTML = `
      <div class="msg-avatar ${isUser ? "user-av" : ""}">${isUser ? "C" : "S"}</div>
      <div class="msg-bubble">
        <span class="msg-label">${label || (isUser ? "CHELSEA" : "SAPHIRA")}</span>
        <p></p>
      </div>
    `;
    div.querySelector("p").textContent = text;
    if (isUser) {
      // reverse order for user
      const bubble = div.querySelector(".msg-bubble");
      const av = div.querySelector(".msg-avatar");
      div.innerHTML = "";
      div.appendChild(bubble);
      div.appendChild(av);
      bubble.querySelector("p").textContent = text;
    }
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendMessage(text) {
    if (!text || !text.trim()) return;
    const trimmed = text.trim();
    appendMessage("user", trimmed, "CHELSEA");
    if (chatInput) chatInput.value = "";

    try {
      const res = await fetch((API_URL.replace(/\/$/, "") + "/chat") || "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      if (!res.ok) throw new Error("API " + res.status);
      const data = await res.json();
      const reply = data.message || data.reply || "Acknowledged. Connecting to production runtime…";
      appendMessage("saphira", reply, "SAPHIRA");
    } catch (err) {
      appendMessage(
        "saphira",
        "I received your request. The Saphira web shell is online; connect the production API endpoint to enable full cloud execution and persistent memory.",
        "SAPHIRA"
      );
      console.warn("Saphira chat fallback:", err);
    }
  }

  if (sendBtn && chatInput) {
    sendBtn.addEventListener("click", () => sendMessage(chatInput.value));
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
      }
    });
  }

  if (talkBtn) {
    talkBtn.addEventListener("click", () => {
      talkBtn.classList.toggle("listening");
      if (talkBtn.classList.contains("listening")) {
        talkBtn.innerHTML = '<span class="mic-icon">⏹</span> LISTENING…';
        // Placeholder: real continuous voice would start here
        if (chatInput) {
          chatInput.placeholder = "Listening… speak or type";
          chatInput.focus();
        }
      } else {
        talkBtn.innerHTML = '<span class="mic-icon">🎤</span> TALK TO SAPHIRA';
        if (chatInput) chatInput.placeholder = "Ask Saphira anything…";
      }
    });
  }

  // Nav active state
  document.querySelectorAll(".nav-item, .dock-item").forEach((el) => {
    el.addEventListener("click", () => {
      document.querySelectorAll(".nav-item, .dock-item").forEach((n) => n.classList.remove("active"));
      el.classList.add("active");
      // Keep corresponding dock/nav in sync if possible
      const href = el.getAttribute("href");
      if (href) {
        document.querySelectorAll(`[href="${href}"]`).forEach((n) => n.classList.add("active"));
      }
    });
  });
})();
