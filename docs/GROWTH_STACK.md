# Saphira Growth Stack

© 2026 Chelsea Megan Woods

## Content policy (owner)

**Allowed:** raw emotion, rage, jealousy, toxic-energy themes, hard confrontation of real dynamics, strong engagement hooks rooted in lived experience.

**Creative preference:** start real/raw when needed; turn toward agency, boundaries, or a positive outcome when it fits.

**Still out of scope:** purchased followers, bot farms, fake engagement pods, content that promotes self-harm or violence.

## Pillars

Healthy boundaries · toxic dynamics · confidence & resilience · positive energy · jealousy (raw + constructive) · toxic family · female rage / real talk

## Tools

| Step | Tool | Secret |
|------|------|--------|
| Content | OpenAI / ChatGPT | `OPENAI_API_KEY` |
| Schedule | FeedHive | `FEEDHIVE_TRIGGER_URL` |
| Schedule | Publer | `PUBLER_API_TOKEN` |
| Publish policy | Instinct + Apex | `ALLOW` |

## Pipeline

`src/growth/pipeline.py` → `run_content_cycle(...)`

Intensity can be passed through as `raw` / `rage` in connector calls.
