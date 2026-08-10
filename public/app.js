(() => {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('prompt');
  const messages = document.getElementById('messages');
  const send = document.getElementById('send');
  const status = document.getElementById('statusText');

  // Set this at deploy time if the FastAPI service lives on another origin:
  // window.SAPHIRA_API_URL = 'https://your-saphira-api.example.com';
  const apiBase = (window.SAPHIRA_API_URL || '').replace(/\/$/, '');

  const addMessage = (role, text) => {
    const article = document.createElement('article');
    article.className = `message ${role}`;
    article.innerHTML = `<div class="avatar">${role === 'user' ? 'C' : 'S'}</div><div><span class="label">${role === 'user' ? 'YOU' : 'SAPHIRA'}</span><p></p></div>`;
    article.querySelector('p').textContent = text;
    messages.appendChild(article);
    messages.scrollTop = messages.scrollHeight;
  };

  const localResponse = (text) => {
    const value = text.toLowerCase();
    if (value.includes('sales') || value.includes('prospect') || value.includes('lead')) {
      return 'I can coordinate research, qualification, sales strategy, outreach, CRM synchronization, and verification. Connect the production sales provider to execute external actions.';
    }
    if (value.includes('tool') || value.includes('plugin')) {
      return 'My unified capability fabric is designed to route work through approved GitHub, Shopify, Stripe, CRM, calendar, research, memory, device, analytics, and MCP integrations.';
    }
    if (value.includes('growth') || value.includes('business')) {
      return 'I can turn a growth objective into a task graph, select the appropriate capabilities, apply approval policies, and verify the result. The production backend determines which connected tools can execute it.';
    }
    return 'I received your request. The Saphira web shell is online; connect the production API endpoint to enable full cloud execution and persistent memory.';
  };

  async function askSaphira(text) {
    if (!apiBase) return localResponse(text);
    const response = await fetch(`${apiBase}/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, source: 'saphira-web'})
    });
    if (!response.ok) throw new Error(`API ${response.status}`);
    const data = await response.json();
    return data.response || data.message || data.output || 'Saphira completed the request.';
  }

  async function submit(text) {
    const clean = text.trim();
    if (!clean || send.disabled) return;
    addMessage('user', clean);
    input.value = '';
    input.style.height = 'auto';
    send.disabled = true;
    status.textContent = apiBase ? 'Thinking' : 'Local shell';
    try {
      const reply = await askSaphira(clean);
      addMessage('saphira', reply);
      status.textContent = 'Ready';
    } catch (error) {
      addMessage('saphira', 'The cloud runtime is unavailable from this deployment. Your request is safe; check the Saphira API URL and deployment environment variables, then try again.');
      status.textContent = 'API offline';
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', (event) => { event.preventDefault(); submit(input.value); });
  input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 130)}px`; });
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
  });
  document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => submit(button.dataset.prompt)));

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
})();
