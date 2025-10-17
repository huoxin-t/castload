from flask import Flask
from flask_cors import CORS
from controllers.main_controller import MainController
import os

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

# 初始化 Flask 应用，指定模板和静态文件目录
app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))
CORS(app)

# 初始化主控制器
controller = MainController(app)

# 初始化数据库
controller.init_db()

if __name__ == '__main__':
    # 启动 Flask 应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)