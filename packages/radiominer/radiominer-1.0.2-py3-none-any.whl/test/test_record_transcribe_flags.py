import unittest
from radiominer.main import RadioRecorder

class TestRecordTranscribeFlags(unittest.TestCase):
    def test_both_flags_true_raises_error(self):
        with self.assertRaises(ValueError):
            RadioRecorder(
                stream_url="http://example.com",
                sender="FlagTest",
                record_only=True,
                transcribe_only=True
            )

if __name__ == "__main__":
    unittest.main()