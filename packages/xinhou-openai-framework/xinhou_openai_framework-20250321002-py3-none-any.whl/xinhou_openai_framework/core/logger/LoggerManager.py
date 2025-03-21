import os
import sys

from loguru import logger as loguru_logger

from xinhou_openai_framework.core.logger.InterceptHandler import setup_logging


class LoggerManager:
    """
    日志管理器
    """

    @staticmethod
    def init_logger(app, log_path):
        """
        初始化日志系统
        """
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # 移除默认的处理器
        loguru_logger.remove()

        # 添加控制台输出
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )

        # 添加文件日志
        log_file = os.path.join(log_path, "app_{time:YYYY-MM-DD}.log")
        loguru_logger.add(
            log_file,
            rotation="00:00",  # 每天午夜切换到新文件
            retention="30 days",  # 保留30天的日志
            compression="zip",  # 压缩旧的日志文件
            encoding="utf-8",
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

        # 添加错误日志文件
        error_log_file = os.path.join(log_path, "error_{time:YYYY-MM-DD}.log")
        loguru_logger.add(
            error_log_file,
            rotation="00:00",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            level="ERROR",
            format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        setup_logging()
        return loguru_logger
