import asyncio
import numpy as np
import logging
from typing import AsyncGenerator, Callable, Optional, Dict, Any
import queue
import threading

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

logger = logging.getLogger("SaphiraSTTStream")


class StreamingAudioTranscriber:
    """
    Low-Latency Streaming Speech-to-Text Engine for Saphira.
    Captures live audio via sounddevice, filters silence using VAD,
    and streams real-time transcriptions using faster-whisper.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "default",
        sample_rate: int = 16000,
        chunk_duration_sec: float = 0.5,
        vad_silence_duration_ms: int = 500,
    ):
        self.sample_rate = sample_rate
        self.chunk_size = int(self.sample_rate * chunk_duration_sec)
        self.vad_silence_ms = vad_silence_duration_ms
        self.is_recording = False
        
        self._audio_queue: queue.Queue = queue.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Load Faster-Whisper Model
        if WhisperModel:
            logger.info(f"Loading Whisper model '{model_size}' on {device} ({compute_type})...")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        else:
            self.model = None
            logger.warning("faster-whisper is not installed. STT engine running in mock mode.")

    # --- Microphone Audio Stream Handler ---

    def _audio_callback(self, indata, frames, time, status):
        """Callback invoked by sounddevice for every raw PCM audio frame."""
        if status:
            logger.warning(f"Audio Stream Status Warning: {status}")
        # Convert audio to float32 normalized array (-1.0 to 1.0)
        audio_data = indata.copy().flatten().astype(np.float32)
        self._audio_queue.put(audio_data)

    async def start_listening(self) -> AsyncGenerator[str, None]:
        """
        Asynchronous generator that listens to the audio stream and yields transcribed text segments.
        """
        if not sd:
            raise RuntimeError("sounddevice is not installed. Install with `pip install sounddevice`.")

        self.is_recording = True
        self._loop = asyncio.get_running_loop()

        # Start continuous sounddevice input stream
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.chunk_size,
            callback=self._audio_callback
        )

        logger.info("Microphone stream started. Listening...")
        buffer = np.array([], dtype=np.float32)

        with stream:
            while self.is_recording:
                # Retrieve available chunks from queue non-blockingly
                chunks = []
                while not self._audio_queue.empty():
                    chunks.append(self._audio_queue.get_nowait())

                if chunks:
                    new_data = np.concatenate(chunks)
                    buffer = np.concatenate([buffer, new_data])

                    # Process audio buffer once accumulated duration exceeds minimum processing window (e.g., 2.0s)
                    if len(buffer) >= self.sample_rate * 2.0:
                        text = await self._transcribe_buffer(buffer)
                        if text:
                            yield text
                        # Keep trailing 0.5s audio for context boundary continuity
                        buffer = buffer[-int(self.sample_rate * 0.5):]

                await asyncio.sleep(0.05)

    def stop_listening(self):
        """Stops the active recording loop."""
        self.is_recording = False
        logger.info("Microphone audio stream stopped.")

    # --- Core Whisper Transcription Execution ---

    async def _transcribe_buffer(self, audio_data: np.ndarray) -> str:
        """Executes non-blocking Whisper transcription with VAD filtering on current buffer."""
        if not self.model:
            # Fallback mock response for testing environment
            return "[Mock STT] Transcribed input utterance."

        def _transcribe():
            # vad_filter uses Silero VAD under the hood in faster-whisper
            segments, info = self.model.transcribe(
                audio_data,
                beam_size=1,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=self.vad_silence_ms),
                language="en"
            )
            text_segments = [segment.text.strip() for segment in segments if segment.text.strip()]
            return " ".join(text_segments)

        # Run transcription off the main async thread
        loop = asyncio.get_running_loop()
        transcribed_text = await loop.run_in_executor(None, _transcribe)
        return transcribed_text


# --- Integration Helper with Saphira Core ---

async def listen_and_dispatch(transcriber: StreamingAudioTranscriber, dispatch_func: Callable[[str], None]):
    """Helper to pipe real-time streaming transcripts directly into Saphira's orchestrator."""
    async for transcribed_text in transcriber.start_listening():
        if transcribed_text:
            logger.info(f"[Live Speech Detected]: {transcribed_text}")
            await dispatch_func(transcribed_text)
                      
