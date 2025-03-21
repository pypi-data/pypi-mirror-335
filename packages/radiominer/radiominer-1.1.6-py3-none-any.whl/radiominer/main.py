import subprocess
import whisper
import os
import time
import threading
import logging
import queue
import contextlib
from datetime import datetime
from enum import Enum
import colorama
import shutil
from .version import __version__
colorama.init()

class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        'DEBUG': "\033[94m",   # Blau
        'INFO': "\033[92m",    # Grün
        'WARNING': "\033[93m", # Gelb
        'ERROR': "\033[91m",   # Rot
        'CRITICAL': "\033[95m" # Magenta
    }
    RESET_CODE = "\033[0m"
    
    def format(self, record):
        message = super().format(record)
        color = self.COLOR_CODES.get(record.levelname, self.RESET_CODE)
        return f"{color}{message}{self.RESET_CODE}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperModel(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    TURBO = "turbo"

class RadioRecorder:
    five_percent = 5

    def __init__(self, stream_url, sender, segment_time=60, base_dir=None, poll_interval=5, whisper_model=WhisperModel.TURBO, quality="64k", record_only=False, transcribe_only=False, verbose=False, ffmpeg_path=None, run_once=False):    
        if base_dir is None:
            base_dir = os.getcwd()
        
        sender_dir = os.path.join(base_dir, sender)
        self.audio_dir = os.path.join(sender_dir, "audio")
        self.transcription_dir = os.path.join(sender_dir, "transkriptionen")
        
        self.stream_url = stream_url
        self.sender = sender
        self.segment_time = segment_time
        self.poll_interval = poll_interval
        self.whisper_model = whisper_model
        self.quality = quality
        self.record_only = record_only
        self.transcribe_only = transcribe_only
        self.verbose = verbose
        self.running = True
        self.segment_queue = queue.Queue()
        self.queued_files = set()  # Track queued or processed files
        self.ffmpeg_path = ffmpeg_path or shutil.which("ffmpeg")
        self.run_once = run_once

        if not self.ffmpeg_path:
            self.ffmpeg_path = "ffmpeg"

        if self.record_only and self.transcribe_only:
            raise ValueError("Fehler: record-only und transcribe-only können nicht gleichzeitig True sein.")

        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.transcription_dir, exist_ok=True)

        self.logger = logging.getLogger(f"RadioRecorder:{self.sender}")
        handler = logging.StreamHandler()
        formatter_str = '%(asctime)s - %(levelname)s - %(message)s' if self.verbose else '%(message)s'
        formatter = ColoredFormatter(formatter_str)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False  # Verhindert, dass der Logger Nachrichten an den Root-Logger sendet
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        
        self.logger.debug(f"RadioRecorder für {self.sender} gestartet. Logging-Level: {self.logger.level}")


    def record_stream(self):
        while self.running:
            if not self.transcribe_only:
                final_output_file = self._record_segment()
                if not final_output_file:
                    continue
            
            if self.record_only:
                continue

            if self.transcribe_only:
                end_time = datetime.now()
                self.check_and_queue_old_files(end_time)
                break

            self._queue_segment_for_transcription(final_output_file)
            
            time.sleep(1)
            end_time = datetime.now()
            self.check_and_queue_old_files(end_time)

    def _get_timeout(self, margin_percent=5, reconnect_delay_max=15, max_retries=8):
        """
        Berechnet einen Timeout-Wert auf Basis von segment_time,
        z.B. +5% Sicherheitsaufschlag.
        """
        return int((self.segment_time + reconnect_delay_max * max_retries) + (self.segment_time * margin_percent / 100))

    def _record_segment(self, reconnect=1, reconnect_on_network_error=1, reconnect_on_http_error=1, reconnect_streamed=1, reconnect_delay_max=15):
        max_retries = 8
        for attempt in range(max_retries):
            try:
                final_output_file = self._attempt_record_segment(reconnect, reconnect_on_network_error, reconnect_on_http_error, reconnect_streamed, reconnect_delay_max, attempt, max_retries)
                if final_output_file:
                    return final_output_file
            except subprocess.TimeoutExpired as e:
                timeout_sec = self._get_timeout(5, reconnect_delay_max, max_retries)
                temp_output_file = os.path.join(self.audio_dir, f"{self.sender}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
                self.logger.error("FFmpeg-Aufruf überschritt Timeout von %s Sekunden für Segment: %s.", timeout_sec, temp_output_file)
                if self.run_once:
                    return None
            except Exception as e:
                self.logger.error(f"Fehler in _record_segment: {e}", exc_info=True)
                if self.run_once:
                    return None

        self.logger.error("Maximale Anzahl von Versuchen erreicht, Segment konnte nicht aufgenommen werden.")
        return None

    def _attempt_record_segment(self, reconnect, reconnect_on_network_error, reconnect_on_http_error, reconnect_streamed, reconnect_delay_max, attempt, max_retries):
        start_time = datetime.now()
        start_timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        temp_output_file = os.path.join(self.audio_dir, f"{self.sender}_{start_timestamp}.mp3")

        timeout_sec = self._get_timeout(RadioRecorder.five_percent, reconnect_delay_max, max_retries)
        command = [
            self.ffmpeg_path, '-y',
            '-reconnect', str(reconnect),                                       # Aktiviert automatisches Wiederverbinden
            '-reconnect_on_network_error', str(reconnect_on_network_error),     # Versucht, bei Netzwerkfehlern erneut zu verbinden
            '-reconnect_on_http_error', str(reconnect_on_http_error),           # Reconnect bei HTTP-Fehlern (z.B. 4xx oder 5xx)
            '-reconnect_streamed', str(reconnect_streamed),                     # Erzwingt Wiederverbindung bei bereits gestreamten Inhalten
            '-reconnect_delay_max', str(reconnect_delay_max),                   # Legt fest, wie lange (in Sekunden) maximal zwischen den Verbindungsversuchen gewartet wird
            '-i', self.stream_url,
            '-t', str(self.segment_time),
            '-c:a', 'libmp3lame',
            '-b:a', self.quality,
            temp_output_file
        ]
        self.logger.info("Starte Aufnahme für Segment: %s (Versuch %d/%d)", temp_output_file, attempt+1, max_retries)
        
        # Timeout für FFmpeg-Prozess
        result = subprocess.run(
            command,
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL,
            timeout=timeout_sec
        )

        return self._finalize_segment(result, temp_output_file, start_timestamp)

    def _finalize_segment(self, result, temp_output_file, start_timestamp):
        if result.returncode == 0:
            end_time = datetime.now()
            end_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
            final_output_file = os.path.join(self.audio_dir, f"{self.sender}_{start_timestamp}_{end_timestamp}.mp3")
            os.rename(temp_output_file, final_output_file)
            return final_output_file
        else:
            self.logger.warning("ffmpeg fehlgeschlagen für Segment: %s, versuche erneut...", temp_output_file)
            return None

    def _queue_segment_for_transcription(self, final_output_file):
        if final_output_file and final_output_file not in self.queued_files:
            self.segment_queue.put(final_output_file)
            self.queued_files.add(final_output_file)
            self.logger.info("Segment fertiggestellt und zur Transkription bereit: %s", final_output_file)
        else:
            self.logger.info("Segment bereits in der Warteschlange: %s", final_output_file)

    def check_and_queue_old_files(self, reference_time):
        for file in os.listdir(self.audio_dir):
            if file.endswith(".mp3"):
                audio_file = os.path.join(self.audio_dir, file)
                if os.path.getsize(audio_file) == 0:
                    self.logger.info("Leere Datei gefunden und gelöscht: %s", audio_file)
                    os.remove(audio_file)
                    continue
                
                mod_time = datetime.fromtimestamp(os.path.getmtime(audio_file))
                transcription_file = os.path.join(self.transcription_dir, file.replace(".mp3", ".txt"))
                if mod_time < reference_time and not os.path.exists(transcription_file):
                    if audio_file not in self.queued_files:
                        self.logger.info("Requeue alte Datei: %s", audio_file)
                        self.segment_queue.put(audio_file)
                        self.queued_files.add(audio_file)

    def transcribe_audio(self, audio_file):
        self.logger.debug("Lade Whisper Modell: %s", self.whisper_model)
        model_name = self.whisper_model.value
        if self.verbose:
            model = whisper.load_model(model_name)
            self.logger.info("Starte Transkription: %s", audio_file)
            result = model.transcribe(audio_file)
        else:
            with open(os.devnull, 'w') as fnull, contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                model = whisper.load_model(model_name)
                result = model.transcribe(audio_file)
        
        segments = result.get("segments", [])
        transcription = "\n".join(segment["text"].strip() for segment in segments)
        
        return transcription

    def transcription_worker(self, run_once=False):
        while self.running or run_once:
            try:
                audio_file = self.segment_queue.get(timeout=self.poll_interval)
                self.logger.info("Empfange Nachricht zur Transkription: %s", audio_file)
                transcription = self.transcribe_audio(audio_file)
                base_name = os.path.basename(audio_file).replace(".mp3", ".txt")
                transcription_file = os.path.join(self.transcription_dir, base_name)
                with open(transcription_file, "w", encoding="utf-8") as f:
                    f.write(transcription)
                self.logger.info("Transkription abgeschlossen: %s", transcription_file)
                self.segment_queue.task_done()
                self.queued_files.remove(audio_file)  # Remove from set when done
            except queue.Empty:
                if run_once or self.transcribe_only:
                    break
                continue
            if run_once:
                break

    def run(self):
        art = f"""
                    _____           _ _                 _                 
                    |  __ \         | (_)               (_)                
                    | |__) |__ _  __| |_  ___  _ __ ___  _ _ __   ___ _ __ 
                    |  _  // _` |/ _` | |/ _ \| '_ ` _ \| | '_ \ / _ \ '__|
                    | | \ \ (_| | (_| | | (_) | | | | | | | | | |  __/ |   
                    |_|  \_\__,_|\__,_|_|\___/|_| |_| |_|_|_| |_|\___|_|      Version: {__version__} 
        """

        print(art)

        if self.record_only:
            self.logger.info("Starte Thread für Aufzeichnungen...")
        
        self.record_thread = threading.Thread(target=self.record_stream, daemon=True)
        self.record_thread.start()

        if self.transcribe_only:
            self.logger.info("Starte Thread für Transkriptionen...")
        
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcription_thread.start()
        
        self.logger.info("RadioRecorder läuft.")
        try:
            while self.running:
                time.sleep(1)
                if not self.record_thread.is_alive() and not self.transcription_thread.is_alive():
                    self.logger.info("Verarbeitung beendet.")
                    self.running = False
        except KeyboardInterrupt:
            self.logger.info("Interrupt erhalten, beende Anwendung...")
            self.stop()

    def stop(self):
        self.running = False
        self.logger.info("Beende Threads, warte auf deren Abschluss...")
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join()
        if hasattr(self, 'transcription_thread') and self.transcription_thread.is_alive():
            self.transcription_thread.join()
        self.logger.info("Anwendung beendet.")