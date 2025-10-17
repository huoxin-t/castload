import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from models.podcast_models import Podcast, PodcastEpisode

# 数据库文件路径
DATABASE = 'podcasts.db'

def init_db():
    """初始化数据库并创建表"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建播客单集表（旧表，保留兼容性）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建播客表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            description TEXT,
            cover_image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建播客节目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            podcast_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            audio_url TEXT,
            description TEXT,
            duration TEXT,
            publish_date TIMESTAMP,
            index_number INTEGER DEFAULT 0,
            downloaded BOOLEAN DEFAULT FALSE,
            download_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (podcast_id) REFERENCES podcasts (id),
            UNIQUE(podcast_id, url)
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcast_episodes_podcast_id ON podcast_episodes (podcast_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcast_episodes_downloaded ON podcast_episodes (downloaded)')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn

# 播客相关操作
def insert_or_update_podcast(podcast: Podcast) -> int:
    """插入或更新播客信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查播客是否已存在
    cursor.execute('SELECT id FROM podcasts WHERE url = ?', (podcast.url,))
    existing = cursor.fetchone()
    
    if existing:
        # 更新现有播客
        cursor.execute('''
            UPDATE podcasts 
            SET name = ?, description = ?, cover_image_url = ?, updated_at = CURRENT_TIMESTAMP
            WHERE url = ?
        ''', (podcast.name, podcast.description, podcast.cover_image_url, podcast.url))
        podcast_id = existing['id']
    else:
        # 插入新播客
        cursor.execute('''
            INSERT INTO podcasts (name, url, description, cover_image_url)
            VALUES (?, ?, ?, ?)
        ''', (podcast.name, podcast.url, podcast.description, podcast.cover_image_url))
        podcast_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return podcast_id

def get_all_podcasts() -> List[Podcast]:
    """获取所有播客"""
    conn = get_db_connection()
    podcasts = conn.execute('SELECT * FROM podcasts ORDER BY name').fetchall()
    conn.close()
    
    return [Podcast(
        id=row['id'],
        name=row['name'],
        url=row['url'],
        description=row['description'],
        cover_image_url=row['cover_image_url'],
        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
    ) for row in podcasts]

def get_podcast_by_id(podcast_id: int) -> Optional[Podcast]:
    """根据ID获取播客"""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM podcasts WHERE id = ?', (podcast_id,)).fetchone()
    conn.close()
    
    if row:
        return Podcast(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            description=row['description'],
            cover_image_url=row['cover_image_url'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
    return None

def get_podcast_by_url(url: str) -> Optional[Podcast]:
    """根据URL获取播客"""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM podcasts WHERE url = ?', (url,)).fetchone()
    conn.close()
    
    if row:
        return Podcast(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            description=row['description'],
            cover_image_url=row['cover_image_url'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
    return None

# 节目相关操作
def insert_or_update_episode(episode: PodcastEpisode) -> int:
    """插入或更新节目信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查节目是否已存在
    cursor.execute('SELECT id FROM podcast_episodes WHERE podcast_id = ? AND url = ?', 
                   (episode.podcast_id, episode.url))
    existing = cursor.fetchone()
    
    if existing:
        # 更新现有节目
        cursor.execute('''
            UPDATE podcast_episodes 
            SET title = ?, audio_url = ?, description = ?, duration = ?, 
                publish_date = ?, index_number = ?, downloaded = ?, download_path = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE podcast_id = ? AND url = ?
        ''', (episode.title, episode.audio_url, episode.description, episode.duration,
              episode.publish_date, episode.index, episode.downloaded, episode.download_path,
              episode.podcast_id, episode.url))
        episode_id = existing['id']
    else:
        # 插入新节目
        cursor.execute('''
            INSERT INTO podcast_episodes 
            (podcast_id, title, url, audio_url, description, duration, publish_date, index_number, downloaded, download_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (episode.podcast_id, episode.title, episode.url, episode.audio_url, 
              episode.description, episode.duration, episode.publish_date, episode.index,
              episode.downloaded, episode.download_path))
        episode_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return episode_id

def get_episodes_by_podcast_id(podcast_id: int) -> List[PodcastEpisode]:
    """根据播客ID获取所有节目"""
    conn = get_db_connection()
    episodes = conn.execute('''
        SELECT * FROM podcast_episodes 
        WHERE podcast_id = ? 
        ORDER BY index_number DESC
    ''', (podcast_id,)).fetchall()
    conn.close()
    
    return [PodcastEpisode(
        id=row['id'],
        podcast_id=row['podcast_id'],
        title=row['title'],
        url=row['url'],
        audio_url=row['audio_url'],
        description=row['description'],
        duration=row['duration'],
        publish_date=datetime.fromisoformat(row['publish_date']) if row['publish_date'] else None,
        index=row['index_number'],
        downloaded=bool(row['downloaded']),
        download_path=row['download_path'],
        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
    ) for row in episodes]

def get_all_episodes_with_podcast_info() -> List[dict]:
    """获取所有节目及其播客信息"""
    conn = get_db_connection()
    episodes = conn.execute('''
        SELECT pe.*, p.name as podcast_name, p.url as podcast_url
        FROM podcast_episodes pe
        JOIN podcasts p ON pe.podcast_id = p.id
        ORDER BY p.name, pe.index_number DESC
    ''').fetchall()
    conn.close()
    
    return [dict(row) for row in episodes]

def check_episode_exists(podcast_id: int, url: str) -> bool:
    """检查节目是否已存在"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM podcast_episodes WHERE podcast_id = ? AND url = ?', (podcast_id, url))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# 旧的兼容性方法
def insert_episodes(episodes):
    """将播客数据插入数据库（保持向后兼容）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted_count = 0
    for episode in episodes:
        try:
            cursor.execute(
                'INSERT INTO episodes (title, url) VALUES (?, ?)',
                (episode['title'], episode['url'])
            )
            inserted_count += 1
        except sqlite3.IntegrityError:
            # 如果 URL 已存在，则忽略
            pass
    
    conn.commit()
    conn.close()
    return inserted_count

def get_all_episodes():
    """从数据库查询并返回所有播客数据（保持向后兼容）"""
    conn = get_db_connection()
    episodes = conn.execute('SELECT * FROM episodes').fetchall()
    conn.close()
    
    # 将查询结果转换为字典列表
    return [dict(episode) for episode in episodes]