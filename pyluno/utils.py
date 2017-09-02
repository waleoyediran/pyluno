

import functools
import inspect
import logging
import traceback
import warnings
# class BaseClass(object):
#     def __init__(self):
from time import sleep, time

log = logging.getLogger(__name__)



def RateLimiter(f):
    """Rate Limiter decorator."""
    burst_count, first_burst = ([0], [0.0])

    def wrapper(*args, **kwargs):
        max_rate = args[0].maxRate
        burst = args[0].maxBurst
        cur_time = time()
        if (max_rate is None) or (burst is None):
            return f(*args, **kwargs)
            # return ret
        min_interval = 1.0 / float(max_rate)
        if burst_count[0] == 0:
            first_burst[0] = cur_time
            burst_count[0] += 1
        if burst_count[0] <= burst:
            burst_count[0] += 1
            # ret = f(*args, **kwargs)
        if burst_count[0] == burst+1:
            elapsed = cur_time - first_burst[0]
            # ret = f(*args, **kwargs)
            burst_count[0] = 1
            wait_time = burst*min_interval - elapsed
            if wait_time > 0:
                log.warning('Rate limited! Waiting {:.2f}s'.format(wait_time))
                sleep(wait_time)
        if burst_count[0] == 1:
            first_burst[0] = time()
        return f(*args, **kwargs)
    return wrapper


class LunoAPIError(ValueError):
    """Generic Error Class."""

    def __init__(self, response):
        """Instatiate with an error response."""
        self.url = response.url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        """Return a string error message."""
        return "Luno request %s failed with %d: %s" % (
            self.url, self.code, self.message)


class LunoAPIRateLimitError(ValueError):
    """Generic rate limit error class."""

    def __init__(self, response):
        """Instanciate with a rate error response."""
        self.url = response.url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        """Return a string error message."""
        return "Rate Limit Error.\nLuno request %s failed with %d: %s" % (
            self.url, self.code, self.message)


def deprecated(message: str = ''):
    """Deprication decorator.

    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used first time and filter is set for show
    DeprecationWarning.
    """
    def decorator_wrapper(func):
        @functools.wraps(func)
        def function_wrapper(*args, **kwargs):
            current_call_source = '|'.join(traceback.format_stack(
                inspect.currentframe()))
            if current_call_source not in function_wrapper.last_call_source:
                warnings.warn("{} is now deprecated! {}".format(
                    func.__name__, message),
                              category=DeprecationWarning, stacklevel=2)
                # warnings.simplefilter('always', DeprecationWarning)  # turn off filter
                function_wrapper.last_call_source.add(current_call_source)

            return func(*args, **kwargs)

        function_wrapper.last_call_source = set()

        return function_wrapper
    return decorator_wrapper
