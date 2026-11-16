import unittest
from unittest.mock import patch

import numpy as np

from components.microphone import MicrophoneRecorder


class MicrophoneRecorderTests(unittest.TestCase):
    @patch("components.microphone.sd.wait")
    @patch("components.microphone.sd.rec")
    def test_record_returns_mono_samples(self, record, wait) -> None:
        record.return_value = np.array([[10], [-10], [5]], dtype=np.int16)
        microphone = MicrophoneRecorder(sample_rate=10)

        audio = microphone.record(0.3)

        np.testing.assert_array_equal(audio, np.array([10, -10, 5], dtype=np.int16))
        record.assert_called_once_with(
            3,
            samplerate=10,
            channels=1,
            dtype="int16",
            device=None,
        )
        wait.assert_called_once_with()

    def test_record_rejects_nonpositive_duration(self) -> None:
        microphone = MicrophoneRecorder()

        with self.assertRaises(ValueError):
            microphone.record(0)
