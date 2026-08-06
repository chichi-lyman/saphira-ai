# Saphira wake-word models

Place trained OpenWakeWord files here:

```
models/wakeword/saphira.onnx
models/wakeword/saphira.tflite   # optional
```

## Train a custom "Hey Saphira" model

**Recommended (2026):** [openwakeword-colab-2026](https://github.com/alfiedennen/openwakeword-colab-2026)

```python
TARGET_PHRASE = ['hey saphira', 'saphira']
MODEL_NAME = 'saphira'
```

Or Docker: [atlas-voice-training](https://github.com/briankelley/atlas-voice-training)

See `saphira_training.yml` for reference config.

## Use with listener

```python
from openwakeword.model import Model
model = Model(wakeword_models=["models/wakeword/saphira.onnx"], inference_framework="onnx")
# on detect → POST /presence/wake
```

Start with threshold `0.5`; raise to `0.6–0.7` if you get false wakes.
