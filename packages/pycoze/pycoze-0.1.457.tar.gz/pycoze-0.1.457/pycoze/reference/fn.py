def single_process(func=None):
    def decorator(f):
        return f

    if func is not None:
        return decorator(func)
    return decorator


def multi_process(func=None):
    def decorator(f):
        return f

    if func is not None:
        return decorator(func)
    return decorator


def generator_function(func=None):
    def decorator(f):
        return f

    if func is not None:
        return decorator(func)
    return decorator


def compatibility(func=None):
    def decorator(f):
        return f

    if func is not None:
        return decorator(func)
    return decorator


def global_process(func=None):
    def decorator(f):
        return f

    if func is not None:
        return decorator(func)
    return decorator
