# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Always-on wake-word engine for Saphira.
# Supports "okay saphira", "saphira", "hey saphira".
# Cross-platform: Chromebook/Linux, Android bridge, Bluetooth audio routing.
# Engines: openWakeWord (preferred local), Porcupine (optional), transcription fallback.
# Integrates with evolution_core for self-healing on stream failures.

from __future__ import annotations

import logging
import os
import queue
import threading
from enum import Enum
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger("SaphiraWakeWord")

try:
    from src.core.evolution_engine import evolution_core
except ImportError:
    evolution_core = None


class WakeWordEngine(str, Enum):
    TRANSCRIPTION = "transcription"
    OPENWAKEWORD = "openwakeword"
    PORCUPINE = "porcupine"


WAKE_PHRASES = ["okay saphira", "hey saphira", "saphira"]


class SaphiraWakeWordListener:
    """
    Continuous low-power wake-word detector.
    On detection the on_wake callback is invoked so Aura perception can
    start the verbal conversation loop. Internal agent identities remain masked.
    """

    def __init__(
        self,
        engine: WakeWordEngine = WakeWordEngine.OPENWAKEWORD,
        sensitivity: float = 0.5,
        on_wake: Optional[Callable[[str], None]] = None,
        sample_rate: int = 16000,
    ) -> None:
        self.engine = engine
        self.sensitivity = max(0.1, min(1.0, sensitivity))
        self.on_wake = on_wake
        self.sample_rate = sample_rate
        self._running = False
        self._audio_queue: queue.Queue = queue.Queue(maxsize=50)
        self._thread: Optional[threading.Thread] = None

        self._oww_model = None
        self._porcupine = None
        self.block_size = 1280

        if self.engine == WakeWordEngine.PORCUPINE:
            self.block_size = 512

        if evolution_core:
            evolution_core.register_fallback("wake_word", self._heal_audio_stream)

    def start(self) -> None:
        if self._running:
            return
        self._init_engine()
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="SaphiraWakeWord")
        self._thread.start()
        logger.info(
            "Saphira wake-word listener started (engine=%s, sensitivity=%.2f)",
            self.engine.value,
            self.sensitivity,
        )

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.5)
        self._cleanup_engine()
        logger.info("Saphira wake-word listener stopped")

    def _heal_audio_stream(self, error: Exception) -> None:
        logger.warning("Wake-word self-heal triggered: %s — restarting stream", error)
        self.stop()
        self.start()

    def _init_engine(self) -> None:
        if self.engine == WakeWordEngine.OPENWAKEWORD:
            try:
                from openwakeword.model import Model
                model_path = os.getenv("SAPHIRA_OWW_MODEL_PATH")
                kwargs = {"inference_framework": "onnx"}
                if model_path and os.path.isfile(model_path):
                    kwargs["wakeword_models"] = [model_path]
                self._oww_model = Model(**kwargs)
                logger.debug("openWakeWord ONNX model loaded")
            except Exception as exc:
                logger.error("openWakeWord init failed: %s — falling back to transcription", exc)
                self.engine = WakeWordEngine.TRANSCRIPTION

        elif self.engine == WakeWordEngine.PORCUPINE:
            try:
                import pvporcupine
                access_key = os.getenv("PORCUPINE_ACCESS_KEY")
                if not access_key:
                    raise ValueError("PORCUPINE_ACCESS_KEY required")
                custom = os.getenv("PORCUPINE_MODEL_PATH")
                if custom and os.path.isfile(custom):
                    self._porcupine = pvporcupine.create(
                        access_key=access_key,
                        keyword_paths=[custom],
                        sensitivities=[self.sensitivity],
                    )
                else:
                    self._porcupine = pvporcupine.create(
                        access_key=access_key,
                        keywords=["jarvis", "computer"],
                        sensitivities=[self.sensitivity],
                    )
                self.block_size = self._porcupine.frame_length
            except Exception as exc:
                logger.error("Porcupine init failed: %s — falling back to transcription", exc)
                self.engine = WakeWordEngine.TRANSCRIPTION

    def _cleanup_engine(self) -> None:
        if self._porcupine is not None:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None
        self._oww_model = None

    def _listen_loop(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice required for Chromebook/Linux capture")
            return

        def callback(indata, frames, time_info, status):
            if status:
                logger.warning("Audio status: %s", status)
            try:
                self._audio_queue.put_nowait(indata.copy().flatten())
            except queue.Full:
                pass

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.block_size,
                callback=callback,
            ):
                while self._running:
                    try:
                        frame = self._audio_queue.get(timeout=0.4)
                        phrase = self._detect(frame)
                        if phrase:
                            logger.info("Wake phrase detected: %s", phrase)
                            if self.on_wake:
                                threading.Thread(
                                    target=self.on_wake,
                                    args=(phrase,),
                                    daemon=True,
                                    name="SaphiraWakeCallback",
                                ).start()
                    except queue.Empty:
                        continue
                    except Exception as exc:
                        logger.exception("Frame processing error: %s", exc)
        except Exception as exc:
            logger.exception("Audio stream failure: %s", exc)

    def _detect(self, frame: np.ndarray) -> Optional[str]:
        if self.engine == WakeWordEngine.OPENWAKEWORD and self._oww_model is not None:
            try:
                scores = self._oww_model.predict(frame)
                for name, score in scores.items():
                    if score >= self.sensitivity:
                        return name
            except Exception as exc:
                logger.debug("openWakeWord predict error: %s", exc)

        elif self.engine == WakeWordEngine.PORCUPINE and self._porcupine is not None:
            try:
                pcm = (frame * 32767.0).astype(np.int16)
                if len(pcm) != self._porcupine.frame_length:
                    return None
                idx = self._porcupine.process(pcm)
                if idx >= 0:
                    return WAKE_PHRASES[0]
            except Exception as exc:
                logger.debug("Porcupine process error: %s", exc)

        return None


def create_wake_listener(
    on_wake: Callable[[str], None],
    engine: Optional[str] = None,
) -> SaphiraWakeWordListener:
    eng = (engine or os.getenv("SAPHIRA_WAKE_ENGINE", "openwakeword")).lower()
    try:
        engine_enum = WakeWordEngine(eng)
    except ValueError:
        engine_enum = WakeWordEngine.OPENWAKEWORD
    sens = float(os.getenv("SAPHIRA_WAKE_SENSITIVITY", "0.5"))
    if evolution_core:
        sens = float(evolution_core.get_param("wake_sensitivity", sens))
    return SaphiraWakeWordListener(
        engine=engine_enum,
        sensitivity=sens,
        on_wake=on_wake,
    )
