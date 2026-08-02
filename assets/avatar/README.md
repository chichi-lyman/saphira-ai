# Saphira Avatar Assets
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

Place master and generated avatar frames here for offline / CDN fallback.

## Recommended layout

```
assets/avatar/
  chelsea_avatar_master.jpg   # Clean portrait reference (upload source)
  idle.png                    # Optional cached Grok frames
  welcome.png
  talking.png
  thinking.png
  listening.png
  glow.png
  confirm.png
```

## Generate frames

With `XAI_API_KEY` and `SAPHIRA_AVATAR_MASTER_URL` set:

```bash
python scripts/generate_avatar_frames.py
```

Or via API:

```bash
curl -X POST localhost:8000/avatar/frame -H 'Content-Type: application/json' \
  -d '{"state":"welcome"}'
```

## Visual lock

All prompts include Chelsea Megan Woods visual DNA:
platinum/black ombré hair, chest tattoo, gold cross necklaces, black corset,
ivory light-mode sci-fi, electric blue + ultraviolet holographic accents.
