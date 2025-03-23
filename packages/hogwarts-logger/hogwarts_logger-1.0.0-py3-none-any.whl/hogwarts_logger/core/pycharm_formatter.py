import inspect
import logging
import os
from logging import LogRecord
from pathlib import Path


class PycharmFormatter(logging.Formatter):
    """
    增加在pycharm里key直接点击文件路径跳转到代码位置的功能
    """

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        super().__init__(fmt, datefmt, style, validate)
        self.cwd = os.getcwd()

    @classmethod
    def get_invoke(cls, record: LogRecord):
        # 获取当前堆栈信息
        stack = inspect.stack()
        for i, s in enumerate(stack):
            if s.filename.rpartition(os.sep)[-1] == record.filename and s.lineno == record.lineno:
                # 被调用方
                index = i + 1
                break
        else:
            index = None

        # 检查是否有父级调用函数

        if index:
            invoke = f'{stack[index].function}:{record.funcName}'  # 获取父级调用函数名
        else:
            invoke = f'{record.funcName}'
        return invoke

    def format(self, record: LogRecord):
        # todo: 仍旧有部分路径无法跳转

        # if record.pathname.startswith(sys.path[0]):
        #     relative_path = record.pathname[len(sys.path[0]) + 1:]
        # else:
        #     relative_path = record.pathname

        # 使用相对路径，但是不能表示 ../a/b 目录
        # path = Path(record.pathname)
        # if path.is_relative_to(self.cwd):
        #     relative_path = path.relative_to(self.cwd)
        # else:
        #     relative_path = record.pathname
        record.relative_path = os.path.relpath(record.pathname, self.cwd)
        record.invoke = self.get_invoke(record)
        record.level_name = record.levelname[0]
        if not hasattr(record, 'interval'):
            record.interval = 0  # 如果没有 interval，设置为 0
        return super().format(record)
