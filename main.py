from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# 确保运行时目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 日志配置
logger.add(
    LOGS_DIR / "{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
    level="DEBUG",
)

# 在导入 framework 之前加载环境变量（通知器初始化时会读取环境变量）
load_dotenv(BASE_DIR / ".env")


def main() -> None:
    from framework.runner import run_all

    run_all()


if __name__ == "__main__":
    main()
