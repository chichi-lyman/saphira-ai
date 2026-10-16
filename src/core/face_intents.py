# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Shared face-intent detection for Saphira surface and multi-agent pipeline.

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

# Intents emitted into the pipeline
FACE_INTENTS = {
    "face_recognize",
    "face_enroll",
    "face_list",
    "face_forget",
    "face_who",
}

_REMEMBER_PATTERNS = [
    r"\bremember\s+(this|my|her|his|their)?\s*face\b",
    r"\bremember\s+(me|us|them)\b",
    r"\benroll\s+(this\s+)?face\b",
    r"\bsave\s+(this\s+)?face\b",
    r"\bthis\s+is\s+([A-Za-z][A-Za-z0-9_\- ]{0,40})\b",
    r"\bthat'?s\s+([A-Za-z][A-Za-z0-9_\- ]{0,40})\b",
    r"\bcall\s+(this|her|him|them)\s+([A-Za-z][A-Za-z0-9_\- ]{0,40})\b",
]

_FORGET_PATTERNS = [
    r"\bforget\s+(this\s+)?face\b",
    r"\bforget\s+([A-Za-z][A-Za-z0-9_\- ]{0,40})\b",
    r"\bremove\s+(the\s+)?face\b",
    r"\bdelete\s+(the\s+)?face\b",
]

_LIST_PATTERNS = [
    r"\bwho\s+do\s+you\s+(know|remember)\b",
    r"\blist\s+(the\s+)?faces\b",
    r"\bfaces\s+you\s+know\b",
    r"\bremembered\s+faces\b",
]

_WHO_PATTERNS = [
    r"\bwho\s+is\s+(this|that)\b",
    r"\bwho\s+am\s+i\b",
    r"\bdo\s+you\s+(see|recognize)\s+me\b",
    r"\brecognize\s+(this\s+)?face\b",
    r"\bwho'?s\s+(this|that)\b",
]


def _match_any(text: str, patterns: list[str]) -> Optional[re.Match]:
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m
    return None


def detect_face_intent(
    text: str,
    *,
    has_image: bool = False,
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Return (intent, params) if the utterance is face-related, else (None, {}).

    params may include:
      - label: suggested name for enrollment / forget
      - confirmed: whether language implies consent
    """
    t = (text or "").strip()
    if not t and not has_image:
        return None, {}

    # Forget
    m = _match_any(t, _FORGET_PATTERNS)
    if m:
        label = None
        if m.lastindex and m.lastindex >= 1:
            candidate = m.group(m.lastindex)
            if candidate and candidate.lower() not in ("this", "the", "face", "a"):
                label = candidate.strip()
        return "face_forget", {"label": label}

    # List
    if _match_any(t, _LIST_PATTERNS):
        return "face_list", {}

    # Remember / enroll
    m = _match_any(t, _REMEMBER_PATTERNS)
    if m:
        label = None
        # Try to pull a name from capture groups
        for i in range(1, (m.lastindex or 0) + 1):
            g = m.group(i)
            if g and g.lower() not in ("this", "my", "her", "his", "their", "me", "us", "them", "face"):
                label = g.strip()
                break
        # "this is X" / "that's X"
        name_m = re.search(
            r"(?:this\s+is|that'?s|call\s+(?:this|her|him|them))\s+([A-Za-z][A-Za-z0-9_\- ]{0,40})",
            t,
            flags=re.IGNORECASE,
        )
        if name_m:
            label = name_m.group(1).strip()
        return "face_enroll", {"label": label, "confirmed": bool(label)}

    # Who is this / recognize
    if _match_any(t, _WHO_PATTERNS) or has_image:
        return "face_recognize" if has_image or _match_any(t, _WHO_PATTERNS) else None, {}

    if has_image:
        return "face_recognize", {}

    return None, {}


def public_face_message(intent: str, result: Dict[str, Any]) -> str:
    """Translate internal face results into warm user-facing language."""
    status = result.get("status", "")

    if intent == "face_list":
        faces = result.get("faces") or []
        labels = [f.get("label") if isinstance(f, dict) else str(f) for f in faces]
        if not labels:
            return "I don't have any faces saved yet. If you'd like, show me someone and tell me their name."
        if len(labels) == 1:
            return f"I remember {labels[0]}."
        return "I remember " + ", ".join(labels[:-1]) + f", and {labels[-1]}."

    if intent == "face_forget":
        label = result.get("label") or "that face"
        if status in ("ok", "success"):
            return f"Okay — I've forgotten {label}."
        return f"I couldn't find a saved face for {label}."

    if intent == "face_enroll":
        label = result.get("label") or "them"
        if status in ("ok", "success", "stored"):
            return f"Got it. I'll remember this face as {label}."
        if status == "consent_required":
            return "I'd love to remember them — just tell me the name you'd like me to use."
        if status == "no_face":
            return "I couldn't quite see a clear face in that photo. Could you try another one?"
        return result.get("message") or "Something went wrong while saving that face."

    # recognize / who
    matches = result.get("matches") or []
    if matches:
        best = matches[0]
        name = best.get("label", "someone I know")
        conf = best.get("confidence", 0)
        if conf >= 0.75:
            return f"That's {name}."
        return f"That looks like {name}, though I'm not completely sure."

    if result.get("requires_consent") or result.get("faces_detected", 0) > 0:
        return "I see someone, but I don't have a name for them yet. Would you like me to remember this face?"

    if result.get("faces_detected", 0) == 0 or status == "no_face":
        return "I don't see a face clearly enough in that image."

    return result.get("message") or "I took a look."
