import signal

def timeout(period=2):
    def decorator(func):
        def handler(sig_num, stack_frame):
            raise TimeoutException()

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(period)
            result = func(*args, **kwargs)
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            return result

        return wrapper
    return decorator
