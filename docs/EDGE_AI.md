# Edge AI Development Notes for Saphira

## Goals
- Keep wake-word, intent classification, and basic biometric stress estimation 100% on-device.
- Use quantized small language models (SLMs) for offline replies.
- Only escalate to cloud for heavy multimodal or long-context reasoning.

## Recommended Stack
- ONNX Runtime / TensorFlow Lite for wake-word + vision models
- Quantized Llama-3.2 / Phi-3 / Gemma-2B for local reasoning
- MediaPipe for camera gesture & object detection
- Health Connect / BLE for wearable streams

## Latency Targets
- Wake-word detection: < 80 ms
- Local intent classification: < 120 ms
- Offline reply (short): < 400 ms
- Full multimodal cloud round-trip: < 1.2 s when online

## Self-Healing Philosophy
Every controlled failure (timeout, exception, corrupted payload, simulated lag)
is an opportunity for the system to practice recovery and become
1% faster, 1% smarter, and 1% more resilient.
