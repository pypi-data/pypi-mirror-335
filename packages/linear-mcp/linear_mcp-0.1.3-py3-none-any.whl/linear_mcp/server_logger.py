import os
import sys
import traceback
from typing import Optional, TextIO
from datetime import datetime

class SafeFileLogger:
    """
    A logger that writes directly to a file without using Python's logging system
    This is important because the `logging` module tends to interfere with stdio transport
    """
    
    def __init__(self):
        self._file: Optional[TextIO] = None
        self._log_level = "INFO"
        self._levels = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }

    def _should_log(self, level: str) -> bool:
        return self._levels.get(level, 0) >= self._levels.get(self._log_level, 0)

    def _write(self, level: str, msg: str, exc_info: bool = False) -> None:
        if not self._file or not self._should_log(level):
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"{timestamp} - {level:8} - {msg}\n"
        
        try:
            self._file.write(log_line)
            if exc_info:
                self._file.write(traceback.format_exc())
            self._file.flush()  # Ensure it's written immediately
        except Exception:
            # If we can't write to the file, write to stderr as last resort
            sys.stderr.write(f"Failed to write to log file: {msg}\n")

    def configure(self, level: str = "INFO", log_file: Optional[str] = None) -> None:
        """Configure the logger with a level and file"""
        self._log_level = level.upper()
        
        # Close existing file if open
        if self._file:
            try:
                self._file.close()
            except Exception:
                pass
            self._file = None
            
        if log_file:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
                self._file = open(log_file, 'a', encoding='utf-8')
                self._write("INFO", f"Log file opened, level: {self._log_level}")
            except Exception as e:
                sys.stderr.write(f"Failed to open log file {log_file}: {str(e)}\n")

    def debug(self, msg: str) -> None:
        self._write("DEBUG", msg)

    def info(self, msg: str) -> None:
        self._write("INFO", msg)

    def warning(self, msg: str) -> None:
        self._write("WARNING", msg)

    def error(self, msg: str, exc_info: bool = False) -> None:
        self._write("ERROR", msg, exc_info)

    def critical(self, msg: str, exc_info: bool = False) -> None:
        self._write("CRITICAL", msg, exc_info)

    def exception(self, msg: str) -> None:
        self._write("ERROR", msg, exc_info=True)

# Create a single logger instance
logger = SafeFileLogger()

def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure the safe file logger"""
    logger.configure(level, log_file)
