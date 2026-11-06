# Saphira AI™ Web Application

React + Vite + TypeScript frontend for the Saphira conversational interface.

## Structure

```
saphira-app/
├── public/                 Static assets (favicon, logo)
├── src/
│   ├── assets/             Global CSS
│   ├── components/
│   │   ├── chat/           ChatInput, MessageList, MessageItem
│   │   ├── layout/         Header, Sidebar
│   │   └── ui/             Button, Modal
│   ├── config/            saphiraConfig.ts
│   ├── context/           UserContext, ChatContext
│   ├── hooks/             useSaphiraStream.ts
│   ├── services/          saphiraApi.ts
│   ├── types/             saphira.ts
│   ├── utils/             markdownFormatter.ts
│   ├── App.tsx
│   └── main.tsx
├── .env.local.example
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Setup

```bash
cd saphira-app
cp .env.local.example .env.local
# Edit .env.local with VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY, and VITE_SAPHIRA_API_BASE_URL
npm install
npm run dev
```

The Vite dev server runs on port 3000 and proxies `/api` to the FastAPI backend (default `http://localhost:8000`).

## Integration with Saphira core

- API client targets `/api/chat` and sends the signed-in Supabase access token as a bearer token.
- Supabase Auth handles registration, email verification, login, password reset, session refresh, and logout.
- Browser code uses only the public Supabase publishable key; never place service-role or provider secrets in Vite variables.
- System instruction and model defaults live in `src/config/saphiraConfig.ts`.
- Streaming is handled by `useSaphiraStream` and `saphiraApi.streamChat`.

© Saphira AI / Nova Umbrella. Architected for integration with the master Saphira runtime.
