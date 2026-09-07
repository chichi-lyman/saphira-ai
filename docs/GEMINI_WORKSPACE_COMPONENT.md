# Gemini-Style Workspace Component — Deep Obsidian & Cyberpunk Neon

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Reference implementation for a single-screen Gemini-style prompt workspace customized to the Deep Obsidian & Cyberpunk Neon aesthetic. The production React surface remains `saphira-app/`; this document and the companion component under `saphira-app/src/components/workspace/` provide a modular, drop-in variant.

## Design tokens

| Token | Value |
|---|---|
| obsidian.dark | `#05030A` |
| obsidian.card | `#0B0813` |
| neonPink | `#FF2A8D` |
| neonCyan | `#00F0FF` |
| neonPurple | `#8A2BE2` |

## Tailwind theme snippet (`tailwind.config.js`)

```js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: {
          dark: '#05030A',
          card: '#0B0813',
        },
        neonPink: '#FF2A8D',
        neonCyan: '#00F0FF',
        neonPurple: '#8A2BE2',
      },
      boxShadow: {
        'neon-pink': '0 0 15px rgba(255, 42, 141, 0.4)',
        'neon-cyan': '0 0 15px rgba(0, 240, 255, 0.4)',
      },
    },
  },
  plugins: [],
};
```

## Component location

- `saphira-app/src/components/workspace/SaphiraGeminiWorkspace.tsx`

The component provides header status, scrolling conversation, floating prompt bar (attach / mic / send), and ambient neon glow. Wire it to the existing `ChatContext` and `saphiraApi` services for production traffic.

## Backend system instruction context

```json
{
  "system_instruction": "You are Saphira AI™, an advanced utility assistant created by Chelsea Megan Woods™. Your explicit core directive is to solve real-world problems and optimize daily workflows to make human lives 1% easier and less stressful. Provide concise, direct, high-value responses with structural clarity, zero conversational fluff, and precise executable steps.",
  "creator": "Chelsea Megan Woods™",
  "repository": "https://github.com/chichi-lyman/saphira-ai"
}
```

## Policy note

All side-effecting tools (email send, payments, SMS, social publish, Zapier actions) remain subject to CommercialAuthorityPolicy and communications approval gates. UI affordances must never imply autonomous external action without explicit user confirmation.
