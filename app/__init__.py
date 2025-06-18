import os
from flask import Flask
from config import Config

def create_app():
    """创建Flask应用实例"""
    # 获取项目根目录
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 指定模板和静态文件路径
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))

    app.config.from_object(Config)

    # 注册路由
    from app.routes import main
    app.register_blueprint(main)

    return app
