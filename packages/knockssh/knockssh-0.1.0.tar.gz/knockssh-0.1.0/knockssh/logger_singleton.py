import logging

class Logger:
    def __init__(self, verbosity):
        logging_level = self._map_verbosity(verbosity)
        logging.basicConfig(
            level=logging_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _map_verbosity(self, verbosity):
        if verbosity >= 3:
            return logging.DEBUG
        elif verbosity == 2:
            return logging.INFO
        elif verbosity == 1:
            return logging.WARNING
        else:
            return logging.ERROR

    def debug(self, msg):
        logging.debug(msg)

    def info(self, msg):
        logging.info(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

_logger_instance = None

def init_logger(verbosity) -> Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger(verbosity)
        _logger_instance.info("Logger initialized")
    return _logger_instance

def get_logger() -> Logger:
    if _logger_instance is None:
        raise Exception("Logger not initialized yet.")
    return _logger_instance
