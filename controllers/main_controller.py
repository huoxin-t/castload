
from flask import Flask, jsonify, request, render_template
from core.podcast_extractor import PodcastExtractor
from core.downloader import PodcastDownloader
from models.download_status import DownloadStatus
from database import get_all_episodes_with_podcast_info
from models.podcast_models import PodcastEpisode
from database import insert_or_update_episode
import asyncio
import json
import os
import sqlite3

class MainController:
    def __init__(self, app):
        self.app = app
        self.register_routes()
    
    def init_db(self):
        """初始化数据库并创建表"""
        conn = sqlite3.connect('podcasts.db')
        cursor = conn.cursor()
        
        # 创建播客单集表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_db_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect('podcasts.db')
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        return conn
    
    def register_routes(self):
        @self.app.route('/')
        def index():
            """渲染主页模板"""
            return render_template('index.html')
        
        @self.app.route('/advanced.html')
        def advanced():
            """渲染高级功能页面"""
            return render_template('advanced.html')
        
        @self.app.route('/api/load_episodes', methods=['POST'])
        def load_episodes():
            try:
                # 获取请求数据
                data = request.json
                url = data.get('url', '')
                
                if not url:
                    return jsonify({"error": "URL不能为空"}), 400
                
                # 创建播客提取器实例
                extractor = PodcastExtractor()
                
                # 获取播客列表
                import asyncio
                podcast_name, episodes = asyncio.run(extractor.get_episodes_list(url))
                
                # 保存到文件
                extractor.save_episodes_to_file(episodes)
                
                # 保存播客信息到数据库
                podcast_id = extractor.save_podcast_to_db(url, podcast_name)
                
                # 保存每个节目到数据库
                for title, audio_url in episodes:
                    episode = PodcastEpisode(
                        title=title,
                        url=audio_url,
                        podcast_id=podcast_id
                    )
                    insert_or_update_episode(episode)
                
                return jsonify({
                    "message": f"成功加载 {len(episodes)} 个播客",
                    "episodes": episodes
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/download_episodes', methods=['POST'])
        def download_episodes():
            try:
                # 创建播客提取器实例
                extractor = PodcastExtractor()
                
                # 从文件加载播客列表
                episodes = extractor.load_episodes_from_file()
                
                if not episodes:
                    return jsonify({"error": "没有找到播客列表"}), 400
                
                # 使用下载器下载播客
                downloader = PodcastDownloader()
                results = downloader.download_episodes(episodes)
                
                return jsonify({
                    "message": "下载任务完成",
                    "results": results
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/download_status', methods=['GET'])
        def download_status():
            try:
                # 获取下载状态
                status_tracker = DownloadStatus()
                status = status_tracker.get_all_status()
                
                return jsonify({
                    "status": status
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/data', methods=['GET'])
        def get_podcast_data():
            """API 接口：从数据库查询并返回所有播客数据（以 JSON 格式）"""
            try:
                conn = self.get_db_connection()
                episodes = conn.execute('SELECT * FROM episodes').fetchall()
                conn.close()
                
                # 将查询结果转换为字典列表
                episodes_list = [dict(episode) for episode in episodes]
                return jsonify(episodes_list)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/config', methods=['POST'])
        def save_config():
            """API 接口：保存配置信息"""
            try:
                # 获取请求数据
                data = request.json
                
                # 这里应该保存配置到文件或数据库
                # 为了简化，我们只是返回成功响应
                return jsonify({
                    'success': True,
                    'message': '配置已保存'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/load-episodes', methods=['POST'])
        def load_episodes_advanced():
            """API 接口：加载播客列表（高级功能）"""
            try:
                # 获取请求数据
                data = request.json
                url = data.get('podcast_url', '')
                
                if not url:
                    return jsonify({
                        'success': False,
                        'error': 'URL不能为空'
                    }), 400
                
                # 创建播客提取器实例
                extractor = PodcastExtractor()
                
                # 获取播客列表
                import asyncio
                podcast_name, episodes = asyncio.run(extractor.get_episodes_list(url))
                
                # 保存到文件
                extractor.save_episodes_to_file(episodes)
                
                # 保存播客信息到数据库
                podcast_id = extractor.save_podcast_to_db(url, podcast_name)
                
                # 保存每个节目到数据库
                for title, audio_url in episodes:
                    episode = PodcastEpisode(
                        title=title,
                        url=audio_url,
                        podcast_id=podcast_id
                    )
                    insert_or_update_episode(episode)
                
                return jsonify({
                    'success': True,
                    'message': f"成功加载 {len(episodes)} 个播客",
                    'episodes': episodes
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/download', methods=['POST'])
        def download_episodes_advanced():
            """API 接口：下载选中的播客"""
            try:
                # 获取请求数据
                data = request.json
                episodes = data.get('episodes', [])
                max_workers = data.get('max_workers', 5)
                download_options = data.get('download_options', {})
                
                if not episodes:
                    return jsonify({
                        'success': False,
                        'error': '没有选择要下载的播客'
                    }), 400
                
                # 使用下载器下载播客
                downloader = PodcastDownloader()
                results = downloader.download_episodes(episodes)
                
                return jsonify({
                    'success': True,
                    'message': f"成功添加 {len(results)} 个播客到下载队列",
                    'results': results
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/podcast-history', methods=['GET'])
        def get_podcast_history():
            """API 接口：获取按播客分类的下载历史"""
            try:
                # 获取所有节目及其播客信息
                all_episodes = get_all_episodes_with_podcast_info()
                
                # 按播客分组
                podcast_groups = {}
                for episode in all_episodes:
                    podcast_id = episode['podcast_id']
                    if podcast_id not in podcast_groups:
                        podcast_groups[podcast_id] = {
                            'podcast_id': podcast_id,
                            'podcast_name': episode['podcast_name'],
                            'podcast_url': episode['podcast_url'],
                            'episodes': []
                        }
                    podcast_groups[podcast_id]['episodes'].append(episode)
                
                # 转换为列表格式
                history = list(podcast_groups.values())
                
                return jsonify({
                    'success': True,
                    'history': history
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/download-episode', methods=['POST'])
        def download_single_episode():
            """API 接口：下载单个播客节目"""
            try:
                # 获取请求数据
                data = request.json
                title = data.get('title', '')
                url = data.get('url', '')
                episode_id = data.get('episode_id', None)
                
                if not title or not url:
                    return jsonify({
                        'success': False,
                        'error': '标题和URL不能为空'
                    }), 400
                
                # 使用下载器下载单个播客（强制下载，不检查状态）
                downloader = PodcastDownloader()
                episode_info = (title, url)
                result = downloader.download_episode(episode_info, force_download=True)
                
                # 如果提供了episode_id，则更新数据库中的下载状态
                if episode_id:
                    try:
                        # 首先获取现有的节目信息以获得podcast_id
                        conn = self.get_db_connection()
                        existing_episode = conn.execute(
                            'SELECT podcast_id FROM podcast_episodes WHERE id = ?', 
                            (episode_id,)
                        ).fetchone()
                        conn.close()
                        
                        if existing_episode:
                            # 更新数据库中的下载状态
                            episode = PodcastEpisode(
                                id=episode_id,
                                podcast_id=existing_episode['podcast_id'],
                                title=title,
                                audio_url=url,
                                url=url,  # 也设置url字段
                                downloaded=True  # 标记为已下载
                            )
                            insert_or_update_episode(episode)
                    except Exception as db_error:
                        print(f"更新数据库时出错: {db_error}")
                
                return jsonify({
                    'success': True,
                    'message': result
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/history.html')
        def history():
            """渲染历史记录页面"""
            return render_template('history.html')
