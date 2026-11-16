import unittest
from unittest.mock import patch

import numpy as np
import speech_recognition as sr

from speech import SpeechToText


class SpeechToTextTests(unittest.TestCase):
    @patch.object(sr.Recognizer, "recognize_google", return_value="matcha")
    def test_transcribe_converts_pcm_clip_and_returns_text(self, recognize) -> None:
        samples = np.array([100, -100, 50], dtype=np.int16)
        speech_to_text = SpeechToText()

        transcript = speech_to_text.transcribe(samples, sample_rate=16000)

        self.assertEqual(transcript, "matcha")
        audio_data = recognize.call_args.args[0]
        self.assertEqual(audio_data.get_raw_data(), samples.tobytes())
        self.assertEqual(audio_data.sample_rate, 16000)
        recognize.assert_called_once_with(audio_data, language="en-US")

    def test_transcribe_rejects_stereo_audio(self) -> None:
        speech_to_text = SpeechToText()
        stereo_samples = np.zeros((4, 2), dtype=np.int16)

        with self.assertRaises(ValueError):
            speech_to_text.transcribe(stereo_samples, sample_rate=16000)
