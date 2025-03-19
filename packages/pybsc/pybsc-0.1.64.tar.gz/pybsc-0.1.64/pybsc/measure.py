import contextlib
import datetime as datetime_module
import sys

time_isoformat = datetime_module.time.isoformat


time_fromisoformat = datetime_module.time.fromisoformat


def timedelta_isoformat(timedelta, timespec='microseconds'):
    time = (datetime_module.datetime.min + timedelta).time()
    return time_isoformat(time, timespec)


@contextlib.contextmanager
def measure(log_name='Total elapsed time',
            file=sys.stderr):
    """Measure time with contextlib.

    Parameters
    ----------
    log_name : str
        log name
    file : writable object
        writable object such as sys.stderr.

    Examples
    --------
    >>> from pybsc import measure
    >>> with measure('measure example'):
    ...     time.sleep(2.0)
    measure example: 00:00:02.002104
    """
    start_time = datetime_module.datetime.now()
    yield
    duration = datetime_module.datetime.now() - start_time
    now_string = timedelta_isoformat(duration)
    file.write('{log_name}: {now_string}\n'.format(
        **locals()))
