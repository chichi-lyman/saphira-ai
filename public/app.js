/**
 * Saphira AI — production frontend runtime
 * Chat + browser voice input/output + session continuity.
 */
(function () {
  "use strict";

  const API_URL = (window.SAPHIRA_API_URL || "/api").replace(/\/$/, "");
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const talkBtn = document.getElementById("talkToSaphira");
  const sessionKey = "saphira_session_id";
  const sessionId = localStorage.getItem(sessionKey) || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
  localStorage.setItem(sessionKey, sessionId);

  let recognition = null;
  let speaking = false;

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
      </div>`;
    div.querySelector("p").textContent = text;
    if (isUser) {
      const bubble = div.querySelector(".msg-bubble");
      const avatar = div.querySelector(".msg-avatar");
      div.innerHTML = "";
      div.appendChild(bubble);
      div.appendChild(avatar);
    }
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function speak(text) {
    if (!("speechSynthesis" in window) || !text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.96;
    utterance.pitch = 1.02;
    utterance.volume = 1;
    speaking = true;
    utterance.onend = () => { speaking = false; };
    window.speechSynthesis.speak(utterance);
  }

  async function sendMessage(text) {
    const trimmed = String(text || "").trim();
    if (!trimmed) return;
    appendMessage("user", trimmed, "CHELSEA");
    if (chatInput) chatInput.value = "";

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Saphira-Device": "web" },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
      });
      if (!response.ok) throw new Error(`API ${response.status}`);
      const data = await response.json();
      const reply = data.message || data.reply || "I received that, but the production runtime returned no message.";
      appendMessage("saphira", reply, "SAPHIRA");
      speak(reply);
    } catch (error) {
      appendMessage("saphira", "I’m online, but my production brain is temporarily unreachable. Please try again in a moment.", "SAPHIRA");
      console.error("Saphira API error:", error);
    }
  }

  function startListening() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      appendMessage("saphira", "Voice input isn't supported by this browser. You can still type to me.", "SAPHIRA");
      return;
    }
    recognition = new Recognition();
    recognition.lang = navigator.language || "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onstart = () => {
      talkBtn.classList.add("listening");
      talkBtn.innerHTML = '<span class="mic-icon">⏹</span> LISTENING…';
    };
    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) transcript += event.results[i][0].transcript;
      if (chatInput) chatInput.value = transcript;
    };
    recognition.onerror = () => stopListening();
    recognition.onend = () => {
      const text = chatInput ? chatInput.value : "";
      stopListening();
      if (text.trim()) sendMessage(text);
    };
    recognition.start();
  }

  function stopListening() {
    if (recognition) {
      try { recognition.stop(); } catch (_) {}
      recognition = null;
    }
    if (talkBtn) {
      talkBtn.classList.remove("listening");
      talkBtn.innerHTML = '<span class="mic-icon">🎤</span> TALK TO SAPHIRA';
    }
  }

  if (sendBtn && chatInput) {
    sendBtn.addEventListener("click", () => sendMessage(chatInput.value));
    chatInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(chatInput.value);
      }
    });
  }

  if (talkBtn) {
    talkBtn.addEventListener("click", () => {
      if (speaking && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        speaking = false;
        return;
      }
      if (recognition) stopListening();
      else startListening();
    });
  }

  document.querySelectorAll(".nav-item, .dock-item").forEach((el) => {
    el.addEventListener("click", () => {
      document.querySelectorAll(".nav-item, .dock-item").forEach((n) => n.classList.remove("active"));
      el.classList.add("active");
      const href = el.getAttribute("href");
      if (href) document.querySelectorAll(`[href="${href}"]`).forEach((n) => n.classList.add("active"));
    });
  });
})();
