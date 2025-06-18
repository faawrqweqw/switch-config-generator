"""
工具函数模块
提供各种辅助功能
"""

import re
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional

def format_timestamp(timestamp: datetime = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除多余的空格和点
    filename = re.sub(r'\s+', '_', filename.strip())
    filename = filename.strip('.')
    
    # 确保文件名不为空
    if not filename:
        filename = 'config'
    
    return filename

def validate_yaml_syntax(yaml_content: str) -> tuple[bool, str]:
    """验证YAML语法"""
    try:
        yaml.safe_load(yaml_content)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)

def format_command_list(commands: List[str]) -> str:
    """格式化命令列表为字符串"""
    if not commands:
        return ""
    
    # 过滤空命令
    filtered_commands = [cmd.strip() for cmd in commands if cmd.strip()]
    
    return '\n'.join(filtered_commands)

def parse_interface_name(interface: str) -> Dict[str, Any]:
    """解析接口名称，提取接口类型和编号"""
    patterns = {
        'gigabit': r'^GigabitEthernet(\d+)/(\d+)(?:/(\d+))?$',
        'ethernet': r'^Ethernet(\d+)/(\d+)(?:/(\d+))?$',
        'fastethernet': r'^FastEthernet(\d+)/(\d+)(?:/(\d+))?$',
        'tengigabit': r'^TenGigabitEthernet(\d+)/(\d+)(?:/(\d+))?$',
    }
    
    for interface_type, pattern in patterns.items():
        match = re.match(pattern, interface, re.IGNORECASE)
        if match:
            groups = match.groups()
            result = {
                'type': interface_type,
                'slot': groups[0],
                'port': groups[1],
                'subport': groups[2] if len(groups) > 2 and groups[2] else None
            }
            return result
    
    return {'type': 'unknown', 'original': interface}

def validate_ip_range(start_ip: str, end_ip: str) -> bool:
    """验证IP地址范围"""
    try:
        import ipaddress
        start = ipaddress.ip_address(start_ip)
        end = ipaddress.ip_address(end_ip)
        return start <= end
    except ValueError:
        return False

def calculate_network_info(ip: str, mask: str) -> Dict[str, str]:
    """计算网络信息"""
    try:
        import ipaddress
        
        # 处理不同格式的子网掩码
        if '.' in mask:
            # 点分十进制格式
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        else:
            # CIDR格式
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        
        return {
            'network': str(network.network_address),
            'broadcast': str(network.broadcast_address),
            'netmask': str(network.netmask),
            'prefix_length': str(network.prefixlen),
            'host_count': str(network.num_addresses - 2)  # 减去网络地址和广播地址
        }
    except ValueError as e:
        return {'error': str(e)}

def generate_config_summary(vendor: str, config_type: str, parameters: Dict[str, Any]) -> str:
    """生成配置摘要"""
    summary_parts = []
    
    # 厂商信息
    vendor_names = {
        'huawei': '华为',
        'h3c': '新华三',
        'ruijie': '锐捷'
    }
    summary_parts.append(f"厂商: {vendor_names.get(vendor, vendor)}")
    
    # 配置类型
    config_names = {
        'vlan_management': 'VLAN管理',
        'interface_config': '接口配置',
        'port_aggregation': '端口聚合',
        'dhcp_service': 'DHCP服务',
        'static_route': '静态路由',
        'interface_ip': '接口IP配置'
    }
    summary_parts.append(f"配置类型: {config_names.get(config_type, config_type)}")
    
    # 关键参数
    key_params = []
    if 'vlan_id' in parameters:
        key_params.append(f"VLAN {parameters['vlan_id']}")
    if 'interface' in parameters:
        key_params.append(f"接口 {parameters['interface']}")
    if 'pool_name' in parameters:
        key_params.append(f"DHCP池 {parameters['pool_name']}")
    if 'destination' in parameters:
        key_params.append(f"目标 {parameters['destination']}")
    
    if key_params:
        summary_parts.append(f"关键参数: {', '.join(key_params)}")
    
    return ' | '.join(summary_parts)

def extract_vlan_list(vlan_string: str) -> List[int]:
    """从VLAN字符串中提取VLAN列表"""
    vlans = []
    
    if not vlan_string:
        return vlans
    
    # 分割逗号分隔的部分
    parts = vlan_string.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 处理范围，如 "10-20"
            try:
                start, end = part.split('-')
                start_vlan = int(start.strip())
                end_vlan = int(end.strip())
                vlans.extend(range(start_vlan, end_vlan + 1))
            except ValueError:
                continue
        else:
            # 处理单个VLAN
            try:
                vlans.append(int(part))
            except ValueError:
                continue
    
    return sorted(list(set(vlans)))  # 去重并排序

def format_vlan_list(vlans: List[int]) -> str:
    """将VLAN列表格式化为字符串"""
    if not vlans:
        return ""
    
    vlans = sorted(vlans)
    ranges = []
    start = vlans[0]
    end = vlans[0]
    
    for vlan in vlans[1:]:
        if vlan == end + 1:
            end = vlan
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = vlan
    
    # 添加最后一个范围
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")
    
    return ','.join(ranges)

def get_vendor_display_name(vendor: str) -> str:
    """获取厂商显示名称"""
    vendor_names = {
        'huawei': '华为 (Huawei)',
        'h3c': '新华三 (H3C)',
        'ruijie': '锐捷 (Ruijie)',
        'cisco': '思科 (Cisco)',
        'juniper': '瞻博 (Juniper)'
    }
    return vendor_names.get(vendor.lower(), vendor)

def parse_ospf_areas(areas_string: str) -> List[Dict[str, str]]:
    """解析OSPF区域和网络配置字符串

    Args:
        areas_string: 格式如 "0.0.0.0:192.168.1.0/24,0.0.0.1:192.168.2.0/24"
                     或 "0:192.168.1.0/24,1:192.168.2.0/24"

    Returns:
        List[Dict]: 包含area_id, network, wildcard的字典列表
    """
    area_network_list = []

    if not areas_string:
        return area_network_list

    # 分割逗号分隔的区域配置
    area_configs = areas_string.split(',')

    for area_config in area_configs:
        area_config = area_config.strip()
        if ':' not in area_config:
            continue

        try:
            # 分割区域ID和网络地址
            area_id, network_cidr = area_config.split(':', 1)
            area_id = area_id.strip()
            network_cidr = network_cidr.strip()

            # 解析网络地址和掩码
            if '/' in network_cidr:
                network_ip, prefix_len = network_cidr.split('/')
                prefix_len = int(prefix_len)

                # 计算反掩码（wildcard mask）
                import ipaddress
                network = ipaddress.IPv4Network(f"{network_ip}/{prefix_len}", strict=False)
                wildcard = str(ipaddress.IPv4Address(int(network.hostmask)))

                area_network_list.append({
                    'area_id': area_id,
                    'network': str(network.network_address),
                    'wildcard': wildcard
                })
            else:
                # 如果没有CIDR格式，假设是/24
                import ipaddress
                network = ipaddress.IPv4Network(f"{network_cidr}/24", strict=False)
                wildcard = str(ipaddress.IPv4Address(int(network.hostmask)))

                area_network_list.append({
                    'area_id': area_id,
                    'network': str(network.network_address),
                    'wildcard': wildcard
                })

        except (ValueError, IndexError) as e:
            print(f"解析OSPF区域配置失败: {area_config}, 错误: {e}")
            continue

    return area_network_list

def get_config_type_display_name(config_type: str) -> str:
    """获取配置类型显示名称"""
    config_names = {
        'vlan_management': 'VLAN管理',
        'interface_config': '接口配置',
        'port_aggregation': '端口聚合',
        'dhcp_service': 'DHCP服务',
        'static_route': '静态路由',
        'interface_ip': '接口IP配置',
        'acl_config': '访问控制列表',
        'qos_config': '服务质量配置'
    }
    return config_names.get(config_type, config_type)

def log_config_generation(vendor: str, config_type: str, parameters: Dict[str, Any], 
                         success: bool, error_msg: str = None) -> None:
    """记录配置生成日志"""
    log_entry = {
        'timestamp': format_timestamp(),
        'vendor': vendor,
        'config_type': config_type,
        'parameters': parameters,
        'success': success,
        'error': error_msg
    }
    
    # 这里可以实现实际的日志记录逻辑
    # 例如写入文件、数据库或发送到日志服务
    print(f"[CONFIG_LOG] {json.dumps(log_entry, ensure_ascii=False)}")

def clean_command_output(commands: List[str]) -> List[str]:
    """清理命令输出，移除空行和多余空格"""
    cleaned_commands = []
    
    for command in commands:
        # 移除首尾空格
        cleaned_command = command.strip()
        
        # 跳过空命令
        if not cleaned_command:
            continue
            
        # 移除多余的空格
        cleaned_command = re.sub(r'\s+', ' ', cleaned_command)
        
        cleaned_commands.append(cleaned_command)
    
    return cleaned_commands
