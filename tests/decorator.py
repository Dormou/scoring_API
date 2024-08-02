import functools


def cases(cases):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    func(*new_args)
                except Exception as ex:
                    print(f"Test: {func.__name__}, case: {case}")
                    raise ex
        return wrapper
    return decorator
