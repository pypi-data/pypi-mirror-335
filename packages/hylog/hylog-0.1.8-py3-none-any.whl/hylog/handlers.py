import atexit
import logging.handlers
import sys

from multiprocessing import Queue
from pathlib import Path

from hylog import config
from hylog import formatters


Config = config.Config()


def _format_output_dir_path(*args, **kwargs) -> Path:
    """Retrieve and validate that the user passed a name and output directory.

    Returns the path to the output file.
    """
    output_dir = kwargs.get("output_dir")

    if output_dir is None:
        raise ValueError(f"output_dir and name must be provided. Got {output_dir=}")

    if not Path(output_dir).is_dir():
        raise FileNotFoundError(f"Output directory {output_dir} does not exist.")

    return Path(output_dir)


def _create_file_path(output_dir: Path, file_name: str | None, default: str) -> Path:
    """Create a file path from the output directory and file name."""
    # TODO: Merge this function with _format_output_dir_path?

    file_name = default if file_name is None else f"{file_name}_{default}"

    return output_dir / file_name


class LogHandler:
    """Base class for all log handlers."""


class FileLastRun(LogHandler, logging.FileHandler):
    _formatter: logging.Formatter = formatters.Detailed()
    _mode: str = "w"

    def __init__(self, *args, **kwargs) -> None:
        """
        Logs the last run of the application to a file.

        The file is overwritten each time the application is run.
        """
        file_path = _create_file_path(
            _format_output_dir_path(*args, **kwargs),
            kwargs.get("file_name"),
            Config.file.last_file_name,
        )

        super().__init__(file_path, mode=self._mode)

        self.setLevel(Config.file.level)
        self.setFormatter(self._formatter)


class FileRotating(LogHandler, logging.handlers.RotatingFileHandler):
    _formatter: logging.Formatter = formatters.Detailed()

    def __init__(self, *args, **kwargs) -> None:
        file_path = _create_file_path(
            _format_output_dir_path(*args, **kwargs),
            kwargs.get("file_name"),
            Config.file.rotating_file_name,
        )

        super().__init__(
            file_path,
            maxBytes=Config.file.max_bytes,
            backupCount=Config.file.backup_count,
        )

        self.setLevel(Config.file.level)
        self.setFormatter(self._formatter)


class JSONHandler(LogHandler, logging.handlers.RotatingFileHandler):
    _formatter: logging.Formatter = formatters.JSON()

    def __init__(self, *args, **kwargs) -> None:
        file_path = _create_file_path(
            _format_output_dir_path(*args, **kwargs),
            kwargs.get("file_name"),
            Config.file.json_file_name,
        )

        super().__init__(
            file_path,
            maxBytes=Config.file.max_bytes,
            backupCount=Config.file.backup_count,
        )

        self.setLevel(Config.file.level)
        self.setFormatter(self._formatter)


# Stream handlers
class StandardOutput(LogHandler, logging.StreamHandler):
    _formatter: logging.Formatter = formatters.Simple()

    def __init__(self, *args, **kwargs) -> None:
        if sys.platform == "darwin":
            StandardOutput._formatter = formatters.SimpleColor()
            
        super().__init__(stream=sys.stdout)
        user_level = kwargs.get("stdout_level")
        if user_level is not None:
            _stdout_level = getattr(logging, user_level.upper())
        else:
            _stdout_level = Config.stream.level

        self.setLevel(_stdout_level)
        self.setFormatter(self._formatter)


# Queue handlers
class QueueHandler(LogHandler, logging.handlers.QueueHandler):
    def __init__(self, queue: Queue) -> None:
        super().__init__(queue)


class QueueListener(LogHandler, logging.handlers.QueueListener):
    def __init__(self, queue, *handlers: logging.Handler) -> None:
        super().__init__(queue, *handlers, respect_handler_level=True)


def setup_handlers(*args, **kwargs) -> None:
    """Instantiae and add all handlers to the QueueListener/Handler and configure logger."""
    # TODO: Add support to disable file logging
    if kwargs.get("name") is None:
        raise ValueError("Logger name must be provided.")

    logger = logging.getLogger(kwargs["name"])

    # Set the logger level to the highest level of all handlers
    logger.setLevel(logging.DEBUG)

    log_queue = Queue(-1)
    queue_handler = QueueHandler(log_queue)

    logger.addHandler(queue_handler)

    # Create a list of handlers to add to the QueueListener
    handlers: list[logging.Handler] = [
        StandardOutput(*args, **kwargs),
    ]

    # Add file handlers if the user specified an output directory
    if kwargs.get("output_dir") is not None:
        handlers.extend(
            [
                FileLastRun(*args, **kwargs),
                FileRotating(*args, **kwargs),
                JSONHandler(*args, **kwargs),
            ]
        )

    # Create a QueueListener to listen to the queue and pass messages to the handlers
    queue_listener = QueueListener(
        log_queue,
        *handlers,
    )

    queue_listener.start()
    atexit.register(queue_listener.stop)
