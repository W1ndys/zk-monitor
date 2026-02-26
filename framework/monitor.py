from __future__ import annotations

from abc import ABC, abstractmethod

from framework.models import Notice


class BaseMonitor(ABC):
    """监控器基类，每个目标网站实现一个子类。"""

    name: str  # 唯一标识，用于存储文件名和日志前缀
    display_name: str  # 人类可读名称，用于通知消息

    @abstractmethod
    def fetch(self) -> list[Notice]:
        """抓取并解析目标页面，返回通知列表。"""
