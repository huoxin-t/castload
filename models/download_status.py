
import json
import os
from core.config import Config

class DownloadStatus:
    def __init__(self):
        self.status_file = Config.STATUS_FILE
        self.status = {}
        self.load_status()
    
    def load_status(self):
        """从文件加载下载状态"""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status = json.load(f)
            except Exception as e:
                print(f"加载状态文件时出错: {e}")
                self.status = {}
    
    def save_status(self):
        """将下载状态保存到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态文件时出错: {e}")
    
    def mark_as_downloaded(self, url):
        """标记特定URL为已下载"""
        self.status[url] = True
        self.save_status()
    
    def is_downloaded(self, url):
        """检查特定URL是否已下载"""
        return self.status.get(url, False)