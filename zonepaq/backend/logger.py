import logging
import sys
import tkinter as tk
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import messagebox


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
    @staticmethod
    def setup_logging(
        log_file="logs/zonepaq.log",
        max_file_size=0.1 * 1024 * 1024,
        backup_count=3,
        log_level=logging.DEBUG,
    ):
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

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
    def deep_debug(text):
        logging.getLogger().deep_debug(text)

    @staticmethod
    def debug(text):
        logging.debug(text)

    @staticmethod
    def info(text):
        logging.info(text)

    @staticmethod
    def warning(text):
        logging.warning(text)

    @staticmethod
    def error(text):
        logging.error(text)

    @staticmethod
    def critical(text):
        logging.critical(text)

    @staticmethod
    def exception(text):
        logging.exception(text)

    @staticmethod
    def fatal(text):
        logging.fatal(text)


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

    sys.exit(0)


sys.excepthook = handle_exception

DeepDebug.add_method()
LogConfig.setup_logging()
