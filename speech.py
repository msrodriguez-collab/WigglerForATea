"""Capture audio and convert it to text with Google's online speech recognizer."""

import numpy as np
import speech_recognition as sr

from components.microphone import MicrophoneRecorder


class SpeechToText:
    """Convert mono int16 audio clips into text."""

    def __init__(self, language: str = "en-US") -> None:
        self.language = language
        self._recognizer = sr.Recognizer()

    def transcribe(self, audio_samples: np.ndarray, sample_rate: int) -> str:
        """Return a transcript; recognition and network errors propagate to the caller."""
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if audio_samples.dtype != np.int16:
            raise TypeError("audio_samples must contain int16 PCM samples")
        if audio_samples.ndim == 2 and audio_samples.shape[1] == 1:
            audio_samples = audio_samples[:, 0]
        elif audio_samples.ndim != 1:
            raise ValueError("audio_samples must be mono")
        if audio_samples.size == 0:
            raise ValueError("audio_samples must not be empty")

        audio_data = sr.AudioData(
            np.ascontiguousarray(audio_samples).tobytes(),
            sample_rate,
            2,
        )
        return self._recognizer.recognize_google(
            audio_data,
            language=self.language,
        )


def main() -> None:
    microphone = MicrophoneRecorder()
    speech_to_text = SpeechToText()

    print("Recording for 5 seconds...")
    audio_samples = microphone.record(5.0)
    try:
        transcript = speech_to_text.transcribe(
            audio_samples,
            sample_rate=microphone.sample_rate,
        )
    except sr.UnknownValueError:
        print("No clear speech was recognized.")
        return
    except sr.RequestError as error:
        raise RuntimeError(f"Speech recognition request failed: {error}") from error

    print(f"Transcript: {transcript}")


if __name__ == "__main__":
    main()
