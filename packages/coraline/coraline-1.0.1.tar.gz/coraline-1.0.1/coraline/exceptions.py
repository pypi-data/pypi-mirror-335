class CoralException(Exception):
    pass


class CoralNotFound(CoralException):
    pass


class ConfigError(CoralException):
    pass
