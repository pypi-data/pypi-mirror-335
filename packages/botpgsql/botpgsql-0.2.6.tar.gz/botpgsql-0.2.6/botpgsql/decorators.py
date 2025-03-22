import time
import logging


def time_out(
        time_out: int = 20,
        raise_exception: bool = True,
        show_exception: bool = False,
        delay: int = 1,
        **kwargsv
        ):
    """
    Decorator that makes a function repeat its execution until a given timeout 
    limit is reached, if necessary. If the function runs without raising 
    exceptions before
    the timeout, it is not repeated.

    :param time_out: Time limit until the function is stopped, defaults to 20
    :type time_out: int, optional
    :param raise_exception: Whether to raise an exception after timeout,
     defaults to False
    :type raise_exception: bool, optional
    :param show_exception: Print the exception traceback in the console
    :type show_exception: bool, optional
    :param delay: time in seconds to wait until try again
    :type delay: int, optional
    :param default_return: Default value to return if the decorated function
    doesn't return anything
    :type default_return: Any
    :param verbose: Print, func_name, args, and kwargs of the decorated 
    function to debug
    :type verbose: bool, optional
    """
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            contador_time_out = 0
            ret = kwargsv.get('default_return', False)
            verbose = kwargsv.get('verbose', False)
            error = None
            while contador_time_out < time_out:
                if verbose:
                    logging.info('#' * 20, func.__name__, '#' * 20)
                    logging.info('_' * 20, 'args', '_' * 20)
                    logging.info(args)
                    logging.info('_' * 20, 'kwargs', '_' * 20)
                    logging.info(kwargs)
                try:
                    ret = func(*args, **kwargs)
                    break
                except Exception as e:
                    error = e
                    if show_exception:
                        logging.exception(error)
                    time.sleep(delay)
                contador_time_out += 1

                if contador_time_out >= time_out and raise_exception:
                    raise error
            return ret

        return inner_wrapper

    return wrapper