import logging,colorlog

log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


class LogUtils:
    """
    日志工具类
    """
    def __init__(self, name):
        self.logger = logging.getLogger(__name__)
        formatter = colorlog.ColoredFormatter(
            f'%(log_color)s[%(asctime)s]-[{name}]-%(levelname)s-%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors=log_colors
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)


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