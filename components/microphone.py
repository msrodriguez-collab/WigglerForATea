"""Capture bounded mono audio clips from the default or selected input device."""

import math

import numpy as np
import sounddevice as sd


class MicrophoneRecorder:
    """Record short PCM audio clips for downstream speech processing."""

    def __init__(self, sample_rate: int = 16000, device: int | str | None = None) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        self.sample_rate = sample_rate
        self.device = device

    def record(self, duration_seconds: float) -> np.ndarray:
        """Return a mono int16 audio clip held in memory."""
        if not math.isfinite(duration_seconds) or duration_seconds <= 0:
            raise ValueError("duration_seconds must be a finite positive number")

        frame_count = round(self.sample_rate * duration_seconds)
        if frame_count < 1:
            raise ValueError("duration_seconds is too short to capture a sample")

        recording = sd.rec(
            frame_count,
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.device,
        )
        sd.wait()
        return np.ascontiguousarray(recording[:, 0])
