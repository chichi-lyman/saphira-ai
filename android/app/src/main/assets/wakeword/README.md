# Saphira wake-word model

Expected production asset: `saphira.onnx`.

Target phrases:
- `Hey Saphira`
- `Okay Saphira`

The Android runtime uses ONNX Runtime locally. The model file is intentionally not checked into this repository because a trained wake-word model must be licensed/owned and its tensor contract must match the preprocessing/postprocessing adapter.

When the model is supplied, place it at:

`android/app/src/main/assets/wakeword/saphira.onnx`

Required model contract should document:
- PCM sample rate
- frame/window size
- feature extraction
- input tensor name/shape
- output tensor name/shape
- score threshold
- cooldown duration

Until the model is present, the app fails closed and does not claim that always-on local wake-word detection is active.
