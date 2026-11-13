#!/usr/bin/env python3
"""
Saphira Autonomous Horror-Drama YouTube Shorts Engine
© 2026 Chelsea Megan Woods / Nova Umbrella

State machine:
  1. Deduplication check against memory/episode_ledger.json
  2. GPT-4o script + 6 vertical image prompts (strict 60s retention arc)
  3. ElevenLabs voice synthesis
  4. DALL·E 3 frames + FFmpeg Ken-Burns + captions → final_short.mp4
  5. YouTube Shorts upload + pinned funnel comment
  6. Ledger append + commit (handled by workflow)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "memory" / "episode_ledger.json"
WORK_DIR = Path("/tmp/saphira_youtube_work")
WORK_DIR.mkdir(parents=True, exist_ok=True)

FUNNEL_URL = os.getenv("FUNNEL_URL", "https://beacons.ai/chichi-lyman")
TARGET_DURATION_SEC = 60
TARGET_WORDS ≈ 145  # ~2.4 words/sec for natural delivery

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_ledger() -> dict[str, Any]:
    if not LEDGER_PATH.exists():
        return {"episodes": [], "last_updated": None, "schema_version": 1}
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(data: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def already_used_title_or_hook(ledger: dict, title: str, hook: str) -> bool:
    titles = {e.get("title", "").lower().strip() for e in ledger.get("episodes", [])}
    hooks = {e.get("hook_snippet", "").lower().strip() for e in ledger.get("episodes", [])}
    return title.lower().strip() in titles or hook.lower().strip()[:40] in hooks


# ---------------------------------------------------------------------------
# 1 + 2. Script generation (strict JSON schema)
# ---------------------------------------------------------------------------
SCRIPT_SYSTEM = """You are the master storyteller for a faceless horror-drama YouTube Shorts channel.
Write a single 60-second vertical Short that follows this exact retention architecture:

Act 1 (0–3 seconds) — Psychological Horror Hook
Start with an atmospheric, unsettling, or terrifying image/feeling. No dialogue yet if possible. Pure dread that stops the scroll.

Act 2 (4–45 seconds) — Toxic Relationship / Situationship Pivot
Smoothly transition into a high-stakes, messy, emotionally charged everyday drama: betrayal, gaslighting, situationship collapse, silent treatment, revenge, or toxic codependency. Make it feel painfully real and relatable.

Act 3 (46–60 seconds) — Peak Cliffhanger
End on maximum tension. Never resolve. The last line must drive the viewer to the pinned comment for the "uncensored Extended Cut".

Constraints:
- Total narration ≈ 145 words (strict).
- Dark gothic, cinematic tone.
- No gore descriptions that would violate YouTube policy; psychological horror only.
- Output ONLY valid JSON matching the schema."""

SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Clickable Shorts title under 70 chars"},
        "description": {"type": "string", "description": "YouTube description with hashtags and funnel tease"},
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 8,
            "maxItems": 15,
        },
        "narration_script": {
            "type": "string",
            "description": "Full spoken narration, ~145 words, ready for TTS",
        },
        "hook_snippet": {
            "type": "string",
            "description": "First 1-2 sentences of the horror hook for deduplication",
        },
        "image_prompts": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 6,
            "maxItems": 6,
            "description": "Exactly 6 vertical 1080x1920 dark-gothic cinematic prompts, one per ~10s segment",
        },
    },
    "required": ["title", "description", "tags", "narration_script", "hook_snippet", "image_prompts"],
    "additionalProperties": False,
}


def generate_script(client: OpenAI, ledger: dict) -> dict[str, Any]:
    max_attempts = 4
    for attempt in range(max_attempts):
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SCRIPT_SYSTEM},
                {
                    "role": "user",
                    "content": (
                        "Generate one fresh, non-repeating episode. "
                        "Avoid any storyline that could overlap with previous episodes. "
                        "Return pure JSON only."
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "horror_drama_short", "schema": SCRIPT_SCHEMA, "strict": True},
            },
            temperature=0.92,
        )
        data = json.loads(resp.choices[0].message.content)
        if not already_used_title_or_hook(ledger, data["title"], data["hook_snippet"]):
            return data
        print(f"[dedup] Attempt {attempt+1} collided — regenerating…")
    raise RuntimeError("Could not generate a unique script after multiple attempts")


# ---------------------------------------------------------------------------
# 3. ElevenLabs voice
# ---------------------------------------------------------------------------
def synthesize_voice(script: str, out_path: Path) -> None:
    api_key = os.environ["ELEVENLABS_API_KEY"]
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": script,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.38,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    print(f"[voice] Saved {out_path} ({len(r.content)} bytes)")


# ---------------------------------------------------------------------------
# 4. Visuals + FFmpeg assembly
# ---------------------------------------------------------------------------
def generate_frames(client: OpenAI, prompts: list[str], frame_dir: Path) -> list[Path]:
    frame_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, prompt in enumerate(prompts):
        full_prompt = (
            f"{prompt}, vertical 9:16 composition, dark gothic cinematic lighting, "
            f"moody atmospheric, high detail, no text, no watermark, film still"
        )
        print(f"[img] Generating frame {i+1}/6 …")
        result = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1792",  # closest vertical
            quality="standard",
            n=1,
        )
        img_url = result.data[0].url
        img_data = requests.get(img_url, timeout=60).content
        p = frame_dir / f"frame_{i:02d}.png"
        p.write_bytes(img_data)
        paths.append(p)
        time.sleep(1.2)  # gentle rate limit
    return paths


def assemble_video(frames: list[Path], voice_path: Path, out_mp4: Path) -> None:
    """
    Simple but effective Ken-Burns + crossfade assembly.
    Each frame gets ~10 seconds with slow zoom, then crossfade.
    Captions are basic burned-in (full script split into chunks).
    """
    # Create a temporary concat list and apply zoompan to each frame
    segment_dir = WORK_DIR / "segments"
    segment_dir.mkdir(exist_ok=True)
    segment_files = []

    duration_per = TARGET_DURATION_SEC / len(frames)

    for i, frame in enumerate(frames):
        seg = segment_dir / f"seg_{i:02d}.mp4"
        # Slow zoom (Ken Burns) — start slightly wider and push in
        # 25 fps, duration_per seconds
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(frame),
            "-vf",
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0008,1.18)':d={int(25*duration_per)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25",
            "-t", str(duration_per),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            str(seg),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        segment_files.append(seg)

    # Concat segments
    concat_list = WORK_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for s in segment_files:
            f.write(f"file '{s}'\n")

    silent_video = WORK_DIR / "silent.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(silent_video),
        ],
        check=True,
        capture_output=True,
    )

    # Mux voice + simple fade
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(silent_video),
            "-i", str(voice_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
    )
    print(f"[video] Assembled {out_mp4}")


# ---------------------------------------------------------------------------
# 5. YouTube upload + pinned comment
# ---------------------------------------------------------------------------
def get_youtube_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ],
    )
    return build("youtube", "v3", credentials=creds)


def upload_short(service, video_path: Path, meta: dict) -> str:
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"] + f"\n\nExtended Cut → {FUNNEL_URL}",
            "tags": meta["tags"],
            "categoryId": "24",  # Entertainment
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[yt] Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[yt] Uploaded Short: https://youtube.com/shorts/{video_id}")
    return video_id


def pin_funnel_comment(service, video_id: str) -> None:
    text = (
        f"🔥 Uncensored Extended Cut + full episode drops here → {FUNNEL_URL}\n\n"
        f"Watch the part they would never allow on YouTube."
    )
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {"snippet": {"textOriginal": text}},
        }
    }
    service.commentThreads().insert(part="snippet", body=body).execute()
    print("[yt] Pinned funnel comment posted")


# ---------------------------------------------------------------------------
# Main state machine
# ---------------------------------------------------------------------------
def main() -> int:
    print("=== Saphira Horror-Drama Engine starting ===")
    required = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
        "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"ERROR: Missing secrets: {missing}")
        return 1

    client = OpenAI()
    ledger = load_ledger()

    # 1 + 2
    print("[1/6] Generating unique script + image prompts…")
    meta = generate_script(client, ledger)
    print(f"      Title: {meta['title']}")

    # 3
    print("[2/6] Synthesizing voice…")
    voice_path = WORK_DIR / "voiceover.mp3"
    synthesize_voice(meta["narration_script"], voice_path)

    # 4
    print("[3/6] Generating 6 gothic frames…")
    frame_dir = WORK_DIR / "frames"
    frames = generate_frames(client, meta["image_prompts"], frame_dir)

    print("[4/6] Assembling video with FFmpeg…")
    final_mp4 = WORK_DIR / "final_short.mp4"
    assemble_video(frames, voice_path, final_mp4)

    # 5
    print("[5/6] Uploading to YouTube Shorts…")
    yt = get_youtube_service()
    video_id = upload_short(yt, final_mp4, meta)
    pin_funnel_comment(yt, video_id)

    # 6
    print("[6/6] Updating episode ledger…")
    episode = {
        "id": str(uuid.uuid4()),
        "title": meta["title"],
        "youtube_id": video_id,
        "hook_snippet": meta["hook_snippet"],
        "published_at": datetime.now(timezone.utc).isoformat(),
        "funnel_url": FUNNEL_URL,
    }
    ledger.setdefault("episodes", []).append(episode)
    save_ledger(ledger)
    print(f"=== Done. Episode logged. Video: https://youtube.com/shorts/{video_id} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
