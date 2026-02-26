from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from loguru import logger

from framework.models import Notice
from framework.monitor import BaseMonitor


class SdzkYzkMonitor(BaseMonitor):
    """山东省研究生招考通知监控。"""

    name = "sdzk_yzk"
    display_name = "山东省研究生招考"

    def __init__(self, url: str = "https://www.sdzk.cn/NewsList.aspx?BCID=25&CID=1124") -> None:
        self.url = url
        self.base_url = "https://www.sdzk.cn/"

    def fetch(self) -> list[Notice]:
        """抓取山东省招考院通知列表页，解析并返回通知列表。"""
        logger.info(f"正在请求: {self.url}")
        resp = requests.get(self.url, timeout=15)
        resp.encoding = "utf-8"
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("div.blockLine ul.bd li a")

        notices: list[Notice] = []
        for a_tag in items:
            href = a_tag.get("href", "")
            title = a_tag.get("title", "") or a_tag.select_one("span").get_text(strip=True)
            date_tag = a_tag.select_one("i")
            date = date_tag.get_text(strip=True) if date_tag else ""
            url = href if href.startswith("http") else self.base_url + href

            notices.append(Notice(title=title, url=url, date=date))

        logger.info(f"共获取到 {len(notices)} 条通知")
        return notices
