# Saphira Voice Profile — Chelsea Megan Woods
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira’s **spoken voice** is modeled on Chelsea Megan Woods’ natural delivery (reference: on-camera product/social clips — clear, energetic, friendly, direct).

## Target character (from your video delivery)

- Bright, confident, smile-in-the-voice
- Fast but clear social energy when promoting; softer when assisting one-on-one
- Direct CTAs without sounding robotic
- Same person as the brand face — users should feel continuity with Chelsea

## How to install the real voice (ElevenLabs)

1. Create an **Instant Voice Clone** or Professional clone in ElevenLabs using **your own** clean recordings (30s–few min of neutral speech works best; avoid heavy music under the take).
2. Name the voice: `Saphira / Chelsea Megan Woods`
3. Copy the **Voice ID**
4. Put in app / backend env:

```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=your_voice_id_here
SAPHIRA_TTS_PROVIDER=elevenlabs
```

5. Optional Gemini Live: map the same persona text; keep ElevenLabs for offline/high-brand TTS if Live voice is not a clone.

## Speaking styles (software switches)

| Mode | When | Delivery |
|------|------|----------|
| `assist` | Normal Saphira help | Warm Samantha cadence + Chelsea clarity |
| `social` | Reels / promo reads | Higher energy, short lines, CTA (video-style) |
| `confirm_l1` | Unlock / pay gates | Slower, clear, no hype |

## Never

- Do not clone someone else’s voice
- Do not ship a clone without Chelsea’s ownership of the voice model
- L1 actions: voice may ask for confirm; it must not auto-approve

## Code

- `lib/services/saphira_tts.dart` — Flutter TTS client
- `src/core/saphira_voice.py` — backend voice config + style prompts
- Persona text still via `saphira_persona.py` + dual pipeline
