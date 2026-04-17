# -*- coding: utf-8 -*-
import random
import string
from datetime import datetime

def generate_random_string(length=8):
    """生成随机字符串，常用于注册用户名"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def format_timestamp(ts=None):
    """格式化时间戳"""
    if ts is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def extract_json_value(json_obj, path):
    """(进阶) 根据路径从字典中提取值，如 'data.user.id'"""
    keys = path.split('.')
    for key in keys:
        if isinstance(json_obj, dict):
            json_obj = json_obj.get(key)
        else:
            return None
    return json_obj