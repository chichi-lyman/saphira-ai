# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Full Orchestrator Chain for the Six Core Agents
# Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero
# + Avatar state hints for the holographic Chelsea-look UI
# + Optional Node invokes (code / canvas / camera)
# + Face recognition path (Aura perception + NovaAethrea memory)

from typing import Dict, Any, List, Optional
import logging
from src.agents.core_agents import (
    SaphiraCore,
    AgentZero,
    AgentTwo,
    Aura,
    NovaReign,
    NovaAethrea,
)
from src.core.face_intents import FACE_INTENTS, detect_face_intent, public_face_message

logger = logging.getLogger("SaphiraOrchestrator")


def _avatar_state_for(final: Dict[str, Any], intent: str = "general") -> str:
    """Map pipeline outcome → SaphiraAvatarView state."""
    status = final.get("status", "")
    if status == "needs_confirmation":
        return "confirm"
    if status in ("blocked", "rejected"):
        return "thinking"
    if status == "scene_executed":
        return "glow"
    if intent in FACE_INTENTS:
        return "talking"
    if intent in ("general",) or status == "success":
        return "talking"
    if intent not in ("general", "activate_scene"):
        return "talking"
    return "idle"


class SaphiraOrchestrator:
    """
    Runs the complete multi-agent pipeline:

    1. Saphira     – NLP + intent parsing
    2. Aura        – perception / room / entity / face context
    3. Agent Two   – security gate
    4. Nova Reign  – governance / policy
    5. NovaAethrea – memory + scene expansion + face ledger
    6. Agent Zero  – final execution (Matter / HA / system / nodes)
    """

    def __init__(self, router=None):
        self.saphira = SaphiraCore(router)
        self.aura = Aura(router)
        self.agent_two = AgentTwo(router)
        self.nova_reign = NovaReign(router)
        self.nova_aethrea = NovaAethrea(router)
        self.agent_zero = AgentZero(router)
        # Lightweight face service (agents package)
        try:
            from agents.aura import AuraAgent

            self._face_aura = AuraAgent()
        except Exception:
            self._face_aura = None

    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        trace: List[Dict[str, Any]] = []
        image_b64 = context.get("image_b64")
        has_image = bool(image_b64)

        # ---- Fast path: explicit face intent from text or image ----
        face_intent, face_params = detect_face_intent(user_input, has_image=has_image)
        if face_intent:
            return await self._process_face(face_intent, face_params, user_input, context, trace)

        # ---- 1. Saphira: NLP + intent ----
        saphira_result = await self.saphira.safe_run({
            "text": user_input,
            "message": user_input,
            **context,
        })
        trace.append(saphira_result)
        if saphira_result.get("status") not in ("success", "recovered_from_failure"):
            return self._finalize(trace, saphira_result, intent="general")

        payload = saphira_result.get("payload", {"text": user_input})
        intent = payload.get("intent") or saphira_result.get("parsed_intent", {}).get("intent", "general")

        # Secondary face check on parsed intent string
        if intent in FACE_INTENTS or "face" in str(intent).lower():
            fi, fp = detect_face_intent(user_input, has_image=has_image)
            if fi:
                return await self._process_face(fi, fp, user_input, context, trace)

        # ---- 2. Aura: perception & entity suggestions ----
        aura_result = await self.aura.safe_run({
            **payload,
            "context": context,
            "intent": intent,
        })
        trace.append(aura_result)

        params = payload.get("params", {})
        if not params.get("entity_id") and aura_result.get("suggested_entities"):
            params["entity_id"] = aura_result["suggested_entities"][0]
            payload["params"] = params

        # ---- 3. Agent Two: security ----
        security_result = await self.agent_two.safe_run({
            **payload,
            "intent": intent,
            "confirmed": context.get("confirmed", False),
        })
        trace.append(security_result)
        if security_result.get("status") == "blocked":
            return self._finalize(trace, {
                "status": "needs_confirmation",
                "message": security_result.get("message"),
                "intent": intent,
            }, intent=intent)

        # ---- 4. Nova Reign: governance ----
        governance_result = await self.nova_reign.safe_run({
            **payload,
            "intent": intent,
        })
        trace.append(governance_result)
        if governance_result.get("status") == "rejected":
            return self._finalize(trace, governance_result, intent=intent)

        # ---- 5. NovaAethrea: memory + scenes ----
        memory_result = await self.nova_aethrea.safe_run({
            **payload,
            "intent": intent,
            "scene": payload.get("matched_phrase") or intent,
        })
        trace.append(memory_result)

        if memory_result.get("status") == "scene_ready":
            step_results = []
            for step in memory_result.get("steps", []):
                step_payload = {
                    "intent": step["intent"],
                    "params": step.get("params", {}),
                    "confirmed": True,
                }
                exec_result = await self.agent_zero.safe_run(step_payload)
                step_results.append(exec_result)
            return self._finalize(trace, {
                "status": "scene_executed",
                "scene": memory_result.get("scene"),
                "steps": step_results,
                "message": f"Scene '{memory_result.get('scene')}' completed.",
            }, intent=intent)

        # ---- 6. Agent Zero: single action / node execution ----
        if intent not in ("general", "activate_scene"):
            exec_result = await self.agent_zero.safe_run({
                **payload,
                "intent": intent,
                "params": params,
            })
            trace.append(exec_result)
            return self._finalize(trace, exec_result, intent=intent)

        return self._finalize(trace, {
            "status": "success",
            "message": "Request processed. No device action required.",
            "intent": intent,
            "memory": memory_result,
        }, intent=intent)

    async def _process_face(
        self,
        intent: str,
        params: Dict[str, Any],
        user_input: str,
        context: Dict[str, Any],
        trace: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Dedicated path: Aura (perception) + NovaAethrea (memory) for faces."""
        image_b64 = context.get("image_b64")
        consent_token = context.get("consent_token") or params.get("consent_token")

        # List / forget do not need an image
        if intent == "face_list":
            mem = await self.nova_aethrea.safe_run({"intent": "face_list"})
            trace.append(mem)
            msg = public_face_message("face_list", mem)
            return self._finalize(trace, {
                "status": "success",
                "intent": intent,
                "message": msg,
                "faces": mem.get("faces", []),
            }, intent=intent)

        if intent == "face_forget":
            mem = await self.nova_aethrea.safe_run({
                "intent": "face_forget",
                "params": {"label": params.get("label")},
            })
            trace.append(mem)
            msg = public_face_message("face_forget", mem)
            return self._finalize(trace, {
                "status": mem.get("status", "ok"),
                "intent": intent,
                "message": msg,
                "label": mem.get("label"),
            }, intent=intent)

        # Recognize / enroll need perception
        if not image_b64:
            return self._finalize(trace, {
                "status": "needs_image",
                "intent": intent,
                "message": "I'd need a photo to look at a face. You can share one or open the camera.",
            }, intent=intent)

        known: List[Dict[str, Any]] = []
        if hasattr(self.nova_aethrea, "get_known_faces_for_perception"):
            known = self.nova_aethrea.get_known_faces_for_perception()

        perception: Dict[str, Any] = {"status": "error", "message": "Face service unavailable"}
        if self._face_aura is not None:
            perception = self._face_aura.perceive({
                "type": "face",
                "image_b64": image_b64,
                "known_faces": known,
                "return_embeddings": intent == "face_enroll",
            })
        trace.append({"agent": "aura", "modality": "face", **perception})

        if intent in ("face_recognize", "face_who"):
            msg = public_face_message(intent, perception)
            return self._finalize(trace, {
                "status": "success",
                "intent": intent,
                "message": msg,
                "matches": perception.get("matches", []),
                "requires_consent": perception.get("requires_consent", False),
                "faces_detected": perception.get("faces_detected", 0),
            }, intent=intent)

        if intent == "face_enroll":
            label = params.get("label")
            if not label:
                return self._finalize(trace, {
                    "status": "needs_confirmation",
                    "intent": intent,
                    "message": "What name should I use for this face?",
                    "requires_consent": True,
                }, intent=intent)

            if not consent_token and not context.get("confirmed"):
                return self._finalize(trace, {
                    "status": "needs_confirmation",
                    "intent": intent,
                    "message": f"Just to confirm — should I remember this face as {label}?",
                    "requires_consent": True,
                    "label": label,
                }, intent=intent)

            # Extract embedding
            if self._face_aura is None:
                return self._finalize(trace, {
                    "status": "error",
                    "intent": intent,
                    "message": "Face perception isn't available right now.",
                }, intent=intent)

            token = consent_token or "user-confirmed"
            enroll = self._face_aura.enroll_face(
                image_payload={"image_b64": image_b64},
                label=label,
                consent_token=token,
            )
            trace.append({"agent": "aura", "action": "enroll", **enroll})

            if enroll.get("status") != "ok":
                msg = public_face_message("face_enroll", enroll)
                return self._finalize(trace, {
                    "status": enroll.get("status", "error"),
                    "intent": intent,
                    "message": msg,
                }, intent=intent)

            mem = await self.nova_aethrea.safe_run({
                "intent": "face_enroll",
                "params": {
                    "label": label,
                    "embedding": enroll["embedding"],
                    "consent_token": token,
                },
            })
            trace.append(mem)
            msg = public_face_message("face_enroll", {**mem, "label": label})
            return self._finalize(trace, {
                "status": "success",
                "intent": intent,
                "message": msg,
                "label": label,
            }, intent=intent)

        return self._finalize(trace, {
            "status": "success",
            "intent": intent,
            "message": public_face_message(intent, perception),
        }, intent=intent)

    def _finalize(
        self,
        trace: List[Dict[str, Any]],
        final: Dict[str, Any],
        intent: str = "general",
    ) -> Dict[str, Any]:
        avatar_state = _avatar_state_for(final, intent)
        return {
            "final": final,
            "trace": trace,
            "agents_involved": [t.get("agent") for t in trace if t.get("agent")],
            "avatar_state": avatar_state,
            "owner": "Chelsea Megan Woods",
        }
