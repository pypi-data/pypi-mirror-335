import logging.config
import logging.handlers

from pathlib import Path
from typing import cast

from hylog import config
from hylog import handlers
from hylog import logger


Config = config.Config()

# Set the default logger class to the custom class and create the default logger.
logging.setLoggerClass(logger._AppLogger)
logging.getLogger(Config.app.name).setLevel(logging.DEBUG)


def get_app_logger(
    name: str | None = None,
    output_dir: str | Path | None = None,
    file_name: str | None = None,
    stdout_level: str | None = None,
) -> logger._AppLogger:
    """Create a logger for the application with the given name and output directory."""
    # TODO: Add support for showing path to module rather than just the name?
    
    if output_dir is None and file_name is not None:
        raise ValueError("If file_name is provided, output_dir must also be provided.")

    name = name or Config.app.name

    if Config.app.initialized and name in Config.app.seen_names:
        return cast(logger._AppLogger, logging.getLogger(name))

    # TODO: Move seem_names out of config module.
    Config.app.seen_names.add(name)

    # Configure all handlers and logging levels into a QueueHandler
    handlers.setup_handlers(
        name=name,
        output_dir=output_dir,
        file_name=file_name,
        stdout_level=stdout_level,
    )

    # Set flag to configured so we don't reconfigure the logger
    Config.app.initialized = True

    return cast(logger._AppLogger, logging.getLogger(name))


def get_logger(
    name: str | None = None,
) -> logger._AppLogger:
    """Create a logger for the application with the given name and output directory."""
    if name is None:
        return cast(logger._AppLogger, logging.getLogger(Config.app.name))
    return cast(logger._AppLogger, logging.getLogger(Config.app.name).getChild(name))
