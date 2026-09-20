# Saphira Growth Stack

© 2026 Chelsea Megan Woods

## Strategy (female empowerment — no toxic engagement farming)

**Pillars:** healthy boundaries · toxic relationship dynamics · confidence & resilience · positive energy · constructive jealousy · toxic family & boundaries

**Forbidden:** rage-bait, jealousy clickbait, shame hooks, fake followers, engagement pods.

**Follower growth:** organic consistency, SEO/ASO-aware profiles and captions, genuine engagement. Analyze with platform analytics; adjust with Lyra summaries.

## Tools

| Step | Tool | Secret / config |
|------|------|-----------------|
| 1. Content | ChatGPT via OpenAI | `OPENAI_API_KEY` |
| 2. Schedule | FeedHive | `FEEDHIVE_TRIGGER_URL` |
| 3. Schedule | Publer (Business API) | `PUBLER_API_TOKEN` |
| 4. Publish policy | Instinct + Apex | `ALLOW` (owner) |

## Pipeline

```text
pillar / topic
  → openai_content.brainstorm / write_copy
  → feedhive.schedule_post and/or publer.schedule_post
  → analytics review (manual or Lyra)
```

Python entry: `src/growth/pipeline.py` → `run_content_cycle(...)`

## Funnels & monetization

Apex may propose offers and funnels under ALLOW. Keep landing pages honest; pair content CTAs with real resources (guides, email, community) — not rage-driven urgency.

## SEO / ASO

- Clear niche keywords in bio and captions (boundaries, self-trust, empowerment).
- Consistent series titles.
- Alt text and on-screen text for accessibility and ranking signals.
- Avoid keyword spam and misleading hooks.
