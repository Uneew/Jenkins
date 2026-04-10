import os
import yaml
import logging

# 配置日志，便于在 Jenkins 控制台查看
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # 读取环境变量，默认为 test
        self.env = os.getenv("TEST_ENV", "test")
        logger.info(f"当前运行环境: {self.env}")

        # 获取当前文件所在目录的绝对路径（即 config/ 目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "env.yaml")
        logger.info(f"配置文件路径: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                all_config = yaml.safe_load(f)
            self.env_config = all_config[self.env]
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

        self.BASE_URL = self.env_config["base_url"]
        self.TIMEOUT = self.env_config["timeout"]
        self.HEADERS = {
            "Content-Type": "application/json",
            "User-Agent": "AutoTest-Client/1.0"
        }
        logger.info(f"BASE_URL = {self.BASE_URL}")

config = Config()