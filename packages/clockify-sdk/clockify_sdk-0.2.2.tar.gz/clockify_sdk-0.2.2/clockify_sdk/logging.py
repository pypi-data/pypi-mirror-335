"""
Logging configuration for the Clockify SDK
"""

import logging
import os


class ClockifyLogger:
    """Logger configuration for the Clockify SDK"""

    def __init__(self, name: str = "clockify_sdk"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(console_handler)

        # Set debug level if environment variable is set
        if os.getenv("CLOCKIFY_DEBUG"):
            self.set_debug_level()

    def set_debug_level(self) -> None:
        """Set logging level to DEBUG"""
        self.logger.setLevel(logging.DEBUG)
        for handler in self.logger.handlers:
            handler.setLevel(logging.DEBUG)

    def set_file_handler(self, filepath: str) -> None:
        """Add file handler for logging to file"""
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log critical message"""
        self.logger.critical(message)


# Create default logger instance
logger = ClockifyLogger()
