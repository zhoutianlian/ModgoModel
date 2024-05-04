class LogLv:
    level = 2


def set_log_level(level):
    assert level in [0, 1, 2], f'Illegal log level {level}'
    LogLv.level = level
