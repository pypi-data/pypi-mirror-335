from hylog import get_logger


log = get_logger()


def test_module_logger() -> None:
    log.debug("DEBUG message from module")
    log.info("INFO message from module")
    log.warning("WARNING message from module")
    log.error("ERROR message from module")
    log.critical("CRITICAL message from module")

    try:
        1 / 0

    except ZeroDivisionError as e:
        log.exception("Exception occurred in module", exc_info=e)


@log.func()
def test_module_logger_with_debug_decorator(arg1: str, *, kwarg1: int) -> str:
    return f"arg1: {arg1}, kwarg1: {kwarg1}"


@log.perf()
def test_module_logger_with_perf_decorator() -> None:
    import time

    time.sleep(2)


def test_module_loggers() -> None:
    test_module_logger()
    test_module_logger_with_debug_decorator("test_module", kwarg1=42)
    test_module_logger_with_perf_decorator()
