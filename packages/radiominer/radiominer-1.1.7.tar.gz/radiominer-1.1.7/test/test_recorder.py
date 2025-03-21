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

    def timeout_side_effect(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ffmpeg", timeout=kwargs.get("timeout", 1))

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
            stderr=subprocess.DEVNULL,
            timeout=121
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
        mock_subprocess_run.assert_called_with(
            mock_subprocess_run.call_args[0][0],
             stdout=None,
            stderr=None,
            timeout=121
        )

    @patch('radiominer.main.subprocess.run')
    @patch('radiominer.main.os.rename')
    def test_record_stream_multiple_iterations(self, mock_rename, mock_subprocess_run):
        """Testet, ob der Recorder in einer Schleife korrekt mehrere Iterationen durchläuft, sofern run_once False ist."""
        recorder = RadioRecorder(self.stream_url, self.sender, self.segment_time, self.base_dir, verbose=False, run_once=False)
        # Simuliere, dass nach 3 Iterationen recorder.running auf False gesetzt wird.
        call_count = 0

        def stop_after_n_iterations(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                recorder.running = False
                return MagicMock(returncode=0)

        mock_subprocess_run.side_effect = stop_after_n_iterations
        recorder.running = True
        # Da record_stream() eine Dauerschleife beinhaltet, sollte es erst nach dem Stoppen verlassen.
        recorder.record_stream()

        self.assertEqual(call_count, 3, "Recorder sollte genau 3 Iterationen ausgeführt haben.")
        self.assertFalse(recorder.running, "Recorder sollte nach den Iterationen gestoppt sein.")

    @patch('radiominer.main.subprocess.run', side_effect=timeout_side_effect)
    def test_record_segment_timeout(self, mock_run):
        # Instantiate RadioRecorder with run_once=True to trigger return on TimeoutExpired
        recorder = RadioRecorder(
            self.stream_url,
            self.sender,
            segment_time=self.segment_time,
            base_dir=self.base_dir,
            verbose=False,
            run_once=True
        )

        # Patch the logger.error method of the recorder instance to monitor calls.
        with patch.object(recorder.logger, 'error') as mock_logger_error:
            result = recorder._record_segment()
            self.assertIsNone(result)
            mock_logger_error.assert_called()
            args, _ = mock_logger_error.call_args
            temp_output_file = args[2]
            # Expect timeout_sec to be computed as int(segment_time + segment_time*5/100) = int(1 + 0.05) = 1
            mock_logger_error.assert_called_with("FFmpeg-Aufruf überschritt Timeout von %s Sekunden für Segment: %s.", 121, temp_output_file)

if __name__ == '__main__':
    unittest.main()
