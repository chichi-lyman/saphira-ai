# Saphira PWA & Client-Side AI

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

## Progressive Web App

| File | Role |
|------|------|
| `public/manifest.json` | Installable app name, theme (#0a0a0a), standalone display |
| `public/sw.js` | Service worker — precache shell, offline fallback |
| `src/ai/registerServiceWorker.js` | Registers `/sw.js` on page load |

### Enable in HTML / Next.js

Link the manifest in `<head>`:

```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#0a0a0a" />
```

Import registration once in your app entry (e.g. `web/pages/index.tsx` or `_app`):

```js
import "../src/ai/registerServiceWorker";
// or
import { registerSaphiraServiceWorker } from "../src/ai/registerServiceWorker";
registerSaphiraServiceWorker();
```

Add real icons at `public/icons/icon-192.png` and `icon-512.png` (dark Saphira mark).

## Client-side / hybrid AI

| File | Role |
|------|------|
| `src/ai/clientAI.js` | On-device prompts via `window.ai` (Gemini Nano / Prompt API) |

### Usage

```js
import { runLocalPrompt, summarizeLocal, smartReplyLocal, isClientAIAvailable } from "../src/ai/clientAI";

if (await isClientAIAvailable()) {
  const summary = await summarizeLocal(longText);
  const reply = await smartReplyLocal(incomingMessage);
} else {
  // fall back to your cloud API (Gemini / orchestrator)
}
```

### What this enables

- Text summarization on device
- Smart replies without a round-trip
- Offline-capable shell via service worker
- Install to home screen (PWA)
- Hybrid path: local model first, cloud when unavailable or for heavy tasks

### Browser note

Chrome Prompt API / Gemini Nano availability depends on device and flags. Always call `isClientAIAvailable()` and keep a cloud fallback (your existing Saphira orchestrator / Gemini connector).
