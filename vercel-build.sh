#!/usr/bin/env bash

# 显示当前工作目录和用户
echo "Current working directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Home directory: $HOME"

# 安装Python依赖
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install Python dependencies"
  exit 1
fi

# 显示Playwright版本信息
echo "Checking Playwright installation..."
python -m playwright --version

# 安装Playwright浏览器
echo "Installing Playwright browsers..."
python -m playwright install --with-deps chromium
if [ $? -ne 0 ]; then
  echo "Failed to install Playwright browsers"
  # 尝试另一种安装方法
  echo "Trying alternative installation method..."
  pip install playwright
  python -m playwright install chromium
fi

# 验证安装
echo "Verifying Playwright installation..."
python -c "import playwright; print('Playwright imported successfully')"
python -c "from playwright.sync_api import sync_playwright; print('Playwright sync API imported successfully')"

# 显示缓存目录内容
echo "Checking Playwright cache directory..."
ls -la $HOME/.cache/ms-playwright/ 2>/dev/null || echo "Cache directory not found"

# 构建完成
echo "Build completed successfully!"