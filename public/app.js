(() => {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('prompt');
  const messages = document.getElementById('messages');
  const send = document.getElementById('send');
  const status = document.getElementById('statusText');
  const talk = document.getElementById('talkToSaphira');
  const clear = document.getElementById('clearChat');

  const apiBase = (window.SAPHIRA_API_URL || 'https://saphira-ai.onrender.com/api').replace(/\/$/, '');
  const sessionKey = 'saphira-session-id';
  const sessionId = localStorage.getItem(sessionKey) || crypto.randomUUID();
  localStorage.setItem(sessionKey, sessionId);

  let listening = false;
  let continuous = true;
  let recognition = null;
  let shouldResumeListening = false;
  let speaking = false;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const supportsRecognition = !!SpeechRecognition;

  const setStatus = (value) => {
    if (status) status.textContent = value;
    if (talk) {
      talk.classList.toggle('listening', value === 'Listening');
      talk.classList.toggle('speaking', value === 'Speaking');
    }
  };

  const addMessage = (role, text) => {
    const article = document.createElement('article');
    article.className = `message ${role}`;
    article.innerHTML = `<div class="avatar">${role === 'user' ? 'C' : 'S'}</div><div><span class="label">${role === 'user' ? 'YOU' : 'SAPHIRA'}</span><p></p></div>`;
    article.querySelector('p').textContent = text;
    messages.appendChild(article);
    messages.scrollTop = messages.scrollHeight;
  };

  // Natural conversational delivery. Browser voices are used as a zero-cost fallback;
  // the backend can later supply a premium audio URL without changing this UI contract.
  const speak = (text) => new Promise((resolve) => {
    if (!('speechSynthesis' in window) || !text) { resolve(false); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.94;
    utterance.pitch = 1.06;
    utterance.volume = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => /Samantha|Karen|Ava|Google US English|Microsoft.*Jenny|Microsoft.*Aria/i.test(v.name));
    if (preferred) utterance.voice = preferred;
    speaking = true;
    setStatus('Speaking');
    utterance.onend = () => { speaking = false; setStatus('Ready'); resolve(true); if (continuous && shouldResumeListening) startListening(); };
    utterance.onerror = () => { speaking = false; setStatus('Ready'); resolve(false); if (continuous && shouldResumeListening) startListening(); };
    window.speechSynthesis.speak(utterance);
  });

  async function askSaphira(text) {
    const response = await fetch(`${apiBase}/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, source: 'saphira-web', session_id: sessionId})
    });
    if (!response.ok) throw new Error(`API ${response.status}`);
    const data = await response.json();
    return data.message || data.response || data.output || 'I am here. What do you want to work on?';
  }

  async function submit(text, fromVoice = false) {
    const clean = text.trim();
    if (!clean || send.disabled) return;
    addMessage('user', clean);
    input.value = '';
    input.style.height = 'auto';
    send.disabled = true;
    shouldResumeListening = fromVoice || continuous;
    stopListening(false);
    setStatus('Thinking');
    try {
      const reply = await askSaphira(clean);
      addMessage('saphira', reply);
      await speak(reply);
    } catch (error) {
      console.error('Saphira API error:', error);
      addMessage('saphira', "I'm having trouble reaching my cloud runtime right now. The connection should recover shortly.");
      setStatus('API offline');
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  function createRecognition() {
    if (!supportsRecognition) return null;
    const r = new SpeechRecognition();
    r.lang = 'en-US';
    r.continuous = false;
    r.interimResults = true;
    r.maxAlternatives = 1;

    r.onstart = () => { listening = true; setStatus('Listening'); };
    r.onresult = (event) => {
      let finalText = '';
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += transcript;
        else interim += transcript;
      }
      input.value = finalText || interim;
      if (finalText.trim()) submit(finalText, true);
    };
    r.onerror = (event) => {
      listening = false;
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        continuous = false;
        setStatus('Mic permission needed');
      } else if (event.error !== 'aborted') setStatus('Ready');
    };
    r.onend = () => {
      listening = false;
      if (!speaking && continuous && shouldResumeListening) {
        window.setTimeout(startListening, 250);
      }
    };
    return r;
  }

  function startListening() {
    if (!supportsRecognition || listening || speaking) return;
    if (!recognition) recognition = createRecognition();
    shouldResumeListening = true;
    try { recognition.start(); } catch (e) { /* browser can reject duplicate starts */ }
  }

  function stopListening(resetContinuous = true) {
    if (resetContinuous) { continuous = false; shouldResumeListening = false; }
    if (recognition && listening) { try { recognition.stop(); } catch (e) {} }
    listening = false;
    if (!speaking && resetContinuous) setStatus('Ready');
  }

  function toggleVoice() {
    if (!supportsRecognition) {
      setStatus('Mic unsupported');
      input.placeholder = 'Use Chrome on Android for voice input';
      input.focus();
      return;
    }
    if (listening || continuous) {
      continuous = false;
      shouldResumeListening = false;
      stopListening(true);
      return;
    }
    continuous = true;
    shouldResumeListening = true;
    startListening();
  }

  form.addEventListener('submit', (event) => { event.preventDefault(); submit(input.value, false); });
  input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 130)}px`; });
  input.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
  document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => submit(button.dataset.prompt, false)));
  if (talk) talk.addEventListener('click', toggleVoice);

  if (clear) clear.addEventListener('click', () => {
    window.speechSynthesis?.cancel();
    continuous = false;
    shouldResumeListening = false;
    stopListening(true);
    messages.innerHTML = '<article class="message saphira"><div class="avatar">S</div><div><span class="label">SAPHIRA</span><p>Conversation cleared. I\'m ready.</p></div></article>';
    setStatus('Ready');
  });

  if ('speechSynthesis' in window) window.speechSynthesis.getVoices();
  if (!supportsRecognition) {
    input.placeholder = 'Type to Saphira, or use Chrome for voice';
  }
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
})();
