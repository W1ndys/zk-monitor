from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from loguru import logger

from framework.models import Notice
from framework.monitor import BaseMonitor


class TjZhaokaoYkxkMonitor(BaseMonitor):
    """天津招考资讯网 - 研考研招通知监控。"""

    name = "tj_zhaokao_ykxk"
    display_name = "天津研考研招"

    def __init__(self, url: str = "http://www.zhaokao.net/ykxk/index.shtml") -> None:
        self.url = url

    def fetch(self) -> list[Notice]:
        """抓取天津招考资讯网研考研招页面，解析并返回通知列表。"""
        logger.info(f"正在请求: {self.url}")
        resp = requests.get(self.url, timeout=15)
        resp.encoding = "utf-8"
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # 每条通知是一个 a 标签，位于 div.zi16 内，href 包含 /ykxk/system/
        links = soup.select("div.zi16 a[href*='/ykxk/system/']")

        notices: list[Notice] = []
        for a_tag in links:
            href = a_tag.get("href", "")
            title = a_tag.get("title", "") or a_tag.get_text(strip=True)

            # 日期在同一行容器的第二个 div.zi16 中
            row = a_tag.parent.parent
            date_divs = row.select("div.zi16")
            date = date_divs[-1].get_text(strip=True) if len(date_divs) >= 2 else ""

            notices.append(Notice(title=title, url=href, date=date))

        logger.info(f"共获取到 {len(notices)} 条通知")
        return notices
