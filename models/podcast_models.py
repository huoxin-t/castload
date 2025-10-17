from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Podcast:
    """播客数据模型"""
    id: Optional[int] = None
    name: str = ""
    url: str = ""
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'cover_image_url': self.cover_image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            url=data.get('url', ''),
            description=data.get('description'),
            cover_image_url=data.get('cover_image_url'),
            created_at=created_at,
            updated_at=updated_at
        )

@dataclass
class PodcastEpisode:
    """播客节目数据模型"""
    id: Optional[int] = None
    podcast_id: int = 0
    title: str = ""
    url: str = ""
    audio_url: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    publish_date: Optional[datetime] = None
    index: int = 0
    downloaded: bool = False
    download_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'podcast_id': self.podcast_id,
            'title': self.title,
            'url': self.url,
            'audio_url': self.audio_url,
            'description': self.description,
            'duration': self.duration,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'index': self.index,
            'downloaded': self.downloaded,
            'download_path': self.download_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        publish_date = data.get('publish_date')
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        if isinstance(publish_date, str):
            publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
        return cls(
            id=data.get('id'),
            podcast_id=data.get('podcast_id', 0),
            title=data.get('title', ''),
            url=data.get('url', ''),
            audio_url=data.get('audio_url'),
            description=data.get('description'),
            duration=data.get('duration'),
            publish_date=publish_date,
            index=data.get('index', 0),
            downloaded=data.get('downloaded', False),
            download_path=data.get('download_path'),
            created_at=created_at,
            updated_at=updated_at
        )