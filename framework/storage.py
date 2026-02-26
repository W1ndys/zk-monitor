from __future__ import annotations

import json
from pathlib import Path

from framework.models import Notice


class NoticeStorage:
    """按监控器隔离的 JSON 文件存储，位于 data/ 目录下。"""

    def __init__(self, monitor_name: str, data_dir: Path) -> None:
        self._path = data_dir / f"{monitor_name}.json"
        self._data_dir = data_dir

    def load(self) -> list[Notice]:
        """加载已保存的通知列表。文件不存在时返回空列表。"""
        if not self._path.exists():
            return []
        with open(self._path, "r", encoding="utf-8") as f:
            return [Notice.from_dict(d) for d in json.load(f)]

    def save(self, notices: list[Notice]) -> None:
        """保存通知列表到 JSON 文件。"""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([n.to_dict() for n in notices], f, ensure_ascii=False, indent=2)

    def find_new(self, current: list[Notice], saved: list[Notice]) -> list[Notice]:
        """对比当前与已保存的通知，返回新增部分（按 url 去重）。"""
        saved_urls = {n.url for n in saved}
        return [n for n in current if n.url not in saved_urls]
