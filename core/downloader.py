
import requests
import os
import threading
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.download_status import DownloadStatus
from core.config import Config

class PodcastDownloader:
    def __init__(self):
        self.download_dir = Config.DOWNLOAD_DIR
        self.max_workers = Config.MAX_WORKERS
        self.download_status = DownloadStatus()
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
    
    def _generate_filename(self, title):
        """生成安全的文件名"""
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        # 限制文件名长度，避免过长
        safe_title = safe_title[:100]  # 限制100个字符
        return f"{safe_title}.mp3"
    
    def _handle_duplicate_filename(self, filepath):
        """处理重复文件名"""
        base_filepath = filepath
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(base_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1
        return filepath
    
    def download_episode(self, episode_info, force_download=False):
        """下载单个播客剧集"""
        title = episode_info[0]  # 标题
        url = episode_info[1]    # URL
        
        # 检查是否已经下载（除非强制下载）
        if not force_download and self.download_status.is_downloaded(url):
            return f"播客 '{title}' 已经下载过了，跳过。"
        
        try:
            print(f"开始下载: {title}")
            # 添加浏览器请求头以避免被服务器拒绝
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # 生成文件名（使用播客标题作为文件名）
            filename = self._generate_filename(title)
            filepath = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在，如果存在则添加序号（强制下载时总是添加序号）
            if force_download and os.path.exists(filepath):
                filepath = self._handle_duplicate_filename(filepath)
            
            # 下载文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 更新下载状态
            self.download_status.mark_as_downloaded(url)
            
            return f"成功下载: {title}"
        except Exception as e:
            return f"下载 '{title}' 时出错: {str(e)}"
    
    def download_episodes(self, episodes):
        """使用多线程下载多个播客剧集"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务
            future_to_episode = {
                executor.submit(self.download_episode, episode): episode 
                for episode in episodes
            }
            
            # 收集结果
            for future in as_completed(future_to_episode):
                result = future.result()
                results.append(result)
                print(result)
        
        return results
