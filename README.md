# zk-monitor

一个基于 Python 的可扩展招考通知监控工具，支持多站点抓取、增量去重和多渠道推送（飞书、OneBot）。

## 功能特性

- 配置驱动：通过 `config.yaml` 动态加载监控器与通知器
- 增量通知：按 `Notice.url` 去重，只推送新通知
- 首次基线：首次运行先做通知渠道连通性测试，再保存基线数据
- 多渠道推送：内置飞书机器人与 OneBot 群消息推送
- 可扩展架构：新增站点或通知渠道无需修改核心调度代码

## 项目结构

```text
zk-monitor/
├── config.yaml
├── main.py
├── framework/
│   ├── models.py
│   ├── monitor.py
│   ├── notifier.py
│   ├── runner.py
│   └── storage.py
├── monitors/
│   ├── sdzk_yzk.py
│   └── tj_zhaokao_ykxk.py
├── notifiers/
│   ├── feishu.py
│   └── onebot.py
├── docs/
│   └── 新网站监控开发文档.md
├── data/
└── logs/
```

## 环境要求

- Python `>=3.10`
- 推荐使用 [uv](https://github.com/astral-sh/uv)

## 快速开始

1. 安装依赖

```powershell
uv sync
```

2. 复制环境变量模板并填写

```powershell
Copy-Item .env.example .env
```

3. 按需修改 `config.yaml`（监控器 URL、启用的通知器）

4. 启动监控

```powershell
uv run python main.py
```

## 环境变量

### 飞书通知器

- `FEISHU_WEBHOOK`：飞书机器人 Webhook
- `FEISHU_SECRET`：飞书签名密钥（可选）

### OneBot 通知器

- `ONEBOT_HTTP_URL`：OneBot HTTP 地址，如 `http://127.0.0.1:3000`
- `ONEBOT_ACCESS_TOKEN`：访问令牌（可选）
- `ONEBOT_GROUP_IDS`：群号列表，英文逗号分隔

## 运行机制说明

- 每个监控器的数据保存在 `data/{monitor_name}.json`
- 每次运行流程：抓取 -> 对比 -> 通知 -> 保存
- 首次运行（无历史数据）会执行通知器 `test()`，测试通过后写入基线

## 扩展开发

- 新增监控器：继承 `framework.monitor.BaseMonitor` 并实现 `fetch()`
- 新增通知器：继承 `framework.notifier.BaseNotifier` 并实现 `send()` 与 `test()`
- 在 `config.yaml` 注册类路径即可生效

详细步骤见：`docs/新网站监控开发文档.md`

## 注意事项

- `data/` 与 `logs/` 已被 `.gitignore` 忽略
- 敏感信息请仅放在 `.env`，不要提交到仓库
