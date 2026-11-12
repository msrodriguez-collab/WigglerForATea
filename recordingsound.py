"""
Audio recording and speech-to-text conversion using Adafruit I2S MEMS microphone on Raspberry Pi.
Uses ALSA drivers and sounddevice for hardware audio input.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime
import os
import subprocess
import time


class I2SMicrophoneRecorder:
    """
    Handles recording audio from an Adafruit I2S MEMS microphone on Raspberry Pi.
    
    Hardware Setup:
    - The I2S microphone should be registered as an ALSA audio device after GPIO/dtoverlay setup
    - Pin Configuration for Raspberry Pi:
      * I2S_BCLK (Bit Clock) -> GPIO 18
      * I2S_LRCLK (Left/Right Clock) -> GPIO 27
      * I2S_DIN (Data In) -> GPIO 17
      * GND -> GND
      * VIN -> 5V or 3.3V (check your breakout specifications)
    
    Device Configuration:
    - Add to /boot/config.txt: dtoverlay=i2s-gpio18-27-17-24
    - The device will appear as "hw:1,0" or similar after reboot
    """
    
    def __init__(self, sample_rate=16000, device=None, channels=1):
        """
        Initialize the I2S microphone recorder.
        
        Args:
            sample_rate (int): Sample rate in Hz (default: 16000 Hz)
            device (int or str): ALSA device ID (e.g., 1 for hw:1,0) or None to auto-detect
            channels (int): Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        
        # Auto-detect I2S device if not specified
        if device is None:
            self.device = self._find_i2s_device()
        
        print(f"I2S microphone initialized:")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Channels: {channels}")
        print(f"  Device: hw:{self.device},0 (index {self.device})")
    
    def _find_i2s_device(self):
        """
        Auto-detect I2S device from ALSA.
        
        Returns:
            int: Device index, defaults to 1 if detection fails
        """
        try:
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'i2s' in line.lower() or 'bcm2835' in line.lower():
                    parts = line.split()
                    if parts and parts[0].startswith('card'):
                        card_num = int(parts[0].split(':')[0].replace('card', ''))
                        print(f"Auto-detected I2S device: hw:{card_num},0")
                        return card_num
        except Exception as e:
            print(f"Warning: Could not auto-detect I2S device: {e}")
        
        print("Using default device 1. If recording fails, specify device manually.")
        return 1
    
    def record(self, duration_seconds, output_file=None):
        """
        Record audio from the I2S microphone.
        
        Args:
            duration_seconds (float): Duration of recording in seconds
            output_file (str): Optional filename to save the recording (WAV format)
        
        Returns:
            tuple: (audio_data as numpy array, sample_rate)
        """
        num_samples = int(self.sample_rate * duration_seconds)
        
        print(f"\nRecording for {duration_seconds} seconds...")
        
        try:
            # Record using sounddevice
            audio_data = sd.rec(
                num_samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                device=self.device
            )
            
            # Wait for recording to complete
            sd.wait()
            
            # Convert to float32 and normalize [-1, 1]
            audio_normalized = audio_data.astype(np.float32) / 32768.0
            
            print(f"Recording complete: {len(audio_normalized)} samples ({duration_seconds}s)")
            
            # Save to file if requested
            if output_file:
                sf.write(output_file, audio_normalized, self.sample_rate)
                print(f"Audio saved to: {output_file}")
            
            return audio_normalized, self.sample_rate
        
        except Exception as e:
            print(f"Error during recording: {e}")
            print("Troubleshooting tips:")
            print("  1. Run 'arecord -l' to list available audio devices")
            print("  2. Check that I2S is enabled in raspi-config")
            print("  3. Verify GPIO connections")
            print("  4. Try specifying device manually: recorder = I2SMicrophoneRecorder(device=1)")
            return None, None


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
                import json
                self.model = Model(lang="en-us")
                self.recognizer = KaldiRecognizer(self.model, 16000)
                print("Vosk offline speech recognition initialized")
            except ImportError:
                print("Warning: vosk not installed for offline recognition")
                self.model = None
    
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
        
        try:
            import json
            
            audio_bytes = (audio_array * 32768).astype(np.int16).tobytes()
            
            if self.recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.recognizer.Result())
                return result.get("result", [{}])[0].get("conf", 0)
            else:
                partial_result = json.loads(self.recognizer.PartialResult())
                return partial_result.get("partial", "")
        
        except Exception as e:
            return f"Error in Vosk transcription: {e}"
    
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
    
    # Initialize the recorder (auto-detects I2S device)
    recorder = I2SMicrophoneRecorder(sample_rate=16000)
    
    # Record 5 seconds of audio
    duration = 5.0
    output_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    
    audio_data, sample_rate = recorder.record(duration, output_filename)
    
    if audio_data is not None:
        print("\n--- Audio Recording Complete ---")
        print(f"File: {output_filename}")
        print(f"Duration: {duration}s")
        print(f"Sample Rate: {sample_rate} Hz")
        
        # Transcription examples (choose one based on your API key)
        print("\n--- Speech-to-Text Conversion ---")
        
        # Option 1: Google Cloud Speech-to-Text (requires credentials)
        # transcriber = SpeechToTextConverter(backend="google")
        # text = transcriber.transcribe(output_filename)
        # print(f"Google Transcription:\n{text}\n")
        
        # Option 2: OpenAI Whisper (requires API key)
        # transcriber = SpeechToTextConverter(backend="openai")
        # text = transcriber.transcribe(output_filename)
        # print(f"OpenAI Transcription:\n{text}\n")
        
        # Option 3: Vosk offline (no API key needed)
        transcriber = SpeechToTextConverter(backend="vosk")
        text = transcriber.transcribe(audio_data)
        print(f"Vosk Transcription:\n{text}\n")


if __name__ == "__main__":
    main()
