# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Real-time barge-in detection while TTS is speaking.
# Continuously measures microphone RMS energy; if speech is detected
# the current TTS playback is stopped and the system returns to listening.
# Registers with evolution_core for self-healing.

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger("SaphiraInterruption")

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    from src.core.evolution_engine import evolution_core
except ImportError:
    evolution_core = None


class InterruptionOrchestrator:
    """
    Monitors microphone energy while TTS is active.
    On detected user speech, invokes on_interrupt so the TTS engine
    can be stopped and the conversation loop returned to listening state.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        block_duration_ms: float = 50.0,
        rms_threshold: float = 0.02,
        consecutive_blocks: int = 3,
        on_interrupt: Optional[Callable[[], None]] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.block_size = int(sample_rate * block_duration_ms / 1000.0)
        self.rms_threshold = rms_threshold
        if evolution_core:
            self.rms_threshold = float(evolution_core.get_param("barge_in_rms", rms_threshold))
        self.consecutive_blocks = consecutive_blocks
        self.on_interrupt = on_interrupt

        self._running = False
        self._tts_active = False
        self._hit_count = 0
        self._thread: Optional[threading.Thread] = None
        self._stream = None

        if evolution_core:
            evolution_core.register_fallback("interruption", self._heal)

    def set_tts_active(self, active: bool) -> None:
        self._tts_active = active
        self._hit_count = 0
        logger.debug("TTS active=%s — barge-in monitoring %s", active, "enabled" if active else "paused")

    def start(self) -> None:
        if self._running or sd is None:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="SaphiraBargeIn")
        self._thread.start()
        logger.info("Interruption orchestrator started")

    def stop(self) -> None:
        self._running = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        logger.info("Interruption orchestrator stopped")

    def _heal(self, error: Exception) -> None:
        logger.warning("Interruption self-heal: %s — restarting monitor", error)
        self.stop()
        self.start()

    def _monitor_loop(self) -> None:
        def callback(indata, frames, time_info, status):
            if status:
                logger.warning("Barge-in audio status: %s", status)
            if not self._tts_active:
                self._hit_count = 0
                return
            rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
            if rms >= self.rms_threshold:
                self._hit_count += 1
                if self._hit_count >= self.consecutive_blocks:
                    logger.info("User speech detected during TTS (RMS=%.4f) — interrupting", rms)
                    self._hit_count = 0
                    if self.on_interrupt:
                        threading.Thread(target=self.on_interrupt, daemon=True).start()
            else:
                self._hit_count = max(0, self._hit_count - 1)

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.block_size,
                callback=callback,
            )
            self._stream.start()
            while self._running:
                sd.sleep(200)
        except Exception as exc:
            logger.exception("Barge-in monitor failure: %s", exc)
        finally:
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
