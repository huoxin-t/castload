
from dataclasses import dataclass
from typing import Optional

@dataclass
class PodcastEpisode:
    """播客剧集数据模型"""
    title: str
    url: str
    index: int
    duration: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'title': self.title,
            'url': self.url,
            'index': self.index,
            'duration': self.duration,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            title=data['title'],
            url=data['url'],
            index=data['index'],
            duration=data.get('duration'),
            description=data.get('description')
        )
