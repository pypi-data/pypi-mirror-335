import datetime as dt
import json
import logging

from typing import ClassVar


TERM_COLORS = {
    "default": "\033[0m",
    "black": "\033[30m",
    "gray": "\033[1;30m",
    "light_gray": "\033[37m",
    "white": "\033[1;37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "yellow": "\033[33m",
}

LEVEL_COLORS = {
    "grey": "\x1b[38;20m",
    "green": "\x1b[32;20m",
    "yellow": "\x1b[33;20m",
    "orange": "\x1b[38;5;208m",
    "red": "\x1b[31;20m",
    "bold_red": "\x1b[31;1m",
    "reset": "\x1b[0m",
}

TERM_ATTRS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "reverse": "\033[7m",
    "conceal": "\033[8m",
}

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class Simple(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s - [%(levelname)-8s] %(module)s:%(lineno)03d | %(message)s",
            datefmt="T%H:%M:%S",
        )


class SimpleColor(logging.Formatter):
    _default_color: ClassVar[str] = TERM_COLORS["black"]

    def __init__(self) -> None:
        super().__init__(
            fmt=f"{self._default_color}%(asctime)s - [%(levelname)-8s] %(module)s:%(lineno)03d   %(message)s{TERM_ATTRS['reset']}",
            datefmt="T%H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        color = LEVEL_COLORS["grey"]

        if levelname == "DEBUG":
            color = LEVEL_COLORS["green"]
        elif levelname == "INFO":
            color = LEVEL_COLORS["yellow"]
        elif levelname == "WARNING":
            color = LEVEL_COLORS["orange"]
        elif levelname == "ERROR":
            color = LEVEL_COLORS["red"]
        elif levelname == "CRITICAL":
            color = LEVEL_COLORS["bold_red"]

        levelname_colored = f"{color}{levelname}{self._default_color}"
        # timestamp = dt.datetime.fromtimestamp(record.created).strftime(self.datefmt or "T%H:%M:%S")
        # record.asctime = f"{TERM_COLORS['black']}{timestamp}{TERM_ATTRS['reset']}"
        # record.filename = f"{TERM_COLORS['black']}{record.filename}{TERM_ATTRS['reset']}"
        # record.message = f"{TERM_COLORS['gray']}{record.getMessage()}{TERM_ATTRS['reset']}"

        record.message = record.getMessage()
        record.message = f"{TERM_COLORS['default']}{record.message}{self._default_color}"

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        s = s.replace(levelname, levelname_colored, 1)

        if record.exc_info:  # noqa: SIM102
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s

        # return super().format(record)


class Detailed(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s [%(levelname)-8s]  %(pathname)s:%(lineno)03d %(module)s %(funcName)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )


class JSON(logging.Formatter):
    _fmt_keys: ClassVar[dict[str, str]] = {
        "level": "levelname",
        "message": "message",
        "timestamp": "timestamp",
        "logger": "name",
        "module": "module",
        "function": "funcName",
        "line": "lineno",
        "thread_name": "threadName",
    }

    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else self._fmt_keys

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str]:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }

        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.ERROR
