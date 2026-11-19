from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter
from datetime import datetime

# Initialize the recorder (auto-detects I2S device)
recorder = I2SMicrophoneRecorder(sample_rate=16000, device=0)
    
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