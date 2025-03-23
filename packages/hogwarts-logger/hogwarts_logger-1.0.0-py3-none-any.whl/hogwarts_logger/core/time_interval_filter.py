import logging
from logging import LogRecord
from time import time


class TimeIntervalFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.last_log_time = time()

    def filter(self, record: LogRecord):
        current_time = time()
        # 计算与上一次日志记录之间的时间间隔
        interval = current_time - self.last_log_time
        self.last_log_time = current_time
        # 在日志消息中加入时间间隔
        record.interval = interval
        return True
