# trading_sdk/logger.py
import logging
import os
from datetime import datetime

def setup_logger(log_config, sdk_id: str) -> logging.Logger:
    logger = logging.getLogger(sdk_id)
    logger.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "../../apphome/log")
    log_file_path = os.path.join(log_file_path, log_config.path)
    # 确保日志目录存在
    os.makedirs(log_file_path, exist_ok=True)

    # 创建日志格式，增加线程名称和ID
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - [%(threadName)s:%(thread)d] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建按日期分割的文件处理器
    log_filename = os.path.join(
        log_file_path,
        f"rxts_strategy_{sdk_id}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger