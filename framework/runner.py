from __future__ import annotations

import importlib
from pathlib import Path

import yaml
from loguru import logger

from framework.models import Notice
from framework.monitor import BaseMonitor
from framework.notifier import BaseNotifier
from framework.storage import NoticeStorage

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _import_class(dotted_path: str):
    """根据点分模块路径动态导入类，如 'monitors.sdzk_yzk.SdzkYzkMonitor'。"""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _instantiate(entry: dict):
    """根据配置项实例化类，支持可选的 args 参数。"""
    cls = _import_class(entry["class"])
    args = entry.get("args", {})
    return cls(**args)


def run_all(config_path: str | Path = "config.yaml") -> None:
    """读取配置文件，实例化所有监控器和通知器，依次执行监控任务。"""
    config_path = BASE_DIR / config_path
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 实例化通知器
    notifiers: list[BaseNotifier] = []
    for entry in config.get("notifiers", []):
        try:
            notifier = _instantiate(entry)
            notifiers.append(notifier)
            logger.info(f"已加载通知器: {notifier.name}")
        except Exception as e:
            logger.error(f"加载通知器 {entry['class']} 失败: {e}")

    # 实例化并运行监控器
    for entry in config.get("monitors", []):
        try:
            monitor: BaseMonitor = _instantiate(entry)
            logger.info(f"已加载监控器: {monitor.name} ({monitor.display_name})")
        except Exception as e:
            logger.error(f"加载监控器 {entry['class']} 失败: {e}")
            continue

        _run_monitor(monitor, notifiers)


def _run_monitor(monitor: BaseMonitor, notifiers: list[BaseNotifier]) -> None:
    """执行单个监控器的 抓取→对比→通知 流程。"""
    log = logger.bind(monitor=monitor.name)
    log.info(f"===== 开始执行监控: {monitor.display_name} =====")

    storage = NoticeStorage(monitor.name, DATA_DIR)

    # 抓取通知
    try:
        current_notices = monitor.fetch()
    except Exception as e:
        log.error(f"获取通知失败: {e}")
        return

    if not current_notices:
        log.warning("未获取到任何通知，跳过处理")
        return

    saved_notices = storage.load()

    # 首次运行：测试通知器，保存基线数据后返回
    if not saved_notices:
        log.info("首次运行，发送测试消息验证各推送渠道连通性")
        if not notifiers:
            log.error("未配置任何推送渠道")
            return
        all_ok = True
        for notifier in notifiers:
            try:
                ok = notifier.test(monitor.display_name)
                if not ok:
                    all_ok = False
            except Exception as e:
                log.error(f"通知器 {notifier.name} 测试异常: {e}")
                all_ok = False
        if not all_ok:
            log.error("部分推送渠道连通性测试未通过，请检查配置")
            return
        storage.save(current_notices)
        log.info(f"已保存 {len(current_notices)} 条通知（首次基线）")
        return

    # 对比新旧通知
    new_notices = storage.find_new(current_notices, saved_notices)

    if new_notices:
        log.info(f"发现 {len(new_notices)} 条新通知:")
        for n in new_notices:
            log.info(f"  [{n.date}] {n.title}")
        # 推送通知
        for notifier in notifiers:
            try:
                notifier.send(monitor.display_name, new_notices)
            except Exception as e:
                log.error(f"通知器 {notifier.name} 发送失败: {e}")
    else:
        log.info("暂无新通知")

    # 无论是否有新通知，都更新存储（页面可能删除旧通知）
    storage.save(current_notices)
    log.info(f"已保存 {len(current_notices)} 条通知")
    log.info(f"===== 监控任务执行完毕: {monitor.display_name} =====")
