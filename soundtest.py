from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter
from datetime import datetime

# Initialize recorder
recorder = I2SMicrophoneRecorder(sample_rate=16000)

# Record audio
filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
audio_data, sr = recorder.record(duration_seconds=10.0, output_file=filename)
recorder.close()

# Transcribe
transcriber = SpeechToTextConverter(backend="google")
result = transcriber.transcribe(filename)
print(f"Result: {result}")