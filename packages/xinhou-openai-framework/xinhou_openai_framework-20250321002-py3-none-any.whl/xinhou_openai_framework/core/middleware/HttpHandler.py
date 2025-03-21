# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
初始化全局Http中间件
----------------------------------------------------
@Project :   xinhou-openai-framework  
@File    :   HttpMiddlewareHandler.py
@Contact :   sp_hrz@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2023/2/20 17:45   shenpeng   1.0         None
"""
import json
import logging
import time
from fastapi import Request, UploadFile
from fastapi.routing import APIRoute

from xinhou_openai_framework.core.logger.Logger import Logger

logger = Logger("HttpHandler", logging.DEBUG)


class HttpHandler:

    @staticmethod
    def init_http_filter(app, context):
        @app.middleware("http")
        async def add_process_filter(request: Request, call_next):
            start_time = time.time()
            
            # 检查当前路由是否有 NoLogger 装饰器
            current_route = None
            for route in request.app.routes:
                if isinstance(route, APIRoute):
                    # 检查路径是否匹配（考虑路径参数）
                    route_path_parts = route.path.split("/")
                    request_path_parts = request.url.path.split("/")
                    
                    # 跳过空字符串（由于路径以/开头）
                    route_path_parts = [p for p in route_path_parts if p]
                    request_path_parts = [p for p in request_path_parts if p]
                    
                    if len(route_path_parts) == len(request_path_parts):
                        match = True
                        for i, part in enumerate(route_path_parts):
                            # 如果是路径参数（以{开头），则认为匹配
                            if part.startswith("{") and part.endswith("}"):
                                continue
                            if part != request_path_parts[i]:
                                match = False
                                break
                        
                        if match and request.method in route.methods:
                            current_route = route
                            break
            
            # 检查是否需要跳过日志
            skip_logging = False
            if current_route:
                # 递归检查函数及其包装函数是否有 no_logger 属性
                def check_no_logger(func):
                    if hasattr(func, 'no_logger'):
                        return True
                    if hasattr(func, "__wrapped__"):
                        return check_no_logger(func.__wrapped__)
                    return False
                
                skip_logging = check_no_logger(current_route.endpoint)
            
            if not skip_logging:
                # 获取请求的IP地址
                client_ip = request.client.host
                request_info = {
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip
                }
                
                try:
                    headers = request.headers
                    if headers:
                        request_info['headers'] = dict(headers)
                except Exception as e:
                    logger.error("[Request Headers]: Unable to parse form headers:{}".format(e))

                try:
                    cookies = request.cookies
                    if cookies:
                        request_info['cookies'] = dict(cookies)
                except Exception as e:
                    logger.error("[Request Cookies]: Unable to parse form cookies:{}".format(e))

                try:
                    query_params = request.query_params
                    if query_params:
                        request_info['query_params'] = dict(query_params)
                except Exception as e:
                    logger.error("[Request Query Params]: Unable to parse form query params:{}".format(e))

                try:
                    body = await request.body()
                    if body:
                        request_info['json_body'] = json.loads(body.decode('utf-8'))
                    else:
                        request_info['json_body'] = {}
                except Exception as e:
                    logger.error("[Request JSON Body]: Unable to read body:{}".format(e))

                try:
                    form_data = await request.form()
                    if len(form_data) > 0:
                        request_info['form_data'] = {
                            key: str(value) if not isinstance(value, UploadFile) else value.filename for key, value in
                            form_data.items()}
                except Exception as e:
                    logger.error("[Request Form Data]: Unable to parse form data:{}".format(e))

                logger.info(f"""
{json.dumps(request_info, indent=4, ensure_ascii=False)}""")

            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
