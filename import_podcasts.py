import os
from database import init_db, insert_episodes

def read_podcast_links(file_path):
    """从文本文件中读取播客标题和链接"""
    episodes = []
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return episodes
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                # 分割标题和链接
                parts = line.split('\t')
                if len(parts) == 2:
                    title, url = parts
                    episodes.append({'title': title, 'url': url})
                else:
                    print(f"跳过无效行: {line}")
    return episodes

def main():
    # 初始化数据库
    init_db()
    
    # 读取播客链接
    file_path = 'podcast_links.txt'
    episodes = read_podcast_links(file_path)
    
    if not episodes:
        print("没有找到有效的播客数据。")
        return
    
    # 插入数据到数据库
    inserted_count = insert_episodes(episodes)
    print(f"成功插入 {inserted_count} 条播客数据到数据库。")

if __name__ == '__main__':
    main()