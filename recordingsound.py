"""
Audio recording and speech-to-text conversion using Adafruit I2S MEMS microphone on Raspberry Pi.
Uses ALSA drivers and sounddevice for hardware audio input.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime


class I2SMicrophoneRecorder:
    """
    Handles recording audio from an Adafruit I2S MEMS microphone on Raspberry Pi.
    
    Uses PortAudio's default input device unless a PortAudio device index is
    explicitly provided. This is intentionally different from ALSA card
    numbering; use `sounddevice.query_devices()` to find PortAudio indices.

    For the Adafruit SPH0645 breakout, the usual Raspberry Pi wiring is
    BCLK -> GPIO18, LRCLK -> GPIO19, and DOUT -> GPIO20. Configure its sound
    card in Raspberry Pi OS separately; see SETUP_GUIDE.md.
    """
    
    def __init__(self, sample_rate=16000, device=None, channels=1):
        """
        Initialize the I2S microphone recorder.
        
        Args:
            sample_rate (int): Sample rate in Hz (default: 16000 Hz)
            device (int or str): PortAudio input device index or name. None uses
                the system default input, as in soundtest.py.
            channels (int): Number of audio channels (default: 1 for mono)
        """
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if channels <= 0:
            raise ValueError("channels must be positive")

        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

        if device is None:
            default_device = sd.default.device[0]
            print("Using PortAudio's default input device.")
            if default_device is None or default_device < 0:
                print("Available input devices:")
                for index, info in enumerate(sd.query_devices()):
                    if info["max_input_channels"] > 0:
                        print(f"  {index}: {info['name']}")
            else:
                info = sd.query_devices(default_device)
                print(f"  {default_device}: {info['name']}")
        else:
            info = sd.query_devices(device)
            if info["max_input_channels"] < channels:
                raise ValueError(
                    f"Input device {device!r} supports only "
                    f"{info['max_input_channels']} channel(s)"
                )
            print(f"Using PortAudio input device {device}: {info['name']}")

        sd.check_input_settings(
            device=device,
            channels=channels,
            dtype="int16",
            samplerate=sample_rate,
        )
        print(f"I2S microphone initialized:")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Channels: {channels}")

    def record(self, duration_seconds, output_file=None):
        """
        Record audio from the I2S microphone.
        
        Args:
            duration_seconds (float): Duration of recording in seconds
            output_file (str): Optional filename to save the recording (WAV format)
        
        Returns:
            tuple: (audio_data as numpy array, sample_rate)
        """
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")

        num_samples = int(self.sample_rate * duration_seconds)
        
        print(f"\nRecording for {duration_seconds} seconds...")
        
        try:
            audio_data = sd.rec(
                num_samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                device=self.device
            )
            sd.wait()
        except Exception as e:
            raise RuntimeError(f"Audio capture failed: {e}") from e

        audio_normalized = audio_data.astype(np.float32) / 32768.0
        print(f"Recording complete: {len(audio_normalized)} samples ({duration_seconds}s)")

        if output_file:
            sf.write(output_file, audio_normalized, self.sample_rate)
            print(f"Audio saved to: {output_file}")

        return audio_normalized, self.sample_rate


class SpeechToTextConverter:
    """
    Convert audio to text using various speech-to-text backends.
    """
    
    def __init__(self, backend="google"):
        """
        Initialize speech-to-text converter.
        
        Args:
            backend (str): "google", "openai", or "vosk" (offline)
        """
        self.backend = backend
        
        if backend == "google":
            try:
                from google.cloud import speech_v1
                self.client = speech_v1.SpeechClient()
                print("Google Cloud Speech-to-Text initialized")
            except ImportError:
                print("Warning: google-cloud-speech not installed")
                self.client = None
        
        elif backend == "openai":
            try:
                import openai
                self.client = openai
                print("OpenAI Whisper initialized")
            except ImportError:
                print("Warning: openai library not installed")
                self.client = None
        
        elif backend == "vosk":
            try:
                from vosk import Model, KaldiRecognizer
                self.model = Model(lang="en-us")
                self.recognizer_class = KaldiRecognizer
                print("Vosk offline speech recognition initialized")
            except ImportError:
                raise ImportError(
                    "Vosk backend selected but not installed; run `pip install vosk`"
                ) from None
        else:
            raise ValueError(f"Unsupported speech-to-text backend: {backend}")
    
    def transcribe_google(self, audio_file):
        """
        Transcribe using Google Cloud Speech-to-Text API.
        Requires: pip install google-cloud-speech
        
        Args:
            audio_file (str): Path to audio file
        
        Returns:
            str: Transcribed text
        """
        if not self.client:
            return "Error: Google Cloud Speech client not initialized"
        
        try:
            from google.cloud.speech import RecognitionAudio, RecognitionConfig
            
            with open(audio_file, "rb") as f:
                audio_content = f.read()
            
            audio = RecognitionAudio(content=audio_content)
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = self.client.recognize(config=config, audio=audio)
            
            results = []
            for result in response.results:
                results.append(result.alternatives[0].transcript)
            
            return " ".join(results)
        
        except Exception as e:
            return f"Error in Google transcription: {e}"
    
    def transcribe_openai(self, audio_file):
        """
        Transcribe using OpenAI Whisper API.
        Requires: pip install openai
        
        Args:
            audio_file (str): Path to audio file
        
        Returns:
            str: Transcribed text
        """
        if not self.client:
            return "Error: OpenAI client not initialized"
        
        try:
            with open(audio_file, "rb") as f:
                transcript = self.client.Audio.transcribe("whisper-1", f)
            
            return transcript["text"]
        
        except Exception as e:
            return f"Error in OpenAI transcription: {e}"
    
    def transcribe_vosk(self, audio_array, sample_rate):
        """
        Transcribe using Vosk offline speech recognition.
        Requires: pip install vosk
        
        Args:
            audio_array (numpy array): Audio data
            sample_rate (int): Sample rate in Hz
        
        Returns:
            str: Transcribed text
        """
        if not hasattr(self, 'model') or self.model is None:
            return "Error: Vosk model not initialized"
        
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        import json

        audio_int16 = np.clip(audio_array * 32768.0, -32768, 32767).astype(
            np.int16
        )
        recognizer = self.recognizer_class(self.model, sample_rate)
        segments = []
        samples_per_chunk = 4000

        for start in range(0, len(audio_int16), samples_per_chunk):
            chunk = audio_int16[start:start + samples_per_chunk]
            if recognizer.AcceptWaveform(chunk.tobytes()):
                text = json.loads(recognizer.Result()).get("text", "")
                if text:
                    segments.append(text)

        final_text = json.loads(recognizer.FinalResult()).get("text", "")
        if final_text:
            segments.append(final_text)
        return " ".join(segments)
    
    def transcribe(self, audio_input):
        """
        Main transcription method that handles both file paths and audio arrays.
        
        Args:
            audio_input: Either a file path (str) or audio array (numpy)
        
        Returns:
            str: Transcribed text
        """
        if isinstance(audio_input, str):
            if self.backend == "google":
                return self.transcribe_google(audio_input)
            elif self.backend == "openai":
                return self.transcribe_openai(audio_input)
            else:
                return "File input requires google or openai backend"
        
        elif isinstance(audio_input, np.ndarray):
            if self.backend == "vosk":
                return self.transcribe_vosk(audio_input, 16000)
            else:
                return "Array input requires vosk backend"
        
        else:
            return "Invalid input type"


def main():
    """Example usage of audio recording and speech-to-text conversion."""
    
    # Use the same PortAudio default input as soundtest.py.
    recorder = I2SMicrophoneRecorder(sample_rate=48000)
    
    # Record 5 seconds of audio
    duration = 5.0
    output_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    
    audio_data, sample_rate = recorder.record(duration, output_filename)
    
    print("\n--- Audio Recording Complete ---")
    print(f"File: {output_filename}")
    print(f"Duration: {duration}s")
    print(f"Sample Rate: {sample_rate} Hz")

    transcriber = SpeechToTextConverter(backend="vosk")
    text = transcriber.transcribe_vosk(audio_data, sample_rate)
    print(f"Vosk Transcription:\n{text}\n")


if __name__ == "__main__":
    main()
