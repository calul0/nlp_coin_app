"""
    Self defined Singleton, to use design pattern easier on dedicated classes.
"""


class Singleton(type):
    """
        Metaclass singleton implementation.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton,
                cls
            ).__call__(*args, **kwargs)

        return cls._instances[cls]
