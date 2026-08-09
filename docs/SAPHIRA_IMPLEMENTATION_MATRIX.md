# Saphira AI — Implementation Matrix

This matrix prevents the repository from confusing a documented capability with a connected production implementation.

| Domain | Core contract | Existing repo signal | Runtime status | Next integration |
|---|---|---|---|---|
| Conversation/persona | `persona.conversation` | `src/core/saphira_persona.py` | Foundation exists | Connect executive response layer |
| Voice STT/TTS | `voice.transcribe`, `voice.synthesize` | voice profile, voice service, TTS router | Foundation exists | Streaming provider adapter + barge-in |
| Multimodal vision | `vision.analyze` | multimodal registry/docs | Foundation exists | Normalize vision adapter into worker runtime |
| Orchestration | `reasoning.plan` | multiple orchestrators + new executive runtime | Consolidating | Make executive runtime authoritative |
| Persistent memory | `memory.read/write` | `src/memory/persistent_store.py` | Foundation exists | Connect operational + long-term memory |
| Developer/sandbox | `code.sandbox` | agent/developer infrastructure | Partial | Isolated execution adapter + QA loop |
| Web grounding | `web.search` | documented web/search capabilities | Partial | Permissioned live-search adapter |
| OS/files | filesystem + telemetry | on-device/mobile architecture | Adapter required | Host-side scoped system adapter |
| IoT | `iot.read/control` | Matter/integration documentation | Adapter required | Home Assistant/Matter adapters |
| CAD/3D | `cad.generate` | Ada bridge / multimodal docs | Contract added | OpenSCAD/build123d provider |
| STEM/math | `stem.calculate` | agent architecture | Contract added | Deterministic calculator/code tool |
| Communications | draft/send | automation/tool architecture | Permissioned | Email/messaging adapters |
| Commerce | catalog/purchase | commerce ecosystem direction | Permissioned | Shopify integration |
| Proactive automation | `schedule.create` | proactive/presence concepts | Partial | Scheduler + event bus |
| Verification | `quality.verify` | QA/verification concepts | Foundation exists | Mandatory post-action verifier |

## Rule

A capability is **available** only when its adapter is connected, permissions are configured, health checks pass, and the relevant tests pass. Documentation or an agent name alone does not count as production availability.

## Target execution loop

`Conversation → Context/Memory → Plan → Capability Routing → Approval Policy → Worker Execution → Tool Adapter → Verification → Memory → Conversational Result`

Saphira should expose this as one assistant experience even when many agents execute behind the scenes.
