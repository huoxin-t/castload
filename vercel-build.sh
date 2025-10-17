#!/usr/bin/env bash

# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
python -m playwright install chromium

# 构建完成
echo "Build completed successfully!"