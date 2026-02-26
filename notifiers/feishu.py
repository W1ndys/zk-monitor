from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time

import requests
from loguru import logger

from framework.models import Notice
from framework.notifier import BaseNotifier


class FeishuNotifier(BaseNotifier):
    """飞书 Webhook 通知器。"""

    name = "feishu"

    def __init__(self) -> None:
        self.webhook = os.getenv("FEISHU_WEBHOOK", "")
        self.secret = os.getenv("FEISHU_SECRET", "")

    def _gen_sign(self) -> tuple[str, str]:
        """生成飞书机器人签名，返回 (timestamp, sign)。"""
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return timestamp, sign

    def _post(self, body: dict) -> bool:
        """发送请求到飞书 Webhook，自动附加签名。成功返回 True。"""
        if not self.webhook:
            logger.warning("未配置 FEISHU_WEBHOOK，跳过飞书推送")
            return False
        if self.secret:
            timestamp, sign = self._gen_sign()
            body["timestamp"] = timestamp
            body["sign"] = sign
        try:
            resp = requests.post(self.webhook, json=body, timeout=10)
            result = resp.json()
            if result.get("code") == 0:
                logger.info("飞书消息发送成功")
                return True
            else:
                logger.error(f"飞书消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书消息发送异常: {e}")
            return False

    def send(self, monitor_name: str, notices: list[Notice]) -> bool:
        """将新通知以富文本格式发送到飞书群。"""
        content_lines = []
        for n in notices:
            content_lines.append(
                [
                    {"tag": "text", "text": f"{n.date}  "},
                    {"tag": "a", "text": n.title, "href": n.url},
                ]
            )

        body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"{monitor_name}新通知（{len(notices)}条）",
                        "content": content_lines,
                    }
                }
            },
        }
        return self._post(body)

    def test(self, monitor_name: str) -> bool:
        """发送飞书测试消息，验证 Webhook 连通性。"""
        if not self.webhook:
            logger.warning("未配置 FEISHU_WEBHOOK，跳过连通性测试")
            return False
        logger.info("正在发送飞书测试消息，验证 Webhook 连通性...")
        body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"{monitor_name}监控 - 初始化测试",
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": "飞书机器人连通性测试成功，监控服务已启动。",
                                }
                            ]
                        ],
                    }
                }
            },
        }
        ok = self._post(body)
        if ok:
            logger.info("飞书连通性测试通过")
        return ok
