import os
import logging
import uuid
import time
import traceback
import json
import yaml
from log.log_level import LogLevel

class BaseLog:
    def __init__(self, log_folder, log_file, guid=None):
        os.makedirs(log_folder, exist_ok=True)
        self.log_path = os.path.join(log_folder, log_file)
        self.start_time = None
        self.guid = guid or str(uuid.uuid4())
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s: (P) %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)


    def start(self, message=None, level="info"):
        """Logs a flexible start message."""
        self.start_time = time.time()
        self.line()
        message = message or f"Start: {self.guid}"
        self._log(message, level, prefix="***")

    def finish(self, message=None, level="info", show_duration=True):
        """Logs a flexible finish message with optional duration."""
        end_time = time.time()
        time_spent = end_time - self.start_time if self.start_time else 0
        time_spent_formatted = self._format_duration(time_spent) if show_duration else ""

        final_message = message or f"Finish: {self.guid}"
        if show_duration:
            final_message += f" (duration: {time_spent_formatted})"
        
        self._log(final_message, level, prefix="***")     

    def debug(self, message, level: LogLevel=LogLevel.LEVEL_0):
        message = self._format_log_message(message, level)
        self.logger.debug(message)

    def info(self, message, level: LogLevel=LogLevel.LEVEL_0):
        message = self._format_log_message(message, level)
        self.logger.info(message)

    def warning(self, message, level: LogLevel=LogLevel.LEVEL_0):
        message = self._format_log_message(message, level)
        self.logger.warning(message)

    def error(self, message, level: LogLevel=LogLevel.LEVEL_0, exc_info=None):
        message = self._format_log_message(message, level)
        if exc_info:
            message += f"\nException: {str(exc_info)}\nTraceback:\n{traceback.format_exc()}"
        self.logger.error(message)

    def fatal(self, message, level: LogLevel=LogLevel.LEVEL_0, exc_info=None):
        message = self._format_log_message(message, level)
        if exc_info:
            message += f"\nException: {str(exc_info)}\nTraceback:\n{traceback.format_exc()}"
        self.logger.critical(message)

    def config(self, config_data):
        """Logs configuration data."""
        if isinstance(config_data, str):
            try:
                config_dict = yaml.safe_load(config_data)
            except yaml.YAMLError as e:
                self.logger.error(f"Failed to parse YAML config: {e}")
                return
        elif isinstance(config_data, dict):
            config_dict = config_data
        else:
            self.logger.error("Invalid config data format. Expected YAML string or dictionary.")
            return
        
        formatted_config = json.dumps(config_dict, indent=4)

        self.logger.info(f"Configuration:\n{formatted_config}")

    def line(self):
        self.logger.info("-" * 150)

    def _format_duration(self, seconds):
        """Formats duration in HH:MM:SS format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def _log(self, message, level, prefix=""):
        """Logs the message at the specified log level."""
        formatted_message = f"{prefix} {message} {prefix}".strip()
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(formatted_message)

    def _format_log_message(self, message: str, level: LogLevel=LogLevel.LEVEL_0) -> str:
        """Formats log messages by adding indentation based on level."""
        if not message:
            return ""

        indentation = "\t" * level.value
        formatted_message = f"{indentation}- {message[0].lower() + message[1:]}" if len(message) > 1 else message.lower()

        return formatted_message