# Saphira Autonomous Evolution Protocol

**© 2026 Chelsea Megan Woods. All Rights Reserved.**  
Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies  
Ecosystem: Nova Umbrella™

## Runtime Principles

1. **Absolute Honesty & Real-World Utility**  
   Saphira evaluates constraints truthfully. She never fabricates capabilities or hides limitations. Responses remain grounded, helpful, and free of sycophancy.

2. **24/7 Ambient Presence**  
   Persistent across Chromebook (ChromeOS Linux / Crostini systemd user units), Android (VoiceInteractionService + AlwaysOnHotwordDetector), and desktop. Bluetooth SCO/A2DP profile changes are handled gracefully.

3. **Continuous Local Optimisation (the +1 % rule)**  
   The evolution engine measures pipeline latency, wake-word false-accept/reject rates, barge-in success, and memory retrieval quality. Once per day it applies bounded, non-safety parameter adjustments (sensitivity, RMS thresholds, memory top-k, chunk sizes). Cumulative gain is tracked but never allowed to alter ethics, persona, or governance rules.

4. **Self-Healing**  
   Every major subsystem (wake-word listener, interruption orchestrator, STT stream, Bluetooth routing) registers a fallback with `SaphiraEvolutionCore`. On recoverable faults the registered handler restarts the affected stream or re-selects the audio device without terminating the parent process.

5. **Immutable Core**  
   The multi-agent pipeline remains fixed:  
   `Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)`.  
   Persona (warm, emotionally intelligent, never reveals internal agent names) and all CommercialAuthorityPolicy / audit invariants stay deterministic.

## Key Modules Added / Updated

| Path | Purpose |
|------|---------|
| `src/core/evolution_engine.py` | Sovereign loop, telemetry, safe parameter store, fallback registry |
| `voice/wake_word.py` | Always-on detection for “okay saphira” / “hey saphira” / “saphira” with self-heal |
| `voice/interruption_orchestrator.py` | Barge-in via RMS energy while TTS is speaking |
| `scripts/train_custom_wakeword.py` | Training orchestrator + documentation for custom openWakeWord ONNX |
| `android/.../SaphiraHardwareReceiver.kt` | Mutes mic on telephony / Bluetooth profile changes |

## Environment Variables

```
SAPHIRA_WAKE_ENGINE=openwakeword
SAPHIRA_WAKE_SENSITIVITY=0.45
SAPHIRA_OWW_MODEL_PATH=/path/to/voice/models/saphira.onnx
PORCUPINE_ACCESS_KEY=          # optional
PORCUPINE_MODEL_PATH=          # optional
```

## Self-Healing Verification Matrix

- Microphone / stream dropouts → `wake_word` / `interruption` fallbacks restart streams.
- Bluetooth profile transitions → Android receiver mutes, then service re-opens preferred device.
- Network loss → offline_mode + local models keep essential intent handling alive.
- Exception in any monitored task → counted in telemetry, logged, and recovered where possible.

## Deployment Notes

- Chromebook: user systemd unit + Pulse/PipeWire client.conf for host Bluetooth access.
- Phone: register `SaphiraHardwareReceiver` in the manifest; request runtime permissions for phone state and Bluetooth.
- Training: prefer 2026 Colab or Docker pipelines; place resulting ONNX under `voice/models/`.

Saphira improves through measured use while remaining honest, safe, and true to her original design.
