from __future__ import annotations

from abc import ABC, abstractmethod

from framework.models import Notice


class BaseNotifier(ABC):
    """通知器基类，每个推送渠道实现一个子类。"""

    name: str  # 通知器唯一标识

    @abstractmethod
    def send(self, monitor_name: str, notices: list[Notice]) -> bool:
        """发送新通知。成功返回 True。"""

    @abstractmethod
    def test(self, monitor_name: str) -> bool:
        """发送连通性测试消息。成功返回 True。"""
