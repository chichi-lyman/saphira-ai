# Saphira AI 🐉

**Personal AI Assistant · Multi-Agent Intelligence Operating System**  
**Architected and Built by Chelsea Megan Woods**  
**Ecosystem:** Nova Umbrella™

Saphira AI is a persistent, multimodal personal AI assistant and executive runtime. She understands natural-language intent, coordinates specialized intelligence workers, executes tasks within strict policy, verifies results, remembers what matters, and reports clearly — all through one unified conversational interface.

> **Say what you want.**  
> Saphira understands the intent, coordinates the right intelligence, executes within policy, verifies the result, remembers what matters, and tells you what happened.

---

## Public deployment

The canonical production web client is `saphira-app/`. It is a React + Vite PWA designed to deploy from the `main` branch. The production frontend requires a public Saphira API endpoint through `SAPHIRA_API_URL` / `VITE_SAPHIRA_API_BASE_URL` for live chat and streaming.

## What Saphira Is

Saphira AI is designed as a single conversational identity backed by a governed multi-agent execution fabric. Users talk to one assistant. Behind the scenes, Saphira plans, delegates, executes, verifies, and remembers.

She is built for:

- **Personal AI assistance** — continuous context, memory, and proactive support  
- **Conversational AI** — natural text and voice interaction  
- **Multi-agent orchestration** — specialized workers coordinated behind one assistant  
- **Business automation** — lead intake, qualification, follow-up, research, and workflows  

---

## Production architecture

```text
Public Saphira Web/PWA
        |
        v
Saphira API / Core Runtime
        |
   +----+----+----+
   |         |    |
  AI      Memory Tools
```

Provider secrets remain server-side. The browser receives only the public API base URL required to communicate with Saphira.

---

© 2026 Chelsea Megan Woods™. All rights reserved.
