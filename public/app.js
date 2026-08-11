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

  const addMessage = (role, text) => {
    const article = document.createElement('article');
    article.className = `message ${role}`;
    article.innerHTML = `<div class="avatar">${role === 'user' ? 'C' : 'S'}</div><div><span class="label">${role === 'user' ? 'YOU' : 'SAPHIRA'}</span><p></p></div>`;
    article.querySelector('p').textContent = text;
    messages.appendChild(article);
    messages.scrollTop = messages.scrollHeight;
  };

  const speak = (text) => {
    if (!('speechSynthesis' in window) || !text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.96;
    utterance.pitch = 1.04;
    utterance.volume = 1;
    utterance.onstart = () => { if (status) status.textContent = 'Speaking'; };
    utterance.onend = () => { if (status) status.textContent = 'Ready'; };
    window.speechSynthesis.speak(utterance);
  };

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

  async function submit(text) {
    const clean = text.trim();
    if (!clean || send.disabled) return;
    addMessage('user', clean);
    input.value = '';
    input.style.height = 'auto';
    send.disabled = true;
    if (status) status.textContent = 'Thinking';
    try {
      const reply = await askSaphira(clean);
      addMessage('saphira', reply);
      if (status) status.textContent = 'Ready';
      speak(reply);
    } catch (error) {
      console.error('Saphira API error:', error);
      addMessage('saphira', "I'm here, but I can't reach my cloud runtime right now. Give me a moment and try again.");
      if (status) status.textContent = 'API offline';
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', (event) => { event.preventDefault(); submit(input.value); });
  input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 130)}px`; });
  input.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
  document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => submit(button.dataset.prompt)));

  if (talk) talk.addEventListener('click', () => {
    input.focus();
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (status) status.textContent = 'Listening';
    input.placeholder = 'I\'m listening…';
  });

  if (clear) clear.addEventListener('click', () => {
    messages.innerHTML = '<article class="message saphira"><div class="avatar">S</div><div><span class="label">SAPHIRA</span><p>Conversation cleared. I\'m ready.</p></div></article>';
    if (status) status.textContent = 'Ready';
  });

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
})();
