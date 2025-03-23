from hogwarts_logger.core.logger import Logger

logger = Logger.get_instance()
trace, debug, info, warn, error = logger.get_log_actions()[:5]
