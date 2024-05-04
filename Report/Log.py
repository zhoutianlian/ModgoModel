# -*- coding: utf-8 -*-：
import Config.Log
from datetime import datetime
import os


__all__ = ['logger']


__basedir__ = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
log_dir = __basedir__ + "/setting/"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
__path__ = os.path.join(log_dir, 'log.txt')
__level__ = Config.Log.LogLv.level


def logger(level: int, info):
    """
    这是一个分级日志
    如果Env.LogLevel.level=0，则表示显示所有日志信息，开发时可用此等级
    如果Env.LogLevel.level=1，则显示1级和以上的日志信息，测试时可用此等级
    如果Env.LogLevel.level=2，则仅显示最高级2级的日志信息，生产时可用此等级
    :param level:
    :param info:
    :return:
    """
    if level >= __level__:
        with open(__path__, 'a', encoding="utf8") as file:
            file.write(f'Event level: {level} at {datetime.now()}: {info}\n')
    else:
        print(datetime.now(), info)


# def logs(func):
#     name = func.__name__
#
#     def wrapper(*args, **kwargs):
#         print(f'调用函数 {name}')
#         try:
#             res = func(*args, **kwargs)
#             print(f'结束函数 {name}')
#             return res
#         except Exception as err:
#             print(f'函数 {name} 发生错误: {err}')
#             raise err
#     return wrapper
