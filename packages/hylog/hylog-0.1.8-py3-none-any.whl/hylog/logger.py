import functools
import inspect
import logging
import time

from collections.abc import Callable
from typing import Any

from hylog import config


Config = config.Config()


class _AppLogger(logging.Logger):
    """Custom logger class that adds decorator functionality on top of the standard logger."""
    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        super().__init__(name, level)
        
    def func(self, level: str | None = None) -> Callable[..., Any]:
        """A decorator that logs the function inputs and outputs at the given level."""
        _logger = logging.getLogger(Config.app.name)
        # Set the level to the log_level if it exists otherwise use the logger.getLevelName
        # to retrieve the corresponding int value for the log level
        _level = getattr(logging, level.upper()) if level else self.level

        def decorator(_func: Callable[..., Any]) -> Any:
            """Print the function signature and return value"""

            @functools.wraps(_func)
            def wrapper_debug(*args: Any, **kwargs: Any) -> Any:
                # Get the function's signature
                func_path = f"{_func.__module__}.{_func.__qualname__}"
                signature = inspect.signature(_func)
                func_line = inspect.getsourcelines(_func)[1]

                # Change the stacklevel to 2 so the log message has the module and lineno of the function call, not the decorator.
                log = functools.partial(_logger.log, stacklevel=2)

                log(_level, f"Function: {func_path} (line {func_line})")

                # Map the *args and **kwargs to parameter names
                bound_arguments = signature.bind(*args, **kwargs)
                bound_arguments.apply_defaults()

                log(_level, f"{_func.__name__}() arguments:")

                for name, value in bound_arguments.arguments.items():
                    log(_level, f"{name} = {value}")

                args_repr = [f"{a!r}" for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                log(_level, f"Calling: {_func.__name__}({signature})")

                value = _func(*args, **kwargs)
                log(_level, "Returned:")
                log(_level, f"{value!r}")

                return value

            return wrapper_debug

        return decorator

    def perf(self, level: str | None = None) -> Callable[..., Any]:
        """A decorator that logs the time taken by the function to execute at the given level."""
        # Set the level to the log_level if it exists otherwise use the logger.getLevelName
        # to retrieve the corresponding int value for the log level
        _level = getattr(logging, level.upper()) if level else self.level
        logger = logging.getLogger(Config.app.name)


        def decorator(func: Callable[..., Any]) -> Any:
            """Print the function signature and return value"""

            @functools.wraps(func)
            def wrapper_debug(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                value = func(*args, **kwargs)
                end_time = time.perf_counter()
                total_time = end_time - start_time

                # Change the stacklevel to 2 so the log message has the module and lineno of the function call, not the decorator.
                log = functools.partial(logger.log, stacklevel=2)
                log(_level, f"{total_time:.4f} seconds for Function {func.__name__}")

                return value

            return wrapper_debug

        return decorator
