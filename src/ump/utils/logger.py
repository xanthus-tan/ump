# -*- encoding:utf-8 -*-
import logging

# ump 日志工具类
from src.ump.metadata.config import LoggerConfig


class UMPLogger:

    def __init__(self):
        self.logger = logging.getLogger('ump')
        log_config = LoggerConfig()
        self.logger.setLevel(log_config.get_log_level())
        if log_config.get_log_handler() == "file":
            log_path = log_config.get_log_path()
            self.handler = logging.FileHandler(log_path, "a", encoding="UTF-8")
        else:
            self.handler = logging.StreamHandler()
        self.handler.setLevel(log_config.get_log_level())
        self.formatter = logging.Formatter('%(asctime)s >> %(levelname)s >> %(msg)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = UMPLogger()
