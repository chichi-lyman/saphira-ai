# Saphira Visual Avatar
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira’s public-facing assistant avatar is a digital presence modeled directly on **Chelsea Megan Woods** — so every user inside the app meets the same face, energy, and aesthetic.

## Visual DNA (locked)

From Chelsea’s reference imagery:

- Platinum blonde hair with dark black under-layers (ombré)
- Long wavy hair, striking eyes, full lashes
- Septum piercing, layered gold cross necklaces
- Signature chest tattoo (wings + cross motif)
- Black corset / structured top
- Warm, confident, direct presence

**Theme:** Classy **light-mode** sci-fi / cyberpunk-girly  
- Ivory / clean white canvas (`#F9F9FB`)  
- Neon **electric blue** (`#00E5FF`)  
- **Ultraviolet** accents (`#9D00FF`)  
- Soft holographic bloom, HUD chips, status bar

## Architecture

```
Flutter SaphiraAvatarView  ←→  AvatarChannel  ←→  FastAPI /avatar  ←→  GrokAvatarService
                                                                          ↓
                                                                   xAI Grok Imagine
                                                              (image-quality + video)
```

### Avatar states

| State | Expression intent |
|-------|-------------------|
| `idle` | Calm, poised, soft HUD rings |
| `welcome` | Warm smile + greeting gesture |
| `talking` | Mid-speech, voice-wave particles |
| `thinking` | Thoughtful upward gaze |
| `listening` | Attentive lean-in, blue halo |
| `glow` | Celebratory holographic bloom |
| `confirm` | Reassuring nod + check glyph |

## Backend

`src/avatar/grok_avatar_service.py`

- Anchors every prompt on Chelsea visual DNA
- Optional `init_image` (master reference URL) for I2I consistency
- `generate_frame(state)` → still via `grok-imagine-image-quality`
- `generate_clip(state)` → short motion via video surface (falls back to still + motion hint)

Env:

```bash
XAI_API_KEY=...                    # required for live generation
SAPHIRA_AVATAR_MASTER_URL=https://.../chelsea_avatar_master.jpg
```

### API

```
GET  /avatar/status
GET  /avatar/states
POST /avatar/frame     { state, extra_action?, reference_url? }
POST /avatar/clip      { state, duration_sec?, ... }
POST /avatar/reference { url }
```

## Flutter

- `lib/ui/saphira_avatar_view.dart` — ivory canvas, dual neon bloom, HUD chips, status bar
- `lib/services/avatar_channel.dart` — HTTP client to `/avatar`

Drop `SaphiraAvatarView` into any screen:

```dart
SaphiraAvatarView(
  avatarImageUrl: frameUrl,
  state: SaphiraAvatarState.talking,
  statusLabel: 'SAPHIRA AI // ONLINE',
)
```

## Master reference

1. Upload a clean portrait of Chelsea (corset, necklaces, tattoo visible, neutral-to-soft expression) to Supabase Storage or any HTTPS CDN.
2. `POST /avatar/reference` with that URL (or set `SAPHIRA_AVATAR_MASTER_URL`).
3. All subsequent frames/clips stay locked to that identity.

## Public interaction goal

Users should feel they are talking to **Saphira as Chelsea’s AI presence** — same face across landing, chat widget, onboarding, and in-app assistant — not a generic cartoon bot.

---

*Persona speech still runs through the Samantha dual pipeline; the avatar is the visual layer only.*
