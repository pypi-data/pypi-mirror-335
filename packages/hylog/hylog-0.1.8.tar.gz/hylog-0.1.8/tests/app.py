import time

from pathlib import Path

import module

from hylog import get_app_logger


OUTPUT_DIR = Path.cwd() / "logs"

log = get_app_logger(output_dir=OUTPUT_DIR, stdout_level="DEBUG")
# log = get_app_logger(output_dir=OUTPUT_DIR)


def test_logger() -> None:

    @log.func()
    def test_func_decorator(arg1: str, *, kwarg1: int) -> str:
        return f"arg1: {arg1}, kwarg1: {kwarg1}"

    @log.perf()
    def test_perf_decorator() -> None:
        time.sleep(1)

    def test_log_messages() -> None:
        log.debug("DEBUG message")
        log.debug("DEBUG message with extra", extra={"extra_key": "extra_value"})
        log.info("INFO message")
        log.warning("WARNING message")
        log.error("ERROR message")
        log.critical("CRITICAL message")

        log.info(Path().cwd())
        log.info(Path().home())

        try:
            1 / 0

        except ZeroDivisionError as e:
            log.exception("Exception occurred", exc_info=e)

    test_log_messages()
    test_func_decorator("test", kwarg1=42)
    test_perf_decorator()

    module.test_module_loggers()




if __name__ == "__main__":
    test_logger()
