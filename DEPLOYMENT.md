# 部署说明

## Playwright浏览器安装问题解决

在部署到Heroku或其他云平台时，您可能会遇到以下错误：

```
Executable doesn't exist at /home/sbx_user1051/.cache/ms-playwright/chromium-1091/chrome-linux/chrome
╔════════════════════════════════════════════════════════════╗
║ Looks like Playwright was just installed or updated.     ║
║ Please run the following command to download new browsers: ║
║                                                          ║
║ playwright install                                       ║
║                                                          ║
║ <3 Playwright Team                                       ║
╚════════════════════════════════════════════════════════════╝
```

### 解决方案

1. **使用自定义Buildpack**（推荐用于Heroku）：
   在Heroku中设置以下buildpacks：
   ```
   https://github.com/heroku/heroku-buildpack-python
   https://github.com/mxschmitt/heroku-buildpack-playwright
   ```

2. **在应用启动时自动安装**：
   项目中已包含postinstall.py脚本，会在部署时自动安装Playwright浏览器。

3. **手动安装**：
   如果上述方法不起作用，可以在部署环境中手动运行：
   ```
   playwright install chromium
   ```

### 不同部署平台的解决方案

#### Heroku
1. 添加官方Playwright buildpack：
   ```
   heroku buildpacks:set https://github.com/mxschmitt/heroku-buildpack-playwright
   ```
2. 确保Python buildpack也在列表中：
   ```
   heroku buildpacks:add --index 1 heroku/python
   ```

#### Railway/Vercel
1. 在项目根目录创建`.railway/build.sh`或相应的构建脚本：
   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

#### 其他平台
1. 在应用启动前运行postinstall脚本：
   ```
   python postinstall.py
   ```

### 注意事项

- Playwright浏览器安装需要较多磁盘空间和时间
- 确保部署环境有足够的资源来安装和运行浏览器
- 在某些受限环境中可能需要特殊配置
- 如果不需要爬取功能，可以考虑移除Playwright依赖以减少部署复杂性