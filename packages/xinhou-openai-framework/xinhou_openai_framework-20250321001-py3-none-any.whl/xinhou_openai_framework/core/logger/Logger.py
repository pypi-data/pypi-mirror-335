import sys

from loguru import logger as loguru_logger


class Logger:
    def __init__(self, name, level="INFO"):
        self.name = name

        # 移除默认的 handler
        loguru_logger.remove()

        # 添加控制台输出
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}",
            level=level,
            enqueue=True
        )

    def info(self, msg, *args, **kwargs):
        loguru_logger.bind(name=self.name).info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        loguru_logger.bind(name=self.name).error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        loguru_logger.bind(name=self.name).warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        loguru_logger.bind(name=self.name).debug(msg, *args, **kwargs)
