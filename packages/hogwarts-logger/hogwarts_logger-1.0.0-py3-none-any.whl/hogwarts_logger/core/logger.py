from __future__ import annotations

import inspect
import logging
import sys
import threading
from logging import Logger
from time import time
from typing import Union, Dict, Optional

from hogwarts_logger.core.pycharm_formatter import PycharmFormatter
from hogwarts_logger.core.time_interval_filter import TimeIntervalFilter


class Logger:
    """
    默认级别 info + 直接展示
    -v 展示时间 info级别
    -vv 展示时间 debug级别
    -vvv 展示调用链 trace级别
    """
    logger_dict: Dict[str, Logger] = {}

    info_formatter = PycharmFormatter(
        '%(relative_path)s:%(lineno)s:%(funcName)s %(asctime)s %(level_name)01s %(message)s'
    )
    debug_formatter = PycharmFormatter(
        '%(relative_path)s:%(lineno)s:%(funcName)s:%(interval).2f  %(asctime)s %(level_name)01s %(message)s'
    )
    trace_formatter = PycharmFormatter(
        '%(relative_path)s:%(lineno)s:%(invoke)s:%(interval).2f %(asctime)s %(level_name)01s %(message)s'
    )

    default_formatter = logging.Formatter("%(message)s")

    def __init__(self, name=None):
        self.logger: Optional[Logger] = None
        self.name = name
        self.last = None

        self.default_level = logging.INFO + 1
        self.info_level = logging.INFO
        self.debug_level = logging.DEBUG
        # self._verbose_level = 9
        self.trace_level = logging.DEBUG - 1

        self.log_level_name: Optional[str] = None
        self.log_level: Optional[int] = self.info_level

        # -v -vv -vvv
        self.log_level_list = [
            self.default_level,
            self.info_level,
            self.debug_level,
            self.trace_level,
        ]

    def _init_logger(self, name=None):
        """
        延迟初始化logger，避免影响其他的logger

        如果默认，会按照线程号与时间戳生成日志
        如果name='' 生成根logger
        """

        if name is None:
            name = str(threading.current_thread().ident) + str(time())
        path_logger = logging.getLogger(name=name)
        path_logger.setLevel(self.log_level)

        time_interval_filter = TimeIntervalFilter()
        path_logger.addFilter(time_interval_filter)

        # 默认会输出到stderr，需要指定下
        handler = logging.StreamHandler(sys.stdout)
        path_logger.addHandler(handler)

        # handle.addFilter(time_interval_filter)

        self.logger = path_logger
        self.set_formatter(self.default_formatter)

    def set_formatter(self, formatter=None):
        if formatter is None:
            if self.log_level <= self.trace_level:
                formatter = self.trace_formatter
            elif self.log_level <= self.debug_level:
                formatter = self.debug_formatter
            elif self.log_level <= self.info_level:
                formatter = self.info_formatter
            else:
                formatter = self.default_formatter
        else:
            ...

        for handle in self._get_logger().handlers:
            handle.setFormatter(formatter)

    @classmethod
    def get_invoker_package_name(cls):
        root_package_name = str(__package__).partition('.')[0]
        for frame in inspect.stack():
            if inspect.ismodule(frame.function):
                module = frame.function
            else:
                module = inspect.getmodule(frame.function, _filename=frame.filename)

            if module is None:
                continue

            module_name = module.__name__
            package_name = module_name.partition('.')[0]
            if package_name != root_package_name:
                return package_name

    @classmethod
    def get_instance(cls, name=None):
        if name is None:
            name = cls.get_invoker_package_name()
        if cls.logger_dict.get(name) is None:
            cls.logger_dict[name] = Logger(name)

        return cls.logger_dict[name]

    def _get_logger(self) -> logging.Logger:
        if not self.logger:
            self._init_logger(name=self.name)
        return self.logger

    def log(self, msg, level=None, *args, **kwargs):
        level = level or self.trace_level
        self._get_logger().log(
            level=level,
            msg=msg,
            stacklevel=2,
            *args,
            **kwargs
        )

    def trace(self, msg, *args, **kwargs):
        self.log(msg, level=self.trace_level, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._get_logger().debug(msg, stacklevel=2, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._get_logger().info(msg, stacklevel=2, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._get_logger().warning(msg, stacklevel=2, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._get_logger().error(msg, stacklevel=2, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._get_logger().critical(msg, stacklevel=2, *args, **kwargs)

    def set_level(self, level: Union[int, str]):
        """
        兼容verbose level 与logging level
        1 = debug 2=trace 3=notset

        """

        if isinstance(level, int):
            if level > 3:
                self.log_level = level
            else:
                self.log_level = self.log_level_list[level]
        elif isinstance(level, str):
            level_name = level.lower()
            if level_name == 'debug':
                self.log_level = self.debug_level
            elif level_name == 'trace':
                self.log_level = self.trace_level
            elif level_name == 'info':
                self.log_level = self.info_level
            else:
                ...

        self._get_logger().setLevel(self.log_level)
        self.set_formatter()

        # 控制台的输出，pytest是可以控制的, logger的handler的level默认是NOSET

        # for handle in self.logger.handlers:
        #     handle.setLevel(level)

    def get_level(self):
        return self._get_logger().getEffectiveLevel()

    def get_log_actions(self):
        return [
            self.log,
            self.debug,
            self.info,
            self.warn,
            self.error,
            self.critical,
        ]

    def enable_raw_log(self):
        """
        info级别建议不输出代码行数
        """
        for handler in self.logger.handlers:
            handler.setFormatter(self.default_formatter)

    @classmethod
    def get_logger_name_list(cls) -> Logger:
        name_list = logging.Logger.manager.loggerDict
        return name_list
