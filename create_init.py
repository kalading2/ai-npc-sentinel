# create_init.py
import os
from pathlib import Path

root_dir = Path(__file__).parent / "agent"

for dirpath, dirnames, filenames in os.walk(root_dir):
    init_file = os.path.join(dirpath, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            pass  # 创建空文件
        from loguru import logger
        logger.info(f"Created: {init_file}")