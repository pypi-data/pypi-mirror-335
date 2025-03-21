from functools import wraps
import inspect

def NoLogger(func):
    """
    禁用日志打印的装饰器，支持同步和异步函数
    支持所有 HTTP 方法（GET、POST 等）
    """
    # 递归地将 no_logger 属性添加到所有包装函数中
    def add_no_logger_attr(f):
        setattr(f, "no_logger", True)
        if hasattr(f, "__wrapped__"):
            add_no_logger_attr(f.__wrapped__)
    
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        async_wrapper.no_logger = True
        add_no_logger_attr(async_wrapper)
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        sync_wrapper.no_logger = True
        add_no_logger_attr(sync_wrapper)
        return sync_wrapper

# 为了兼容不同的装饰器顺序，提供一个可以放在 FastAPI 路由装饰器下方的版本
def no_logger(func):
    """
    与 NoLogger 功能相同，但可以放在路由装饰器下方使用
    支持所有 HTTP 方法（GET、POST 等）
    """
    # 递归地将 no_logger 属性添加到所有包装函数中
    def add_no_logger_attr(f):
        setattr(f, "no_logger", True)
        if hasattr(f, "__wrapped__"):
            add_no_logger_attr(f.__wrapped__)
    
    add_no_logger_attr(func)
    return func 