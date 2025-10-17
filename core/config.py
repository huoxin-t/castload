
import os

class Config:
    # 下载目录
    DOWNLOAD_DIR = "download"
    
    # 状态文件路径
    STATUS_FILE = os.path.join(DOWNLOAD_DIR, "download_status.json")
    
    # 播客列表页面URL
    LIST_PAGE_URL = "https://castbox.fm/channel/..."
    
    # 最大并发下载数
    MAX_WORKERS = 3
    
    # 测试模式
    TEST_MODE = True


    # 确保下载目录存在
    @staticmethod
    def init_config():
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

# 初始化配置
Config.init_config()
