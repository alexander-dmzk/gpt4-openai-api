class Singleton(type):
    """
    Singleton meta class.

    Usage:
        class Foo(<ParentClass>, metaclass=Singleton):
            pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def clear(mcs, class_):
        mcs._instances.pop(class_, None)
