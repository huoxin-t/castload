#!/usr/bin/env python3
"""
手动安装Playwright浏览器的脚本
"""

import os
import sys
import subprocess
import shutil

def run_command(cmd):
    """运行命令并返回结果"""
    print(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(e.stderr)
        return None

def main():
    print("Starting manual Playwright installation...")
    
    # 设置环境变量
    home_dir = os.path.expanduser("~")
    playwright_cache_dir = os.path.join(home_dir, ".cache", "ms-playwright")
    os.makedirs(playwright_cache_dir, exist_ok=True)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = playwright_cache_dir
    
    print(f"Playwright cache directory: {playwright_cache_dir}")
    
    # 安装playwright包
    print("Installing playwright package...")
    run_command("pip install playwright")
    
    # 安装浏览器
    print("Installing Chromium browser...")
    run_command("python -m playwright install chromium")
    
    # 验证安装
    print("Verifying installation...")
    try:
        from playwright.sync_api import sync_playwright
        print("Playwright imported successfully!")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            print("Chromium browser launched successfully!")
            browser.close()
    except Exception as e:
        print(f"Error verifying installation: {e}")
        sys.exit(1)
    
    print("Manual Playwright installation completed successfully!")

if __name__ == "__main__":
    main()