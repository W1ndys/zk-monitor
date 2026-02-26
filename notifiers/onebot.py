from __future__ import annotations

import os

import requests
from loguru import logger

from framework.models import Notice
from framework.notifier import BaseNotifier


class OneBotNotifier(BaseNotifier):
    """OneBot HTTP 群消息通知器。"""

    name = "onebot"

    def __init__(self) -> None:
        self.http_url = os.getenv("ONEBOT_HTTP_URL", "").rstrip("/")
        self.access_token = os.getenv("ONEBOT_ACCESS_TOKEN", "")
        self.group_ids: list[int] = [
            int(gid.strip())
            for gid in os.getenv("ONEBOT_GROUP_IDS", "").split(",")
            if gid.strip().isdigit()
        ]

    def _headers(self) -> dict[str, str]:
        """构造 OneBot HTTP 请求头，含鉴权 Token。"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _send_to_groups(self, message: str) -> bool:
        """向所有配置的群发送消息，全部成功返回 True。"""
        if not self.http_url or not self.group_ids:
            logger.warning("未配置 ONEBOT_HTTP_URL 或 ONEBOT_GROUP_IDS，跳过 OneBot 推送")
            return False

        api_url = f"{self.http_url}/send_group_msg"
        headers = self._headers()
        success = True

        for group_id in self.group_ids:
            body = {"group_id": group_id, "message": message}
            try:
                resp = requests.post(api_url, json=body, headers=headers, timeout=10)
                result = resp.json()
                if result.get("status") == "ok" or result.get("retcode") == 0:
                    logger.info(f"OneBot 群 {group_id} 消息发送成功")
                else:
                    logger.error(f"OneBot 群 {group_id} 消息发送失败: {result}")
                    success = False
            except Exception as e:
                logger.error(f"OneBot 群 {group_id} 消息发送异常: {e}")
                success = False

        return success

    def send(self, monitor_name: str, notices: list[Notice]) -> bool:
        """将新通知以纯文本格式发送到 QQ 群。"""
        lines = [f"【{monitor_name}新通知（{len(notices)}条）】\n"]
        for n in notices:
            lines.append(f"{n.date}  {n.title}\n{n.url}\n")
        message = "\n".join(lines)
        return self._send_to_groups(message)

    def test(self, monitor_name: str) -> bool:
        """发送 OneBot 测试消息，验证连通性。"""
        if not self.http_url or not self.group_ids:
            logger.warning("未配置 ONEBOT_HTTP_URL 或 ONEBOT_GROUP_IDS，跳过 OneBot 连通性测试")
            return False
        logger.info("正在发送 OneBot 测试消息，验证连通性...")
        message = f"【{monitor_name}监控】初始化测试成功，监控服务已启动。"
        ok = self._send_to_groups(message)
        if ok:
            logger.info("OneBot 连通性测试通过")
        return ok
