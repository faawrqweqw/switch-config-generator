import os
import json
import re
import ipaddress
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from jinja2 import Template

main = Blueprint('main', __name__)

def load_template(vendor, config_type):
    """加载指定厂商和配置类型的模板"""
    template_path = os.path.join('templates', vendor, f'{config_type}.json')
    if not os.path.exists(template_path):
        return None

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('template')
    except Exception as e:
        print(f"加载模板失败: {e}")
        return None

def expand_ports(port_string):
    """
    增强版端口展开函数，支持复杂的不连续端口输入

    支持的格式：
    - 单个端口：GigabitEthernet0/0/1
    - 简单范围：GigabitEthernet0/0/1-4
    - 复杂范围：GigabitEthernet0/0/1-4,0/0/8-10
    - 不连续端口：GigabitEthernet0/0/1,0/0/4,0/0/5-10
    - 混合格式：GigabitEthernet0/0/1,0/0/4,0/0/5-10,0/0/15
    - 多层级：GigabitEthernet0/0/1-4,1/0/1-2
    """
    ports = []

    if not port_string or not port_string.strip():
        return ports

    # 处理逗号分隔的多个端口或范围
    parts = [part.strip() for part in port_string.split(',') if part.strip()]

    for part in parts:
        expanded_part = _expand_single_port_part(part)
        ports.extend(expanded_part)

    # 去重并保持顺序
    seen = set()
    unique_ports = []
    for port in ports:
        if port not in seen:
            seen.add(port)
            unique_ports.append(port)

    return unique_ports

def _expand_single_port_part(part):
    """
    展开单个端口部分
    支持多种格式的端口范围
    """
    ports = []

    if '-' in part:
        # 处理范围格式
        ports.extend(_expand_port_range(part))
    else:
        # 单个端口
        ports.append(part)

    return ports

def _expand_port_range(range_part):
    """
    展开端口范围，支持多种复杂格式

    支持的范围格式：
    1. GigabitEthernet0/0/1-4 (简单范围)
    2. GigabitEthernet0/0/1-4 (最后一位数字范围)
    3. GigabitEthernet0/1/1-0/2/4 (跨槽位范围)
    4. 10GE1/0/1-1/0/4 (华为10GE格式)
    """
    ports = []

    # 尝试匹配不同的范围格式
    range_patterns = [
        # 格式1: 简单数字范围 (如: GigabitEthernet0/0/1-4)
        r'^(.+?)(\d+)-(\d+)$',

        # 格式2: 复杂路径范围 (如: GigabitEthernet0/0/1-0/0/4)
        r'^(.+?)(\d+/\d+/\d+)-(\d+/\d+/\d+)$',

        # 格式3: 槽位范围 (如: GigabitEthernet0/1-0/4)
        r'^(.+?)(\d+/\d+)-(\d+/\d+)$',

        # 格式4: 华为简化格式 (如: 10GE1/0/1-4)
        r'^(.+?)(\d+/\d+/\d+)-(\d+)$'
    ]

    for pattern in range_patterns:
        match = re.match(pattern, range_part)
        if match:
            if pattern == range_patterns[0]:  # 简单数字范围
                ports.extend(_expand_simple_number_range(match))
            elif pattern == range_patterns[1]:  # 复杂路径范围
                ports.extend(_expand_complex_path_range(match))
            elif pattern == range_patterns[2]:  # 槽位范围
                ports.extend(_expand_slot_range(match))
            elif pattern == range_patterns[3]:  # 华为简化格式
                ports.extend(_expand_huawei_simplified_range(match))
            break
    else:
        # 如果没有匹配到任何模式，直接返回原字符串
        ports.append(range_part)

    return ports

def _expand_simple_number_range(match):
    """展开简单数字范围 (如: GigabitEthernet0/0/1-4)"""
    prefix, start, end = match.groups()
    ports = []

    try:
        start_num = int(start)
        end_num = int(end)

        if start_num <= end_num:
            for i in range(start_num, end_num + 1):
                ports.append(f"{prefix}{i}")
        else:
            # 如果起始大于结束，交换顺序
            for i in range(end_num, start_num + 1):
                ports.append(f"{prefix}{i}")
    except ValueError:
        # 如果转换失败，返回原字符串
        ports.append(f"{prefix}{start}-{end}")

    return ports

def _expand_complex_path_range(match):
    """展开复杂路径范围 (如: GigabitEthernet0/0/1-0/0/4)"""
    prefix, start_path, end_path = match.groups()
    ports = []

    try:
        # 解析起始和结束路径
        start_parts = [int(x) for x in start_path.split('/')]
        end_parts = [int(x) for x in end_path.split('/')]

        if len(start_parts) == len(end_parts) == 3:
            # 三层路径格式 (slot/subslot/port)
            start_slot, start_subslot, start_port = start_parts
            end_slot, end_subslot, end_port = end_parts

            # 生成范围内的所有端口
            for slot in range(start_slot, end_slot + 1):
                if slot == start_slot and slot == end_slot:
                    # 同一槽位
                    for subslot in range(start_subslot, end_subslot + 1):
                        if subslot == start_subslot and subslot == end_subslot:
                            # 同一子槽位
                            for port in range(start_port, end_port + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                        elif subslot == start_subslot:
                            # 起始子槽位
                            for port in range(start_port, 48 + 1):  # 假设最大48端口
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                        elif subslot == end_subslot:
                            # 结束子槽位
                            for port in range(1, end_port + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                        else:
                            # 中间子槽位
                            for port in range(1, 48 + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                elif slot == start_slot:
                    # 起始槽位
                    for subslot in range(start_subslot, 8 + 1):  # 假设最大8子槽位
                        if subslot == start_subslot:
                            for port in range(start_port, 48 + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                        else:
                            for port in range(1, 48 + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                elif slot == end_slot:
                    # 结束槽位
                    for subslot in range(0, end_subslot + 1):
                        if subslot == end_subslot:
                            for port in range(1, end_port + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                        else:
                            for port in range(1, 48 + 1):
                                ports.append(f"{prefix}{slot}/{subslot}/{port}")
                else:
                    # 中间槽位
                    for subslot in range(0, 8 + 1):
                        for port in range(1, 48 + 1):
                            ports.append(f"{prefix}{slot}/{subslot}/{port}")

    except (ValueError, IndexError):
        # 如果解析失败，返回原字符串
        ports.append(f"{prefix}{start_path}-{end_path}")

    return ports

def _expand_slot_range(match):
    """展开槽位范围 (如: GigabitEthernet0/1-0/4)"""
    prefix, start_path, end_path = match.groups()
    ports = []

    try:
        start_parts = [int(x) for x in start_path.split('/')]
        end_parts = [int(x) for x in end_path.split('/')]

        if len(start_parts) == len(end_parts) == 2:
            start_slot, start_port = start_parts
            end_slot, end_port = end_parts

            for slot in range(start_slot, end_slot + 1):
                if slot == start_slot and slot == end_slot:
                    # 同一槽位
                    for port in range(start_port, end_port + 1):
                        ports.append(f"{prefix}{slot}/{port}")
                elif slot == start_slot:
                    # 起始槽位
                    for port in range(start_port, 48 + 1):
                        ports.append(f"{prefix}{slot}/{port}")
                elif slot == end_slot:
                    # 结束槽位
                    for port in range(1, end_port + 1):
                        ports.append(f"{prefix}{slot}/{port}")
                else:
                    # 中间槽位
                    for port in range(1, 48 + 1):
                        ports.append(f"{prefix}{slot}/{port}")

    except (ValueError, IndexError):
        ports.append(f"{prefix}{start_path}-{end_path}")

    return ports

def _expand_huawei_simplified_range(match):
    """展开华为简化格式 (如: 10GE1/0/1-4)"""
    prefix, start_path, end_num = match.groups()
    ports = []

    try:
        # 解析起始路径
        start_parts = [int(x) for x in start_path.split('/')]
        end_number = int(end_num)

        if len(start_parts) == 3:
            slot, subslot, start_port = start_parts

            # 从起始端口到结束端口
            for port in range(start_port, end_number + 1):
                ports.append(f"{prefix}{slot}/{subslot}/{port}")

    except (ValueError, IndexError):
        ports.append(f"{prefix}{start_path}-{end_num}")

    return ports

def cidr_to_netmask(cidr):
    """将CIDR格式转换为网络地址和子网掩码"""
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
        return str(network.network_address), str(network.netmask)
    except ValueError:
        return cidr, "255.255.255.0"  # 默认值

def cidr_to_ip_netmask(cidr):
    """将CIDR格式转换为IP地址和子网掩码（保留原始IP地址）"""
    try:
        if '/' in cidr:
            ip_str, prefix_len = cidr.split('/')
            network = ipaddress.IPv4Network(f"0.0.0.0/{prefix_len}", strict=False)
            return ip_str, str(network.netmask)
        else:
            return cidr, "255.255.255.0"  # 默认值
    except ValueError:
        return cidr, "255.255.255.0"  # 默认值

def parse_ospf_areas(areas_string):
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
                network = ipaddress.IPv4Network(f"{network_ip}/{prefix_len}", strict=False)
                wildcard = str(ipaddress.IPv4Address(int(network.hostmask)))

                area_network_list.append({
                    'area_id': area_id,
                    'network': str(network.network_address),
                    'wildcard': wildcard
                })
            else:
                # 如果没有CIDR格式，假设是/24
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

@main.route('/')
def index():
    """主页面"""
    # 获取支持的厂商列表
    generator = get_config_generator()
    vendors = generator.get_supported_vendors()
    return render_template('index.html', vendors=vendors)

@main.route('/api/config_types/<vendor>')
def get_config_types(vendor):
    """获取指定厂商支持的配置类型"""
    try:
        generator = get_config_generator()
        config_types = generator.get_supported_config_types(vendor)

        # 配置类型的中文名称映射
        type_names = {
            'vlan_complete_config': 'VLAN一体化配置',
            'port_aggregation': '端口聚合',
            'dhcp_service': 'DHCP服务',
            'static_route': '静态路由',
            'interface_ip': '接口IP配置',
            'stp_config': 'STP配置',
            'ospf_config': 'OSPF配置'
        }

        result = []
        for config_type in config_types:
            result.append({
                'value': config_type,
                'name': type_names.get(config_type, config_type)
            })

        return jsonify({
            'success': True,
            'config_types': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@main.route('/api/template_info/<vendor>/<config_type>')
def get_template_info(vendor, config_type):
    """获取模板参数信息"""
    try:
        generator = get_config_generator()
        template_info = generator.get_template_info(vendor, config_type)
        return jsonify({
            'success': True,
            'template_info': template_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_config_generator():
    """获取配置生成器实例"""
    global config_generator
    if config_generator is None:
        from app.template_engine import ConfigGenerator
        config_generator = ConfigGenerator(
            template_dir=current_app.config.get('TEMPLATE_DIR'),
            supported_vendors=current_app.config.get('SUPPORTED_VENDORS')
        )
    return config_generator

# 全局变量，延迟初始化
config_generator = None

def format_vlan_range(vlan_str):
    """格式化VLAN范围，如 10,20,30-50 -> 10 20 30 to 50"""
    parts = []
    for part in vlan_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            parts.append(f"{start.strip()} to {end.strip()}")
        else:
            parts.append(part)
    return ' '.join(parts)

def parse_vlan_list(vlan_str):
    """解析VLAN列表为单个VLAN ID列表"""
    vlans = []
    for part in vlan_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            vlans.extend(range(start, end + 1))
        else:
            vlans.append(int(part))
    return vlans

def process_excluded_addresses(excluded_str):
    """处理DHCP排除地址"""
    excluded_cmds = []
    if excluded_str:
        for part in excluded_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                excluded_cmds.append((start.strip(), end.strip()))
            elif part:
                excluded_cmds.append((part.strip(), None))
    return excluded_cmds
@main.route('/generate', methods=['POST'])
def generate_config():
    """生成配置命令（增强版，支持智能输入处理）"""
    try:
        # 获取表单数据
        vendor = request.form.get('vendor')
        config_type = request.form.get('config_type')

        if not vendor or not config_type:
            flash('请选择厂商和配置类型', 'error')
            return redirect(url_for('main.index'))

        # 构建参数字典，包含智能处理逻辑
        form_data = {}
        for key, value in request.form.items():
            if key not in ['vendor', 'config_type'] and value.strip():
                form_data[key] = value.strip()

        # 智能处理不同配置类型的参数
        processed_params = process_smart_inputs(config_type, vendor, form_data)

        # 验证表单数据
        from app.validators import validate_form_data
        is_valid, errors = validate_form_data(config_type, processed_params)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('main.index'))

        # 生成配置
        generator = get_config_generator()
        result = generator.generate(vendor, config_type, processed_params)

        if result['success']:
            return render_template('result.html',
                                 commands=result['commands'],
                                 vendor=vendor,
                                 config_type=config_type,
                                 parameters=processed_params)
        else:
            flash(f'生成配置失败: {result["error"]}', 'error')
            return redirect(url_for('main.index'))

    except Exception as e:
        flash(f'系统错误: {str(e)}', 'error')
        return redirect(url_for('main.index'))

def process_smart_inputs(config_type, vendor, form_data):
    """智能处理用户输入，支持范围展开、批量处理等"""
    processed = dict(form_data)

    # 处理接口配置 - 支持端口范围
    if config_type == 'interface_config':
        if 'interface' in form_data:
            # 支持端口范围输入，如 GigabitEthernet0/1-4
            processed['port_list'] = expand_ports(form_data['interface'])

        # 处理trunk模式的VLAN列表
        if form_data.get('port_mode') == 'trunk' and 'allowed_vlans' in form_data:
            processed['trunk_vlans'] = format_vlan_range(form_data['allowed_vlans'])

    # 处理VLAN管理 - 支持批量创建
    elif config_type == 'vlan_management':
        vlan_id = form_data.get('vlan_id', '')
        if ',' in vlan_id or '-' in vlan_id:
            # 批量创建VLAN
            processed['is_batch'] = True
            processed['vlan_list'] = parse_vlan_list(vlan_id)

            # 根据厂商格式化批量VLAN字符串
            if vendor == 'huawei' or vendor == 'h3c':
                processed['vlan_batch'] = format_vlan_range(vlan_id)
            else:  # cisco等
                processed['vlan_batch'] = vlan_id.replace(' ', '')
        else:
            processed['is_batch'] = False

    # 处理VLAN一体化配置
    elif config_type == 'vlan_complete_config':
        # 处理VLAN创建
        vlan_id = form_data.get('vlan_id', '')
        if ',' in vlan_id or '-' in vlan_id:
            processed['is_batch'] = True
            processed['vlan_list'] = parse_vlan_list(vlan_id)
            if vendor == 'huawei' or vendor == 'h3c':
                processed['vlan_batch'] = format_vlan_range(vlan_id)
            else:
                processed['vlan_batch'] = vlan_id.replace(' ', '')
        else:
            processed['is_batch'] = False

        # 处理接口配置
        if 'interface' in form_data:
            processed['port_list'] = expand_ports(form_data['interface'])

        # 处理trunk模式的VLAN列表
        if form_data.get('port_mode') == 'trunk' and 'allowed_vlans' in form_data:
            processed['trunk_vlans'] = format_vlan_range(form_data['allowed_vlans'])

        # 处理VLAN接口IP配置
        if form_data.get('configure_vlan_ip') and 'vlan_ip_address' in form_data:
            vlan_ip_addr, vlan_subnet_mask = cidr_to_ip_netmask(form_data['vlan_ip_address'])
            processed['vlan_ip_address'] = vlan_ip_addr
            processed['vlan_subnet_mask'] = vlan_subnet_mask

    # 处理端口聚合 - 支持成员端口范围
    elif config_type == 'port_aggregation':
        if 'interfaces' in form_data:
            # 展开成员端口范围
            processed['member_port_list'] = expand_ports(form_data['interfaces'])

        # 根据厂商设置聚合接口名称
        lag_id = form_data.get('lag_id', '1')
        if vendor == 'cisco':
            processed['lag_interface'] = f'Port-channel{lag_id}'
        elif vendor == 'h3c':
            processed['lag_interface'] = f'Bridge-Aggregation{lag_id}'
        elif vendor == 'huawei':
            processed['lag_interface'] = f'Eth-Trunk{lag_id}'
        elif vendor == 'ruijie':
            processed['lag_interface'] = f'aggregateport{lag_id}'

    # 处理DHCP服务 - 支持排除地址范围和华为双模式
    elif config_type == 'dhcp_service':
        # 处理网络地址格式
        if 'network' in form_data:
            network_addr, netmask = cidr_to_netmask(form_data['network'])
            processed['network'] = network_addr
            if 'mask' not in form_data or not form_data['mask']:
                processed['mask'] = netmask

        # 处理排除地址
        if 'excluded_addresses' in form_data:
            processed['excluded_cmds'] = process_excluded_addresses(form_data['excluded_addresses'])

        # 处理租期时间 - 支持"天 小时 分钟"格式
        if 'lease_time' in form_data and form_data['lease_time']:
            lease_time_str = form_data['lease_time'].strip()
            if lease_time_str:
                # 验证格式：天 小时 分钟（如：1 0 0）
                parts = lease_time_str.split()
                if len(parts) == 3:
                    try:
                        days = int(parts[0])
                        hours = int(parts[1])
                        minutes = int(parts[2])

                        # 验证范围
                        if 0 <= days <= 365 and 0 <= hours <= 23 and 0 <= minutes <= 59:
                            processed['lease_time'] = lease_time_str
                        else:
                            raise ValueError('租期时间范围不正确')
                    except ValueError:
                        # 如果格式不正确，使用默认值
                        processed['lease_time'] = "1 0 0"  # 默认1天
                else:
                    # 如果格式不正确，使用默认值
                    processed['lease_time'] = "1 0 0"  # 默认1天



        # 华为厂商特殊处理：验证DHCP类型和必要参数
        if vendor == 'huawei' and config_type == 'dhcp_service':
            dhcp_type = form_data.get('dhcp_type', 'global')
            processed['dhcp_type'] = dhcp_type

            # 全局地址池模式需要池名称
            if dhcp_type == 'global' and not form_data.get('pool_name'):
                raise ValueError('全局地址池模式必须指定池名称')

            # 接口地址池模式需要VLAN接口
            if dhcp_type == 'interface' and not form_data.get('vlanif'):
                raise ValueError('接口地址池模式必须指定VLAN接口')

            # 处理接口地址池模式的接口IP
            if dhcp_type == 'interface' and 'interface_ip' in form_data:
                interface_ip_addr, interface_subnet_mask = cidr_to_ip_netmask(form_data['interface_ip'])
                processed['interface_ip_addr'] = interface_ip_addr
                processed['interface_subnet_mask'] = interface_subnet_mask

    # 处理接口IP配置 - 支持多接口和CIDR格式
    elif config_type == 'interface_ip':
        if 'interface' in form_data:
            # 支持多接口配置
            processed['port_list'] = expand_ports(form_data['interface'])

        # 处理IP地址格式
        if 'ip_address' in form_data and '/' in form_data['ip_address']:
            # 支持CIDR格式，如 192.168.1.1/24
            ip_addr, netmask = cidr_to_ip_netmask(form_data['ip_address'])
            processed['ip_address'] = ip_addr
            if 'subnet_mask' not in form_data or not form_data['subnet_mask']:
                processed['subnet_mask'] = netmask

    # 处理静态路由
    elif config_type == 'static_route':
        # 处理目标网络格式
        if 'destination' in form_data and '/' in form_data['destination']:
            dest_network, dest_mask = cidr_to_netmask(form_data['destination'])
            processed['destination'] = dest_network
            if 'mask' not in form_data or not form_data['mask']:
                processed['mask'] = dest_mask

        # Cisco特殊处理：静态路由格式不同
        if vendor == 'cisco':
            # Cisco使用 ip route destination/mask next_hop 格式
            if 'destination' in form_data and 'mask' in processed:
                # 将destination和mask合并为CIDR格式
                import ipaddress
                try:
                    network = ipaddress.IPv4Network(f"{processed['destination']}/{processed['mask']}", strict=False)
                    processed['destination'] = str(network)
                    # Cisco不需要单独的mask参数
                    processed.pop('mask', None)
                except:
                    pass

    # 处理STP配置
    elif config_type == 'stp_config':
        # 处理全局使能（字符串转布尔值）
        if 'global_enable' in form_data:
            processed['global_enable'] = form_data['global_enable'].lower() == 'true'

        # 处理根桥配置（新的单选框格式）
        if 'root_bridge_config' in form_data:
            root_config = form_data['root_bridge_config']
            if root_config == 'primary':
                processed['root_primary'] = True
                processed['root_secondary'] = False
            elif root_config == 'secondary':
                processed['root_primary'] = False
                processed['root_secondary'] = True
            else:  # none
                processed['root_primary'] = False
                processed['root_secondary'] = False

        # 处理STP保护功能（字符串转布尔值）
        stp_protection_params = ['edge_port', 'bpdu_protection', 'root_protection', 'loop_protection']
        for param in stp_protection_params:
            if param in form_data:
                processed[param] = form_data[param].lower() == 'true'

        # 处理桥优先级（必须是4096的倍数）
        if 'bridge_priority' in form_data and form_data['bridge_priority']:
            priority = int(form_data['bridge_priority'])
            if priority % 4096 != 0:
                raise ValueError('桥优先级必须是4096的倍数')

        # 处理端口优先级（必须是16的倍数）
        if 'port_priority' in form_data and form_data['port_priority']:
            priority = int(form_data['port_priority'])
            if priority % 16 != 0:
                raise ValueError('端口优先级必须是16的倍数')

        # 处理根桥配置
        if 'root_bridge_config' in form_data:
            root_config = form_data['root_bridge_config']
            if root_config == 'primary':
                processed['root_primary'] = True
                processed['root_secondary'] = False
            elif root_config == 'secondary':
                processed['root_primary'] = False
                processed['root_secondary'] = True
            else:  # none
                processed['root_primary'] = False
                processed['root_secondary'] = False

        # 处理实例VLAN映射
        if 'instance_vlan_mapping' in form_data and form_data['instance_vlan_mapping']:
            mapping_str = form_data['instance_vlan_mapping']
            instance_vlan_list = []
            # 解析格式如：1:10,20;2:30,40
            for mapping in mapping_str.split(';'):
                if ':' in mapping:
                    instance_id, vlans = mapping.split(':', 1)
                    instance_vlan_list.append({
                        'instance': instance_id.strip(),
                        'vlans': vlans.strip()
                    })
            processed['instance_vlan_list'] = instance_vlan_list

        # 处理接口列表
        if 'interface' in form_data and form_data['interface']:
            processed['port_list'] = expand_ports(form_data['interface'])

        # 处理边缘端口接口列表
        if 'edge_port_interface' in form_data and form_data['edge_port_interface']:
            processed['edge_port_list'] = expand_ports(form_data['edge_port_interface'])

        # 处理根保护接口列表
        if 'root_protection_interface' in form_data and form_data['root_protection_interface']:
            processed['root_protection_port_list'] = expand_ports(form_data['root_protection_interface'])

        # 处理环路保护接口列表
        if 'loop_protection_interface' in form_data and form_data['loop_protection_interface']:
            processed['loop_protection_port_list'] = expand_ports(form_data['loop_protection_interface'])

    # 处理OSPF配置 - 支持区域和网络配置
    elif config_type == 'ospf_config':
        # 处理areas参数，格式：区域ID:网络地址/掩码，多个用逗号分隔
        if 'areas' in form_data:
            processed['area_network_list'] = parse_ospf_areas(form_data['areas'])

        # 处理接口范围（如果有接口配置）
        if 'interface_name' in form_data:
            processed['interface_list'] = expand_ports(form_data['interface_name'])

        if 'interface_auth_interface' in form_data:
            processed['interface_auth_list'] = expand_ports(form_data['interface_auth_interface'])

    return processed

@main.route('/api/generate', methods=['POST'])
def api_generate_config():
    """API接口：生成配置命令"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            })

        vendor = data.get('vendor')
        config_type = data.get('config_type')
        parameters = data.get('parameters', {})

        if not vendor or not config_type:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：vendor 或 config_type'
            })

        # 验证参数
        from app.validators import validate_form_data
        is_valid, errors = validate_form_data(config_type, parameters)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': '参数验证失败',
                'details': errors
            })

        # 智能处理API参数
        processed_params = process_smart_inputs(config_type, vendor, parameters)

        # 生成配置
        generator = get_config_generator()
        result = generator.generate(vendor, config_type, processed_params)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@main.route('/download/<vendor>/<config_type>')
def download_config(vendor, config_type):
    """下载配置文件"""
    try:
        # 从URL参数获取配置参数
        parameters = {}
        for key, value in request.args.items():
            if value.strip():
                if key in ['interfaces', 'dns_servers']:
                    parameters[key] = [item.strip() for item in value.split(',') if item.strip()]
                else:
                    parameters[key] = value.strip()

        # 生成配置
        generator = get_config_generator()
        result = generator.generate(vendor, config_type, parameters)

        if result['success']:
            # 生成文件内容
            content = '\n'.join(result['commands'])

            # 设置响应头
            from flask import Response
            response = Response(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename={vendor}_{config_type}_config.txt'
                }
            )
            return response
        else:
            flash(f'生成配置失败: {result["error"]}', 'error')
            return redirect(url_for('main.index'))

    except Exception as e:
        flash(f'下载失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main.errorhandler(404)
def not_found_error(error):
    """404错误处理"""
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500
