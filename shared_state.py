# -*- coding: utf-8 -*-
"""
Shared State Module — 全局状态代理
通过模块级 __getattr__ 实现延迟绑定，避免循环导入
Blueprint 中使用 import shared_state; shared_state.xxx
"""

import threading

# ==================== 基础锁和标志（app.py 初始化前就需要）====================
_agi_lock = threading.Lock()
_agi_system = None
_agi_ready = False

_medium_symbiosis = None
_medium_symbiosis_lock = threading.Lock()

_compound_agi_lock = threading.Lock()
_compound_agi_ready = False
_compound_agi_system = None

_expert_registry = None
_expert_registry_lock = threading.Lock()

# Flask app 引用
app = None

def set_app(flask_app):
    """设置 Flask app 引用"""
    global app
    app = flask_app


def __getattr__(name):
    """
    模块级属性代理 — 当访问 shared_state.xxx 时：
    1. 先检查本模块是否有该属性
    2. 没有则从 app 模块获取
    3. 再没有则抛出 AttributeError
    """
    # 避免递归：不在 __getattr__ 中触发 app 模块的 __getattr__
    if name.startswith('__') and name.endswith('__'):
        raise AttributeError(name)

    try:
        import app as _app_module
        attr = getattr(_app_module, name)
        # 缓存到本模块
        globals()[name] = attr
        return attr
    except (ImportError, AttributeError):
        raise AttributeError(f"shared_state has no attribute '{name}'")
