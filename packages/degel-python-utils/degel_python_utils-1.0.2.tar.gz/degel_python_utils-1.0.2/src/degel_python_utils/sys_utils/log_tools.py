"""Custom log formatting."""

import contextvars
import logging
import time
from typing import Any, Literal, Self, Union, cast

from blessings import Terminal

log_prefix: contextvars.ContextVar[str] = contextvars.ContextVar(
    "log_prefix", default=""
)


class DegelLogger(logging.Logger):
    """Add some extra logging levels."""

    DEBUG = logging.DEBUG
    MINOR = logging.INFO - 5
    INFO = logging.INFO
    MAJOR = logging.WARNING - 5
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    logging.addLevelName(MINOR, "MINOR")
    logging.addLevelName(MAJOR, "MAJOR")

    def minor(self: Self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log level MINOR."""
        if self.isEnabledFor(self.MINOR):
            self._log(self.MINOR, message, args, **kwargs)

    def major(self: Self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log level MAJOR."""
        if self.isEnabledFor(self.MAJOR):
            self._log(self.MAJOR, message, args, **kwargs)


logging.setLoggerClass(DegelLogger)


class DegelLogFormatter(logging.Formatter):
    """Apply colors to the different logging levels."""

    def __init__(
        self: Self,
        fmt: str = "%(asctime)s - %(levelname)s - %(message)s",
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_color: bool = True,
    ) -> None:
        """Initialize the logger."""
        super().__init__(fmt, datefmt, style)
        self.use_color = use_color
        self.t = Terminal() if use_color else None

    def format(self: Self, record: logging.LogRecord) -> str:
        """Format a log line."""
        ct = self.converter(record.created)
        prefix = log_prefix.get()
        record.msg = f"{prefix}{record.msg}"
        record.asctime = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S', ct)},{int(record.msecs):03}"
        )
        color = ""
        level = ""
        if self.use_color and self.t is not None:
            color = self.get_color(record.levelno)
            level = f"{record.levelname+':':<10}"
            record.levelname = f"{color}{level}{self.t.normal}"
            record.msg = f"{color}{record.msg}{self.t.normal}"

        formatted_msg = super().format(record)
        if "\n" in record.msg:
            lines = formatted_msg.split("\n")
            space_prefix_length = len(record.asctime) + len(level) + 5
            space_prefix = " " * space_prefix_length
            if self.use_color and self.t is not None:
                colored_lines = [lines[0]] + [
                    f"{color}{space_prefix}{line}{self.t.normal}" for line in lines[1:]
                ]
                return "\n".join(colored_lines)
            return formatted_msg
        return formatted_msg

    def get_color(self: Self, levelno: int) -> str:
        """Map log levels to colors."""
        if not self.t:
            return ""
        return {
            DegelLogger.DEBUG: self.t.red + self.t.bold,
            DegelLogger.MINOR: self.t.yellow,
            DegelLogger.INFO: self.t.blue,
            DegelLogger.MAJOR: self.t.magenta,
            DegelLogger.WARNING: self.t.yellow,
            DegelLogger.ERROR: self.t.red,
            DegelLogger.CRITICAL: self.t.red,
        }.get(levelno, self.t.normal)

    def formatException(self: Self, ei: Union[Exception, tuple]) -> str:
        """Highlight exception lines."""
        if self.use_color and self.t is not None:
            return self.t.red + super().formatException(cast(tuple, ei)) + self.t.normal
        return super().formatException(cast(tuple, ei))


class DegelLogHandler(logging.StreamHandler):
    """Auto-exit the app if it hits a critical error."""

    def emit(self: Self, record: logging.LogRecord) -> None:
        """Exit application if writing a CRITICAL log line."""
        if record.levelno >= logging.CRITICAL:
            raise RuntimeError("Exit forced by Degel logging handler")
        super().emit(record)


def setup_logger(name: str, level: int = logging.DEBUG) -> DegelLogger:
    """Set up and return a logger with the specified name."""
    logger = cast(DegelLogger, logging.getLogger(name))
    logger.setLevel(level)
    handler = DegelLogHandler()
    handler.setFormatter(DegelLogFormatter())
    logger.addHandler(handler)
    return logger
