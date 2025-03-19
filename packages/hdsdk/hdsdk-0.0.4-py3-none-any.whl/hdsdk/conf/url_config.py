#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/6 16:24
# @Author  : yh
# @File    : point_config.py
import os

# 获取环境变量
env = os.getenv('ENV', 'production')

# 根据环境选择 URL
if env == "production":
    BACKEND_CLIENT_URL = "http://ssms-backend:8080"
    EXT_API_CLIENT_URL = "http://light-extendapi:8080"
else:
    BACKEND_CLIENT_URL = 'http://47.106.217.68:31580/backend-api'
    EXT_API_CLIENT_URL = "http://47.106.217.68:31580/ext-api"

# api_client配置
BACKEND_API_PATH = '/api/v1/sso/login'
EXT_API_BASE_PATH = '/api/v1/meta_api/call'

BASE_DIAGNOSIS_URL = 'http://localhost:port/api/v1/algorithm/val'