import logging
from nonebot.log import logger

class LogUtils:
    """
    日志工具类
    """
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def info(self, message):
        """
        输出info级别的日志
        :param message: 日志内容
        """
        self.logger.info(message)

    def warning(self, message):
        """
        输出warning级别的日志
        :param message: 日志内容
        """
        self.logger.warning(message)

    def error(self, message):
        """
        输出error级别的日志
        :param message: 日志内容
        """
        self.logger.error(message)

    def debug(self, message):
        """
        输出debug级别的日志
        :param message: 日志内容
        """
        self.logger.debug(message)

    @staticmethod
    def set_log_format(plugin_name):
        format_str = f"[%(asctime)s] [%(levelname)s] [{plugin_name}] %(message)s"
        formatter = logging.Formatter(format_str)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
