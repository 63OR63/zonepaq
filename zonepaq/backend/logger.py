import json
import logging
import sys
import tkinter as tk
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import messagebox

log_level = logging.DEBUG
# log_level = logging.INFO


class DeepDebug:
    DEEP_DEBUG_LEVEL = 9
    logging.addLevelName(DEEP_DEBUG_LEVEL, "DEEP_DEBUG")

    @staticmethod
    def add_method():
        def deep_debug(self, message, *args, **kwargs):
            if self.isEnabledFor(DeepDebug.DEEP_DEBUG_LEVEL):
                self._log(DeepDebug.DEEP_DEBUG_LEVEL, message, args, **kwargs)

        setattr(logging.Logger, "deep_debug", deep_debug)


class LogConfig:
    class SafeFormatter(logging.Formatter):
        _format = "%(asctime)s - %(name)s - %(levelname)s - %(caller_file)s:%(caller_line)d - %(caller_func)s() - %(message)s"
        _format = "%(asctime)s - %(name)s - %(levelname)s - %(caller_file)s:%(caller_line)d - %(message)s"

        def __init__(self):
            super().__init__(self._format)

        def format(self, record):
            if not hasattr(record, "caller_file"):
                record.caller_file = record.filename
            if not hasattr(record, "caller_line"):
                record.caller_line = record.lineno
            if not hasattr(record, "caller_func"):
                record.caller_func = record.funcName
            return super().format(record)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            # Adding additional attributes if not already present
            if not hasattr(record, "caller_file"):
                record.caller_file = record.filename
            if not hasattr(record, "caller_line"):
                record.caller_line = record.lineno
            if not hasattr(record, "caller_func"):
                record.caller_func = record.funcName

            # Creating a structured JSON log
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
                "logger": record.name,
                "level": record.levelname,
                "filename": record.caller_file,
                "lineno": record.caller_line,
                # "funcName": record.caller_func,
                "message": record.getMessage(),
            }

            return json.dumps(log_record, ensure_ascii=False)

    @staticmethod
    def setup_logging(
        log_file="zonepaq/logs/zonepaq.log",
        max_file_size=0.5 * 1024 * 1024,
        backup_count=3,
        log_level=log_level,
    ):
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        formatter = LogConfig.SafeFormatter()
        # formatter = LogConfig.JsonFormatter()

        # File Handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        # Console Handler (Single Handler for All Console Logs)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)  # Set the log level here
        console_handler.setFormatter(formatter)

        # Root Logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear any existing handlers to avoid duplicates
        root_logger.handlers.clear()

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)


class log:
    @staticmethod
    def _get_caller_info():
        """Retrieve caller's relative file path, line number, and function name."""
        try:
            frame = sys._getframe(3)  # Get the caller's frame
            full_path = frame.f_code.co_filename
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name  # Retrieve the function name

            # Handle PyInstaller runtime
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                return full_path, lineno, func_name

            if not full_path or full_path.startswith("<"):
                return "unknown_file", lineno, func_name

            try:
                relative_path = str(Path(full_path).relative_to(Path.cwd()))
                return relative_path, lineno, func_name
            except ValueError:
                return str(full_path), lineno, func_name

        except (ValueError, KeyError, RuntimeError):
            return "Unknown", 0, "Unknown"

    @staticmethod
    def _log_with_caller(level, text, exc_info=None):
        logger = logging.getLogger()
        filename, lineno, func_name = log._get_caller_info()
        extra = {
            "caller_file": filename or "Unknown",
            "caller_line": lineno or 0,
            "caller_func": func_name or "Unknown",
        }
        logger._log(level, text, (), exc_info=exc_info, extra=extra)

    @staticmethod
    def debug(text):
        log._log_with_caller(logging.DEBUG, text)

    @staticmethod
    def info(text):
        log._log_with_caller(logging.INFO, text)

    @staticmethod
    def warning(text):
        log._log_with_caller(logging.WARNING, text)

    @staticmethod
    def error(text):
        log._log_with_caller(logging.ERROR, text)

    @staticmethod
    def critical(text):
        log._log_with_caller(logging.CRITICAL, text)

    @staticmethod
    def exception(text):
        log._log_with_caller(logging.ERROR, text, exc_info=True)


def handle_exception(exc_type, exc_value, exc_traceback):

    log.exception("An unhandled exception occurred:")

    error_message = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Application Error", f"An unexpected error occurred:\n\n{error_message}"
    )
    root.destroy()

    sys.exit(0)


sys.excepthook = handle_exception

DeepDebug.add_method()
LogConfig.setup_logging()
