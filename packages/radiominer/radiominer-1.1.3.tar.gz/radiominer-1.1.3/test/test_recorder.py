import unittest
from unittest.mock import patch, MagicMock
import subprocess
import logging
from datetime import datetime
from radiominer.main import RadioRecorder

class TestRadioRecorder(unittest.TestCase):

    def setUp(self):
        self.stream_url = "http://example.com/stream.mp3"
        self.sender = "TestSender"
        self.segment_time = 1
        self.base_dir = "test_dir"

    @patch('radiominer.main.subprocess.run')
    @patch('radiominer.main.datetime')
    @patch('radiominer.main.os.rename')
    def test_record_stream_verbose_false(self, mock_rename, mock_datetime, mock_subprocess_run):
        recorder = RadioRecorder(self.stream_url, self.sender, self.segment_time, self.base_dir, verbose=False)

        # 🔥 Prüfe den **Instanz-Logger**, nicht den globalen Logger
        self.assertEqual(recorder.logger.level, logging.INFO)

        mock_start_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 10, 0, self.segment_time)
        mock_datetime.now.side_effect = [mock_start_time, mock_end_time] + [mock_end_time] * 10

        def stop_after_one_iteration(*args, **kwargs):
            recorder.running = False
            return MagicMock(returncode=0)

        mock_subprocess_run.side_effect = stop_after_one_iteration

        recorder.running = True
        recorder.record_stream()

        # subprocess.run sollte mit DEVNULL aufgerufen werden, weil verbose=False
        mock_subprocess_run.assert_called_once()
        mock_subprocess_run.assert_called_with(
            mock_subprocess_run.call_args[0][0], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )

    @patch('radiominer.main.subprocess.run')
    @patch('radiominer.main.datetime')
    @patch('radiominer.main.os.rename')
    def test_record_stream_verbose_true(self, mock_rename, mock_datetime, mock_subprocess_run):
        recorder = RadioRecorder(self.stream_url, self.sender, self.segment_time, self.base_dir, verbose=True)

        # 🔥 Prüfe den **Instanz-Logger**, nicht den globalen Logger
        self.assertEqual(recorder.logger.level, logging.DEBUG)

        mock_start_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 10, 0, self.segment_time)
        mock_datetime.now.side_effect = [mock_start_time, mock_end_time] + [mock_end_time] * 10

        def stop_after_one_iteration(*args, **kwargs):
            recorder.running = False
            return MagicMock(returncode=0)

        mock_subprocess_run.side_effect = stop_after_one_iteration

        recorder.running = True
        recorder.record_stream()

        # subprocess.run sollte **NICHT** mit DEVNULL aufgerufen werden, weil verbose=True
        mock_subprocess_run.assert_called_once()
        mock_subprocess_run.assert_called_with(mock_subprocess_run.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
