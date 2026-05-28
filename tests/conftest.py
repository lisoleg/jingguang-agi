# -*- coding: utf-8 -*-
"""
pytest 共享 fixtures — 太乙AGI测试基础设施
"""
import sys
import os
import pytest

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(scope="session")
def flask_app():
    """创建Flask应用实例（session级别共享）"""
    from app import app
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def client(flask_app):
    """Flask测试客户端"""
    return flask_app.test_client()
