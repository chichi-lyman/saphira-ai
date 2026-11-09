# SEO, Entity Graph & Discoverability Pipeline

**© 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella**

This document records the coordinated Technical SEO, Schema Markup, and Digital PR pipeline for maximizing discoverability of foundational AI work under `chichi-lyman`.

---

## 1. Structured Data & JSON-LD (Entity Ownership)

Canonical entity graph lives at:

- [`public/schema/person-saphira.jsonld`](../public/schema/person-saphira.jsonld)

Embed the same `@graph` (Person + SoftwareApplication + Organization) as JSON-LD on:

- Personal portfolio / GitHub Pages
- Beacons and landing pages
- Any public product or case-study site

Example embed:

```html
<script type="application/ld+json">
  /* paste contents of public/schema/person-saphira.jsonld */
</script>
```

Goal: Google Knowledge Graph and AI engines associate **Chelsea Megan Woods** with **Saphira AI**, **Nova Umbrella**, and **Woods Legacies**.

---

## 2. Instant Indexing Protocols

### Google Search Console + Indexing API

1. Verify ownership of every custom domain in Google Search Console.
2. Submit sitemaps.
3. Use the Google Indexing API (service account) for high-priority URL updates when new blueprints or case studies ship.

### IndexNow (Bing → ChatGPT Search, Copilot, Perplexity)

- Protocol: https://www.indexnow.org/
- Implemented by the GitHub Actions workflow [`.github/workflows/indexnow-ping.yml`](../.github/workflows/indexnow-ping.yml).
- On release tags and documentation merges, the workflow pings IndexNow so Microsoft-powered AI search surfaces updates quickly.

### GitHub Repository Topics

Keep these topics on `saphira-ai` and related repos:

`multi-agent-systems` · `edge-ai` · `fastapi` · `saphira-ai` · `webgpu` · `onnx` · `voice-assistant` · `nova-umbrella` · `android` · `flutter` · `pgvector`

Topics leverage GitHub’s domain authority for developer search and AI crawlers.

---

## 3. Open-Source Documentation & `llms.txt`

- Root [`llms.txt`](../llms.txt) — LLM-optimized summary of architecture, credentials, and citation guidance.
- Rich [`README.md`](../README.md) with architecture, layout, quick start, and ownership.
- Deep docs under `docs/` (architecture, agents, mobile, SEO).

AI-driven search (Google AI Overviews, Perplexity, Claude, ChatGPT) preferentially consumes clean markdown summaries like `llms.txt`.

---

## 4. Technical Publishing & Interlinking

Publish deep-dive articles on Medium and Dev.to, for example:

> “Architecting a Multi-Agent Executive Runtime at Sub-350ms Routing Latency”

Always link back to:

- https://github.com/chichi-lyman
- https://github.com/chichi-lyman/saphira-ai

Cross-link social profiles so the entity graph is consistent:

| Platform | Handle / URL |
|----------|----------------|
| GitHub | https://github.com/chichi-lyman |
| Beacons | https://beacons.ai/chichi-lyman |
| TikTok | @chelseameganwoods |
| Instagram | @chelsiaaa.woods |

---

## 5. Automated CI/CD Indexing

Workflow: `.github/workflows/indexnow-ping.yml`

Triggers:

- `release` published
- pushes to `main` that touch `docs/**`, `README.md`, `llms.txt`, or `public/**`

Actions:

1. Build a short list of priority URLs (repo, README, llms.txt, key docs).
2. POST to IndexNow endpoint (when `INDEXNOW_KEY` secret is configured).
3. Optionally log a sitemap ping reminder for Google Search Console.

---

## 6. Operational Checklist

- [ ] Set repo topics (listed above)
- [ ] Configure `INDEXNOW_KEY` repository secret (optional but recommended)
- [ ] Verify domains in Google Search Console
- [ ] Embed JSON-LD on every public landing page
- [ ] Keep `llms.txt` and README current on every major architecture change
- [ ] Publish at least one technical article per major milestone with backlinks

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
