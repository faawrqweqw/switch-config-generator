#!/usr/bin/env python3
"""
交换机配置命令生成Web平台
启动文件
"""

from app import create_app

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    # 开发模式运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
