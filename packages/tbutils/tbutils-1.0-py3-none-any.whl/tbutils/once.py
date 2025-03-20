from logging import INFO, WARNING, Logger
from typing import Callable

dict_printing_messages = set()


def one_time_printing(message : str):
    """Print a message only if it has not been printed before.

    Args:
        message (str): The message to print.
    """
    message = str(message)
    if message not in dict_printing_messages:
        print(message)
        dict_printing_messages.add(message)


dict_log_messages = set()


def one_time_log(logger: Logger, message: str, level=INFO, *args, **kwargs):
    """Log a <level> message only if it has not been logged before.

    Args:
        logger (Logger): The logger to log the message.
        message (str): The message to log.
        level: The level at which to log the message.
        args: The arguments to pass to the logger.
        kwargs: The keyword arguments to pass to the logger
    """
    message = str(message)
    if message not in dict_log_messages:
        logger.log(level, message, *args, **kwargs)
        dict_log_messages.add(message)


def one_time_warning(logger: Logger, message: str, *args, **kwargs):
    return one_time_log(logger, message, WARNING, *args, **kwargs)


def one_time_exec(func: Callable):
    """Decorator to make a function only execute once.

    Args:
        func (Callable): The function to decorate.
    """
    assert callable(func), f"Expected a callable, got {func}"
    def wrapper(*args, **kwargs):
        if not wrapper.has_executed:
            wrapper.has_executed = True
            return func(*args, **kwargs)

    wrapper.has_executed = False
    return wrapper
