import os

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 模板文件路径
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_templates')
    
    # 支持的厂商列表
    SUPPORTED_VENDORS = ['huawei', 'h3c', 'ruijie', 'cisco']
    
    # 支持的配置类型
    SUPPORTED_CONFIG_TYPES = [
        'vlan_management',
        'interface_config', 
        'port_aggregation',
        'dhcp_service',
        'static_route',
        'interface_ip'
    ]
    
    # 调试模式
    DEBUG = True
