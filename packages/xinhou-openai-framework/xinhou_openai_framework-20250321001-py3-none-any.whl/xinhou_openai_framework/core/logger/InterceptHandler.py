import logging
import sys

from loguru import logger as loguru_logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys.exc_info()[2], 2
        while frame and frame.tb_frame.f_code.co_filename == logging.__file__:
            frame = frame.tb_next
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # 移除所有现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # 配置 loguru
    loguru_logger.remove()  # 移除默认的 sink
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}",
        level="INFO",
        enqueue=True
    )

    # 配置拦截器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


# 在模块导入时立即设置日志
setup_logging()
