from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter

recorder = I2SMicrophoneRecorder(sample_rate=48000)
transcriber = SpeechToTextConverter(backend="vosk")

#testing ordering boba by recognizing key phrases in speech
flavor = None
boba_amount = None
while flavor is None:
    print("Welcome! What flavor of boba would you like?")
    print("Please speak clearly into the microphone.")
    print("You have 5 seconds to say your order.")
    audio_data, sample_rate = recorder.record(duration_seconds=5)
    transcribed_text = transcriber.transcribe(audio_data, sample_rate)
    print(f"Transcribed text: {transcribed_text}")

    # Check for key phrases related to boba flavors
    if "taro" in transcribed_text.lower():
        flavor = "taro"
        print("You ordered taro tea.")
    elif "matcha" in transcribed_text.lower():
        flavor = "matcha"
        print("You ordered matcha tea.")
    elif "milk" in transcribed_text.lower():
        flavor = "milk"
        print("You ordered milk tea.")
    else:
        flavor = None
        print("Could not recognize a specific boba flavor in your order. Please try again and make sure to mention the flavor clearly.")
        print("Let's try again.")
while boba_amount is None:
    print("How much boba would you like?")
    print("Please speak clearly into the microphone.")
    print("You have 5 seconds to say your order.")
    audio_data, sample_rate = recorder.record(duration_seconds=5)
    transcribed_text = transcriber.transcribe(audio_data, sample_rate)
    print(f"Transcribed text: {transcribed_text}")
    none_phrases = ["none", "no", "zero"]
    lesser_phrases = ["tiny", "few", "little", "less", "mini", "smallest"]
    regular_phrases = ["regular", "normal", "standard"]
    more_phrases = ["extra", "more", "large", "big", "largest", "max", "maximum", "double"]
    # Check for key phrases related to boba amount
    if any(phrase in transcribed_text.lower() for phrase in none_phrases):
        boba_amount = "none"
        print("You ordered no boba.")
    elif any(phrase in transcribed_text.lower() for phrase in lesser_phrases):
        boba_amount = "small"
        print("You ordered a small amount of boba.")
    elif any(phrase in transcribed_text.lower() for phrase in regular_phrases):
        boba_amount = "medium"
        print("You ordered a medium amount of boba.")
    elif any(phrase in transcribed_text.lower() for phrase in more_phrases):
        boba_amount = "large"
        print("You ordered a large amount of boba.")
    else:
        boba_amount = None
        print("Could not recognize a specific boba amount in your order. Please try again and make sure to mention the amount clearly.")
        print("Let's try again.")
print(f"You have chosen {flavor} boba with {boba_amount} amount of boba.")
print("Thank you for your order!")
print("Please wait while we make your boba tea.")



