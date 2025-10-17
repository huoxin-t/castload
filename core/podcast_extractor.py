import re
import asyncio
import os
from playwright.async_api import async_playwright
from core.config import Config
from database import insert_or_update_podcast, get_podcast_by_url
from models.podcast_models import Podcast

class PodcastExtractor:
    """通用播客提取器，支持多种音频源"""
    
    def __init__(self):
        self.test_mode = Config.TEST_MODE
    
    def save_episodes_to_file(self, episodes):
        """将播客列表保存到文件"""
        filepath = os.path.join(Config.DOWNLOAD_DIR, 'podcast_links.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            for title, url in episodes:
                f.write(f"{title},{url}\n")
    
    def load_episodes_from_file(self):
        """从文件加载播客列表"""
        filepath = os.path.join(Config.DOWNLOAD_DIR, 'podcast_links.txt')
        if os.path.exists(filepath):
            episodes = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',', 1)
                    if len(parts) == 2:
                        episodes.append((parts[0], parts[1]))
            return episodes
        return []
    
    # 定义多种音频URL模式
    AUDIO_PATTERNS = [
        # 原有的vistopia模式
        r'https?:\/\/cdn\d+\.vistopia\.com\.cn\/[a-zA-Z0-9-]+\.mp3',
        # Art19模式（您提供的测试链接）
        r'https?:\/\/rss\.art19\.com\/episodes\/[a-zA-Z0-9-]+\.mp3[^"\']*\b',
        # 通用MP3链接模式
        r'https?:\/\/[^\s"\']+\.(mp3|wav|m4a)[^\s"\']*',
        # 包含audio的通用模式
        r'https?:\/\/[^\s"\']*\/audio\/[^\s"\']*',
        # 包含media的通用模式
        r'https?:\/\/[^\s"\']*\/media\/[^\s"\']*'
    ]
    
    @classmethod
    async def extract_audio_url(cls, page_content):
        """
        从页面内容中提取音频URL
        
        Args:
            page_content (str): 页面HTML内容
            
        Returns:
            str or None: 找到的音频URL，如果未找到则返回None
        """
        # 尝试各种模式匹配音频URL
        for pattern in cls.AUDIO_PATTERNS:
            match = re.search(pattern, page_content)
            if match:
                return match.group(0)
        
        # 如果正则表达式没有找到，尝试查找audio标签
        audio_match = re.search(r'<audio[^>]*src=[\'"]([^\'"]+)[\'"]', page_content)
        if audio_match:
            return audio_match.group(1)
            
        # 查找source标签
        source_match = re.search(r'<source[^>]*src=[\'"]([^\'"]+)[\'"][^>]*type=[\'"]audio', page_content)
        if source_match:
            return source_match.group(1)
            
        return None
    
    async def get_episodes_list(self, podcast_url=None, batch_size=10):
        """
        获取播客列表，支持分批加载
        
        Args:
            podcast_url (str): 播客频道URL
            batch_size (int): 每批处理的播客数量
            
        Returns:
            tuple: (podcast_name, list) 包含播客名称和播客信息的元组 [('title', 'url'), ...]
        """
        # 如果没有提供URL，使用配置中的默认URL
        if podcast_url is None:
            podcast_url = Config.LIST_PAGE_URL
            
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print(f"使用Playwright访问主页: {podcast_url}")
            await page.goto(podcast_url)
            
            # 获取播客名称
            podcast_name = "未知播客"
            try:
                # 尝试从页面标题获取播客名称
                title_element = await page.query_selector('.detail-toolbox-title')
                if title_element:
                    podcast_name = await title_element.inner_text()
                else:
                    # 备用方案：从页面标题中提取
                    page_title = await page.title()
                    if " - " in page_title:
                        podcast_name = page_title.split(" - ")[0]
                    else:
                        podcast_name = page_title
            except Exception as e:
                print(f"获取播客名称时发生错误: {e}")
            
            if self.test_mode:
                print("测试模式已启用，等待页面加载...")
                await asyncio.sleep(5)  # 等待5秒让页面加载
            else:
                await page.wait_for_selector(".ep-item", timeout=60000)
                print("开始向下滚动，加载所有播客...")
                last_count = 0
                while True:
                    current_count = await page.locator(".ep-item").count()
                    print(f"当前加载了 {current_count} 个播客。")

                    if current_count == last_count:
                        print("已加载所有播客，停止滚动。")
                        break

                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                    await asyncio.sleep(2)

                    last_count = current_count

            episodes_data = await page.evaluate('''() => {
                const items = Array.from(document.querySelectorAll('.ep-item'));
                return items.map(item => {
                    const linkElement = item.querySelector('.ep-item-cover a');
                    const titleElement = item.querySelector('.ep-item-con-title');
                    const href = linkElement ? linkElement.getAttribute('href') : null;
                    const title = titleElement ? titleElement.textContent.trim() : '未知标题';
                    return { href, title };
                });
            }''')

            episodes_data = [ep for ep in episodes_data if ep['href']]

            # 如果是测试模式，只处理前10个（而不是限制为5个）
            if self.test_mode:
                episodes_data = episodes_data[:3]
                print(f"测试模式：只处理前 {len(episodes_data)} 个播客")

            all_episodes = []
            total_episodes = len(episodes_data)
            
            # 分批处理播客
            for i in range(0, total_episodes, batch_size):
                batch = episodes_data[i:i + batch_size]
                print(f"正在处理第 {i//batch_size + 1} 批播客，共 {(total_episodes-1)//batch_size + 1} 批")
                
                batch_episodes = []
                for ep_data in batch:
                    full_link = f"https://castbox.fm{ep_data['href']}"
                    title = ep_data['title']
                    print(f"--- 正在处理: {title} ---")

                    new_page = await browser.new_page()

                    try:
                        await new_page.goto(full_link)
                        await new_page.wait_for_selector(".trackinfo-titleBox", timeout=30000)

                        page_content = await new_page.content()
                        audio_url = await self.extract_audio_url(page_content)

                        if audio_url:
                            batch_episodes.append((title, audio_url))
                            print(f"✓ 成功找到音频URL: {audio_url}")
                        else:
                            print("× 警告: 未能从页面中找到音频URL。")
                            # 尝试打印页面的部分内容以帮助调试
                            print(f"页面内容预览: {page_content[:500]}...")

                    except Exception as e:
                        print(f"处理 '{title}' 时发生错误: {e}")
                    finally:
                        await new_page.close()
                
                # 将这一批的结果添加到总列表中
                all_episodes.extend(batch_episodes)
                # 添加一个小的延迟，避免过于频繁的请求
                await asyncio.sleep(1)

            await browser.close()
            return (podcast_name, all_episodes)

    def save_podcast_to_db(self, podcast_url, podcast_name):
        """
        保存播客信息到数据库
        
        Args:
            podcast_url (str): 播客URL
            podcast_name (str): 播客名称
            
        Returns:
            int: 播客ID
        """
        podcast = Podcast(
            name=podcast_name,
            url=podcast_url
        )
        return insert_or_update_podcast(podcast)