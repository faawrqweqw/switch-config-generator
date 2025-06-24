import os
import yaml
import ipaddress
from jinja2 import Template, Environment
from typing import Dict, List, Any, Optional
from flask import current_app

def cidr_to_netmask_filter(cidr_prefix):
    """将CIDR前缀长度转换为子网掩码"""
    try:
        prefix_len = int(cidr_prefix)
        network = ipaddress.IPv4Network(f"0.0.0.0/{prefix_len}")
        return str(network.netmask)
    except (ValueError, ipaddress.AddressValueError):
        return "255.255.255.0"  # 默认值

def ip_from_cidr_filter(cidr_ip):
    """从CIDR格式的IP地址中提取IP部分"""
    try:
        if '/' in cidr_ip:
            return cidr_ip.split('/')[0]
        return cidr_ip
    except:
        return cidr_ip

def netmask_from_cidr_filter(cidr_ip):
    """从CIDR格式的IP地址中提取子网掩码"""
    try:
        if '/' in cidr_ip:
            prefix_len = int(cidr_ip.split('/')[1])
            network = ipaddress.IPv4Network(f"0.0.0.0/{prefix_len}")
            return str(network.netmask)
        return "255.255.255.0"  # 默认值
    except:
        return "255.255.255.0"

class TemplateEngine:
    """配置模板引擎"""

    def __init__(self, template_dir=None, supported_vendors=None):
        self.templates = {}
        self.template_dir = template_dir
        self.supported_vendors = supported_vendors or ['huawei', 'h3c', 'cisco', 'ruijie']

        # 创建Jinja2环境并注册自定义过滤器
        self.jinja_env = Environment()
        self.jinja_env.filters['cidr_to_netmask'] = cidr_to_netmask_filter
        self.jinja_env.filters['ip_from_cidr'] = ip_from_cidr_filter
        self.jinja_env.filters['netmask_from_cidr'] = netmask_from_cidr_filter

        self.load_templates()

    def load_templates(self):
        """加载所有厂商的配置模板"""
        # 如果在应用上下文中，使用配置；否则使用默认值
        try:
            template_dir = self.template_dir or current_app.config.get('TEMPLATE_DIR')
            supported_vendors = self.supported_vendors or current_app.config.get('SUPPORTED_VENDORS', [])
        except RuntimeError:
            # 不在应用上下文中，使用默认值
            template_dir = self.template_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config_templates')
            supported_vendors = self.supported_vendors

        for vendor in supported_vendors:
            template_file = os.path.join(template_dir, f'{vendor}.yaml')
            if os.path.exists(template_file):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        self.templates[vendor] = yaml.safe_load(f)
                except Exception as e:
                    print(f"加载模板文件 {template_file} 失败: {e}")
    
    def get_config_types(self, vendor: str) -> List[str]:
        """获取指定厂商支持的配置类型"""
        if vendor not in self.templates:
            return []
        
        return list(self.templates[vendor].keys())
    
    def get_template_parameters(self, vendor: str, config_type: str) -> Dict[str, Any]:
        """获取模板参数定义"""
        if vendor not in self.templates:
            return {}
        
        if config_type not in self.templates[vendor]:
            return {}
        
        return self.templates[vendor][config_type].get('parameters', {})
    
    def generate_config(self, vendor: str, config_type: str, parameters: Dict[str, Any]) -> Optional[List[str]]:
        """生成配置命令"""
        if vendor not in self.templates:
            raise ValueError(f"不支持的厂商: {vendor}")
        
        if config_type not in self.templates[vendor]:
            raise ValueError(f"厂商 {vendor} 不支持配置类型: {config_type}")
        
        template_data = self.templates[vendor][config_type]
        commands_template = template_data.get('commands', [])
        
        if not commands_template:
            return []
        
        # 使用Jinja2渲染命令模板
        rendered_commands = []

        # 处理新的多行字符串格式和旧的列表格式
        if isinstance(commands_template, str):
            # 新的多行字符串格式
            try:
                template = self.jinja_env.from_string(commands_template)
                rendered_cmd = template.render(**parameters)
                if rendered_cmd.strip():
                    # 按行分割并清理空行，但保留缩进
                    lines = [line.rstrip() for line in rendered_cmd.split('\n') if line.strip()]
                    rendered_commands.extend(lines)
            except Exception as e:
                print(f"渲染命令模板失败: {e}")
                print(f"参数: {parameters}")
                raise e  # 重新抛出异常以便调试
        else:
            # 旧的列表格式
            for cmd_template in commands_template:
                try:
                    template = self.jinja_env.from_string(cmd_template)
                    rendered_cmd = template.render(**parameters)
                    if rendered_cmd.strip():  # 忽略空命令
                        rendered_commands.append(rendered_cmd.strip())
                except Exception as e:
                    print(f"渲染命令模板失败: {e}")
                    continue

        return rendered_commands
    
    def get_template_info(self, vendor: str, config_type: str) -> Dict[str, Any]:
        """获取模板信息"""
        if vendor not in self.templates:
            return {}
        
        if config_type not in self.templates[vendor]:
            return {}
        
        template_data = self.templates[vendor][config_type]
        return {
            'description': template_data.get('description', ''),
            'parameters': template_data.get('parameters', {}),
            'example': template_data.get('example', {})
        }

class ConfigGenerator:
    """配置生成器"""

    def __init__(self, template_dir=None, supported_vendors=None):
        self.template_engine = TemplateEngine(template_dir, supported_vendors)
    
    def generate(self, vendor: str, config_type: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成配置命令"""
        try:
            # 生成命令
            commands = self.template_engine.generate_config(vendor, config_type, form_data)
            
            if not commands:
                return {
                    'success': False,
                    'error': '生成的命令为空',
                    'commands': []
                }
            
            return {
                'success': True,
                'commands': commands,
                'vendor': vendor,
                'config_type': config_type,
                'parameters': form_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'commands': []
            }
    
    def get_supported_vendors(self) -> List[str]:
        """获取支持的厂商列表"""
        return list(self.template_engine.templates.keys())
    
    def get_supported_config_types(self, vendor: str) -> List[str]:
        """获取指定厂商支持的配置类型"""
        return self.template_engine.get_config_types(vendor)
    
    def get_template_parameters(self, vendor: str, config_type: str) -> Dict[str, Any]:
        """获取模板参数定义"""
        return self.template_engine.get_template_parameters(vendor, config_type)
    
    def get_template_info(self, vendor: str, config_type: str) -> Dict[str, Any]:
        """获取模板详细信息"""
        return self.template_engine.get_template_info(vendor, config_type)
