from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Notice:
    """通知数据模型，通过 url 去重。"""

    title: str
    url: str
    date: str

    def to_dict(self) -> dict:
        """转换为字典，用于 JSON 序列化。"""
        return {"title": self.title, "url": self.url, "date": self.date}

    @classmethod
    def from_dict(cls, d: dict) -> Notice:
        """从字典创建 Notice 实例，用于 JSON 反序列化。"""
        return cls(title=d["title"], url=d["url"], date=d["date"])
