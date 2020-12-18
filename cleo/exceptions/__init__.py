class CleoException(Exception):

    pass


class LogicException(CleoException):

    pass


class RuntimeException(RuntimeError):

    pass


class ValueException(ValueError):

    pass
