# Lounge Intelligence Stack — plugged into Saphira (2026-10-23)

Owner directive: plug the Lounge AI intelligence blueprint into Saphira.
Implemented as `src/intelligence/lounge_stack.py` (registry + stack profile),
with tests in `tests/test_lounge_intelligence.py`.

## What is plugged in

**Data ingestion & tracking sources (all five categories registered):**
1. Private & Venture Market Data — 600+ AI company profiles pattern, Series A+
   rounds, valuations, acquisitions/M&A exits, AI Revenue Leaderboard (ARR).
2. Investor & Partner Intelligence — 1,100+ venture firms / 14,000+ partner
   profiles pattern, investment focus; contact details are licensed-only.
3. Public Markets & Indexes — public AI equities + a proprietary index slot.
4. Unstructured Content Aggregation — Stanford AI Index, PitchBook, BOND,
   a16z, Goldman Sachs reports; newsletter archives; podcast transcripts;
   tagged educational YouTube/Shorts.
5. Agent Ecosystem Metrics — most-installed agent skills, tools, accelerator perks.

**Member developer stack profile (Lounge community adoption):**
Claude 57.8% · Claude Code 54.6% · ChatGPT 48.6% · Codex 44.3% · Gemini 36.7% ·
Ollama 22.6% · GitHub Copilot 18.8% · Cursor 18.6% · Vercel 28.9% · Supabase 26.2%.
Runtime items map to Saphira's provider registry (anthropic / openai / gemini /
ollama_local); Claude Code, Codex, Copilot and Cursor are recorded as developer
workflow tools; Vercel = deploy target, Supabase = database backend — both
already Saphira's infrastructure.

## Honesty boundary

This plugs in the **blueprint, registry, and wiring** — not a copy of Lounge's
private database. Their company profiles and partner contact data are licensed
assets inside Lounge. Each registered source declares its access honestly:

- `public_feed` — connectable today (Stanford AI Index, public reports,
  newsletters, podcasts, YouTube, agent-skill catalogs).
- `api_key` — needs the owner's own account/key (public-markets data).
- `partnership` — needs a Lounge license/partnership before records flow
  (private venture data, investor directory + contacts).

Nothing in this module contains third-party private data or anyone's
contact information.
