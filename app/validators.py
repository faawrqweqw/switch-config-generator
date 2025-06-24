import re
import ipaddress
from typing import Dict, List, Any, Tuple

class ConfigValidator:
    """配置参数验证器"""
    
    @staticmethod
    def validate_vlan_id(vlan_id: str) -> Tuple[bool, str]:
        """验证VLAN ID（支持批量格式，如：10,20,30-40）"""
        if not vlan_id:
            return False, "VLAN ID不能为空"

        # 支持批量格式
        try:
            for part in vlan_id.split(','):
                part = part.strip()
                if '-' in part:
                    # 处理范围
                    start, end = part.split('-')
                    start_vlan = int(start.strip())
                    end_vlan = int(end.strip())
                    if not (1 <= start_vlan <= 4094 and 1 <= end_vlan <= 4094):
                        return False, "VLAN ID必须在1-4094范围内"
                    if start_vlan >= end_vlan:
                        return False, "VLAN范围起始值必须小于结束值"
                else:
                    # 处理单个VLAN
                    vlan_num = int(part)
                    if not (1 <= vlan_num <= 4094):
                        return False, "VLAN ID必须在1-4094范围内"
            return True, ""
        except ValueError:
            return False, "VLAN ID格式不正确，支持格式：10 或 10,20,30-40"
    
    @staticmethod
    def validate_vlan_name(vlan_name: str) -> Tuple[bool, str]:
        """验证VLAN名称"""
        if not vlan_name:
            return True, ""  # VLAN名称可选
        
        if len(vlan_name) > 32:
            return False, "VLAN名称长度不能超过32个字符"
        
        # 检查是否包含特殊字符
        if not re.match(r'^[a-zA-Z0-9_-]+$', vlan_name):
            return False, "VLAN名称只能包含字母、数字、下划线和连字符"
        
        return True, ""
    
    @staticmethod
    def validate_interface(interface: str) -> Tuple[bool, str]:
        """验证接口名称（支持端口范围，如：GigabitEthernet0/0/1-4）"""
        if not interface:
            return False, "接口名称不能为空"

        # 处理逗号分隔的多个接口或范围
        parts = [part.strip() for part in interface.split(',')]

        for part in parts:
            if '-' in part:
                # 首先检查是否是范围格式，如 GigabitEthernet0/0/1-4
                match = re.match(r'^(.+?)(\d+)-(\d+)$', part)
                if match:
                    prefix, start, end = match.groups()
                    # 验证前缀格式
                    if not ConfigValidator._validate_interface_prefix(prefix + start):
                        return False, f"接口名称格式不正确: {part}"
                    # 验证范围
                    if int(start) >= int(end):
                        return False, f"接口范围起始值必须小于结束值: {part}"
                else:
                    # 不是范围格式，可能是包含连字符的接口名称（如 Vlan-interface100）
                    if not ConfigValidator._validate_interface_prefix(part):
                        return False, f"接口名称格式不正确: {part}"
            else:
                # 验证单个接口
                if not ConfigValidator._validate_interface_prefix(part):
                    return False, f"接口名称格式不正确: {part}"

        return True, ""

    @staticmethod
    def _validate_interface_prefix(interface: str) -> bool:
        """验证接口名称前缀格式"""
        patterns = [
            # 华为格式
            r'^GigabitEthernet\d+/\d+/\d+$',      # 千兆以太网
            r'^TenGigabitEthernet\d+/\d+/\d+$',   # 万兆以太网
            r'^XGigabitEthernet\d+/\d+/\d+$',     # 万兆以太网(X格式)
            r'^40GE\d+/\d+/\d+$',                 # 40G以太网
            r'^100GE\d+/\d+/\d+$',                # 100G以太网
            r'^10GE\d+/\d+/\d+$',                 # 10G以太网简写
            r'^GE\d+/\d+/\d+$',                   # 千兆以太网简写
            r'^FE\d+/\d+/\d+$',                   # 快速以太网简写
            r'^Vlanif\d+$',                       # 华为VLAN接口
            r'^vlanif\d+$',                       # 华为VLAN接口(小写)

            # H3C/锐捷格式
            r'^GigabitEthernet\d+/\d+$',          # 千兆以太网
            r'^TenGigabitEthernet\d+/\d+$',       # 万兆以太网
            r'^XGigabitEthernet\d+/\d+$',         # 万兆以太网(X格式)
            r'^40GE\d+/\d+$',                     # 40G以太网
            r'^100GE\d+/\d+$',                    # 100G以太网
            r'^10GE\d+/\d+$',                     # 10G以太网简写
            r'^GE\d+/\d+$',                       # 千兆以太网简写
            r'^FE\d+/\d+$',                       # 快速以太网简写
            r'^Vlan-interface\d+$',               # H3C VLAN接口
            r'^vlan-interface\d+$',               # H3C VLAN接口(小写)

            # 通用格式
            r'^Ethernet\d+/\d+$',                 # 通用以太网
            r'^FastEthernet\d+/\d+$',             # 快速以太网

            # 思科格式
            r'^GigabitEthernet\d+/\d+/\d+$',      # 思科千兆
            r'^TenGigabitEthernet\d+/\d+/\d+$',   # 思科万兆
            r'^FortyGigabitEthernet\d+/\d+/\d+$', # 思科40G
            r'^HundredGigE\d+/\d+/\d+$',          # 思科100G
            r'^Vlan\d+$',                         # 思科VLAN接口
        ]

        for pattern in patterns:
            if re.match(pattern, interface):
                return True
        return False
    
    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """验证IP地址（支持CIDR格式，如：192.168.1.1/24）"""
        try:
            if '/' in ip:
                # CIDR格式
                ipaddress.IPv4Network(ip, strict=False)
            else:
                # 普通IP地址
                ipaddress.ip_address(ip)
            return True, ""
        except ValueError:
            return False, "IP地址格式不正确，支持格式：192.168.1.1 或 192.168.1.0/24"
    
    @staticmethod
    def validate_subnet_mask(mask: str) -> Tuple[bool, str]:
        """验证子网掩码"""
        try:
            # 支持点分十进制和CIDR格式
            if '.' in mask:
                # 点分十进制格式
                ipaddress.ip_address(mask)
            else:
                # CIDR格式
                prefix_len = int(mask)
                if not 0 <= prefix_len <= 32:
                    return False, "CIDR前缀长度必须在0-32之间"
            return True, ""
        except ValueError:
            return False, "子网掩码格式不正确"
    
    @staticmethod
    def validate_dhcp_pool_name(pool_name: str) -> Tuple[bool, str]:
        """验证DHCP池名称"""
        if not pool_name:
            return False, "DHCP池名称不能为空"
        
        if len(pool_name) > 32:
            return False, "DHCP池名称长度不能超过32个字符"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', pool_name):
            return False, "DHCP池名称只能包含字母、数字、下划线和连字符"
        
        return True, ""
    
    @staticmethod
    def validate_port_range(port_range: str) -> Tuple[bool, str]:
        """验证端口范围"""
        if not port_range:
            return False, "端口范围不能为空"
        
        # 支持单个端口或端口范围
        if '-' in port_range:
            try:
                start, end = port_range.split('-')
                start_port = int(start.strip())
                end_port = int(end.strip())
                
                if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                    return False, "端口号必须在1-65535范围内"
                
                if start_port >= end_port:
                    return False, "起始端口必须小于结束端口"
                
                return True, ""
            except ValueError:
                return False, "端口范围格式不正确"
        else:
            try:
                port = int(port_range)
                if 1 <= port <= 65535:
                    return True, ""
                else:
                    return False, "端口号必须在1-65535范围内"
            except ValueError:
                return False, "端口号格式不正确"

    @staticmethod
    def validate_vlan_range(vlan_range: str) -> Tuple[bool, str]:
        """验证VLAN范围格式"""
        return ConfigValidator.validate_vlan_id(vlan_range)

    @staticmethod
    def validate_interface_range(interface_range: str) -> Tuple[bool, str]:
        """验证接口范围格式"""
        return ConfigValidator.validate_interface(interface_range)

def validate_form_data(config_type: str, form_data: Dict[str, Any], vendor: str = None) -> Tuple[bool, List[str]]:
    """验证表单数据（支持智能输入格式）"""
    errors = []

    if config_type == 'vlan_management':
        # 验证VLAN相关参数
        if 'vlan_id' in form_data:
            valid, msg = ConfigValidator.validate_vlan_id(str(form_data['vlan_id']))
            if not valid:
                errors.append(f"VLAN ID错误: {msg}")

        if 'vlan_name' in form_data and form_data['vlan_name']:
            valid, msg = ConfigValidator.validate_vlan_name(form_data['vlan_name'])
            if not valid:
                errors.append(f"VLAN名称错误: {msg}")

    elif config_type == 'interface_config':
        # 验证接口配置参数
        if 'interface' in form_data:
            valid, msg = ConfigValidator.validate_interface(form_data['interface'])
            if not valid:
                errors.append(f"接口名称错误: {msg}")

        if 'vlan_id' in form_data:
            valid, msg = ConfigValidator.validate_vlan_id(str(form_data['vlan_id']))
            if not valid:
                errors.append(f"VLAN ID错误: {msg}")

    elif config_type == 'port_aggregation':
        # 验证端口聚合参数
        if 'interfaces' in form_data:
            valid, msg = ConfigValidator.validate_interface(form_data['interfaces'])
            if not valid:
                errors.append(f"聚合接口错误: {msg}")

        if 'lag_id' in form_data:
            try:
                lag_id = int(form_data['lag_id'])
                if not (1 <= lag_id <= 128):
                    errors.append("聚合组ID必须在1-128范围内")
            except ValueError:
                errors.append("聚合组ID必须是数字")

    elif config_type == 'dhcp_service':
        # 验证DHCP服务参数
        # 华为厂商特殊验证
        if 'dhcp_type' in form_data:
            dhcp_type = form_data['dhcp_type']
            if dhcp_type not in ['global', 'interface']:
                errors.append("华为DHCP类型必须是 'global' 或 'interface'")

            # 全局地址池模式必须有池名称
            if dhcp_type == 'global' and not form_data.get('pool_name'):
                errors.append("全局地址池模式必须指定池名称")

        if 'pool_name' in form_data and form_data['pool_name']:
            valid, msg = ConfigValidator.validate_dhcp_pool_name(form_data['pool_name'])
            if not valid:
                errors.append(f"DHCP池名称错误: {msg}")

        if 'network' in form_data:
            valid, msg = ConfigValidator.validate_ip_address(form_data['network'])
            if not valid:
                errors.append(f"网络地址错误: {msg}")

        if 'mask' in form_data and form_data['mask']:
            valid, msg = ConfigValidator.validate_subnet_mask(form_data['mask'])
            if not valid:
                errors.append(f"子网掩码错误: {msg}")

        # 验证VLAN接口格式
        if 'vlanif' in form_data and form_data['vlanif']:
            vlanif = form_data['vlanif']
            if not vlanif.startswith('Vlanif') and not vlanif.startswith('vlanif'):
                errors.append("VLAN接口格式错误，应为 'Vlanif100' 格式")

        # 验证租期时间格式（根据厂商不同处理）
        if 'lease_time' in form_data and form_data['lease_time'] is not None:
            lease_time_value = form_data['lease_time']

            # H3C使用整数格式（天数）
            if vendor == 'h3c':
                if isinstance(lease_time_value, int):
                    if not (0 <= lease_time_value <= 365):
                        errors.append("租期时间范围错误，应为0-365天")
                elif isinstance(lease_time_value, str) and lease_time_value.strip().isdigit():
                    days = int(lease_time_value.strip())
                    if not (0 <= days <= 365):
                        errors.append("租期时间范围错误，应为0-365天")
                else:
                    errors.append("H3C租期时间应为整数（天数），如：1")

            # 其他厂商使用字符串格式（天 小时 分钟）
            else:
                if isinstance(lease_time_value, str):
                    lease_time_str = lease_time_value.strip()
                    if lease_time_str:
                        # 支持infinite关键字（思科/锐捷）
                        if lease_time_str.lower() == 'infinite':
                            pass  # infinite是有效值
                        else:
                            parts = lease_time_str.split()
                            if len(parts) != 3:
                                errors.append("租期时间格式错误，应为 '天 小时 分钟' 格式，如：1 0 0")
                            else:
                                try:
                                    days = int(parts[0])
                                    hours = int(parts[1])
                                    minutes = int(parts[2])

                                    if not (0 <= days <= 365):
                                        errors.append("租期时间天数必须在0-365范围内")
                                    if not (0 <= hours <= 23):
                                        errors.append("租期时间小时数必须在0-23范围内")
                                    if not (0 <= minutes <= 59):
                                        errors.append("租期时间分钟数必须在0-59范围内")
                                except ValueError:
                                    errors.append("租期时间必须是数字，格式：天 小时 分钟，如：1 0 0")
                else:
                    errors.append("租期时间格式错误，应为 '天 小时 分钟' 格式，如：1 0 0")

    elif config_type == 'interface_ip':
        # 验证接口IP配置参数
        if 'interface' in form_data:
            valid, msg = ConfigValidator.validate_interface(form_data['interface'])
            if not valid:
                errors.append(f"接口名称错误: {msg}")

        if 'ip_address' in form_data:
            valid, msg = ConfigValidator.validate_ip_address(form_data['ip_address'])
            if not valid:
                errors.append(f"IP地址错误: {msg}")

        if 'subnet_mask' in form_data and form_data['subnet_mask']:
            valid, msg = ConfigValidator.validate_subnet_mask(form_data['subnet_mask'])
            if not valid:
                errors.append(f"子网掩码错误: {msg}")

    elif config_type == 'static_route':
        # 验证静态路由参数
        if 'destination' in form_data:
            valid, msg = ConfigValidator.validate_ip_address(form_data['destination'])
            if not valid:
                errors.append(f"目标网络错误: {msg}")

        if 'next_hop' in form_data:
            valid, msg = ConfigValidator.validate_ip_address(form_data['next_hop'])
            if not valid:
                errors.append(f"下一跳地址错误: {msg}")

    elif config_type == 'stp_config':
        # 验证STP配置参数
        if 'stp_mode' in form_data:
            stp_mode = form_data['stp_mode']
            if stp_mode not in ['rstp', 'mstp']:
                errors.append("STP模式必须是 'rstp' 或 'mstp'")

        # 验证桥优先级
        if 'bridge_priority' in form_data and form_data['bridge_priority']:
            try:
                priority = int(form_data['bridge_priority'])
                if priority < 0 or priority > 61440 or priority % 4096 != 0:
                    errors.append("桥优先级必须在0-61440范围内且为4096的倍数")
            except ValueError:
                errors.append("桥优先级必须是数字")

        # 验证端口优先级
        if 'port_priority' in form_data and form_data['port_priority']:
            try:
                priority = int(form_data['port_priority'])
                if priority < 0 or priority > 240 or priority % 16 != 0:
                    errors.append("端口优先级必须在0-240范围内且为16的倍数")
            except ValueError:
                errors.append("端口优先级必须是数字")

        # 验证定时器参数
        if 'hello_time' in form_data and form_data['hello_time']:
            try:
                hello_time = int(form_data['hello_time'])
                if hello_time < 1 or hello_time > 10:
                    errors.append("Hello时间必须在1-10秒范围内")
            except ValueError:
                errors.append("Hello时间必须是数字")

        if 'forward_delay' in form_data and form_data['forward_delay']:
            try:
                forward_delay = int(form_data['forward_delay'])
                if forward_delay < 4 or forward_delay > 30:
                    errors.append("转发延迟时间必须在4-30秒范围内")
            except ValueError:
                errors.append("转发延迟时间必须是数字")

        if 'max_age' in form_data and form_data['max_age']:
            try:
                max_age = int(form_data['max_age'])
                if max_age < 6 or max_age > 40:
                    errors.append("最大老化时间必须在6-40秒范围内")
            except ValueError:
                errors.append("最大老化时间必须是数字")

        # 验证MSTP实例ID
        if 'instance_id' in form_data and form_data['instance_id']:
            try:
                instance_id = int(form_data['instance_id'])
                if instance_id < 1 or instance_id > 64:
                    errors.append("MSTP实例ID必须在1-64范围内")
            except ValueError:
                errors.append("MSTP实例ID必须是数字")

        # 验证修订级别
        if 'revision_level' in form_data and form_data['revision_level']:
            try:
                revision_level = int(form_data['revision_level'])
                if revision_level < 0 or revision_level > 65535:
                    errors.append("修订级别必须在0-65535范围内")
            except ValueError:
                errors.append("修订级别必须是数字")

        # 验证VLAN列表格式
        if 'vlan_list' in form_data and form_data['vlan_list']:
            valid, msg = ConfigValidator.validate_vlan_range(form_data['vlan_list'])
            if not valid:
                errors.append(f"VLAN列表格式错误: {msg}")

        # 验证接口格式
        interface_fields = ['interface', 'edge_port_interface', 'root_protection_interface', 'loop_protection_interface']
        for field in interface_fields:
            if field in form_data and form_data[field]:
                valid, msg = ConfigValidator.validate_interface_range(form_data[field])
                if not valid:
                    errors.append(f"{field}格式错误: {msg}")

        # 验证端口开销
        if 'port_cost' in form_data and form_data['port_cost']:
            try:
                port_cost = int(form_data['port_cost'])
                if port_cost < 1 or port_cost > 200000000:
                    errors.append("端口开销必须在1-200000000范围内")
            except ValueError:
                errors.append("端口开销必须是数字")

        # 验证MST域名
        if 'region_name' in form_data and form_data['region_name']:
            region_name = form_data['region_name']
            if len(region_name) > 32:
                errors.append("MST域名长度不能超过32个字符")

        # 验证根桥配置
        if 'root_bridge_config' in form_data and form_data['root_bridge_config']:
            root_config = form_data['root_bridge_config']
            if root_config not in ['none', 'primary', 'secondary']:
                errors.append("根桥配置必须是 'none', 'primary' 或 'secondary'")

        # 验证实例VLAN映射格式
        if 'instance_vlan_mapping' in form_data and form_data['instance_vlan_mapping']:
            mapping = form_data['instance_vlan_mapping']
            # 验证格式如：1:10,20;2:30,40
            if not re.match(r'^\d+:\d+(,\d+)*(;\d+:\d+(,\d+)*)*$', mapping):
                errors.append("实例VLAN映射格式不正确，应类似：1:10,20;2:30,40")

    elif config_type == 'vlan_complete_config':
        # 验证VLAN一体化配置参数
        if 'vlan_id' in form_data and form_data['vlan_id']:
            valid, msg = ConfigValidator.validate_vlan_id(str(form_data['vlan_id']))
            if not valid:
                errors.append(f"VLAN ID错误: {msg}")

        if 'vlan_name' in form_data and form_data['vlan_name']:
            valid, msg = ConfigValidator.validate_vlan_name(form_data['vlan_name'])
            if not valid:
                errors.append(f"VLAN名称错误: {msg}")

        # 验证接口配置
        if 'interface' in form_data and form_data['interface']:
            valid, msg = ConfigValidator.validate_interface(form_data['interface'])
            if not valid:
                errors.append(f"接口名称错误: {msg}")

        # 验证VLAN接口名称
        if 'vlan_interface_name' in form_data and form_data['vlan_interface_name']:
            valid, msg = ConfigValidator.validate_interface(form_data['vlan_interface_name'])
            if not valid:
                errors.append(f"VLAN接口名称错误: {msg}")

        # 验证VLAN接口IP地址
        if 'vlan_ip_address' in form_data and form_data['vlan_ip_address']:
            valid, msg = ConfigValidator.validate_ip_address(form_data['vlan_ip_address'])
            if not valid:
                errors.append(f"VLAN接口IP地址错误: {msg}")

    elif config_type == 'vrrp_config':
        # 验证VRRP配置参数
        # 必需参数验证
        required_params = ['vlan_id', 'interface_ip', 'vrrp_group_id', 'virtual_ip']
        for param in required_params:
            if param not in form_data or not form_data[param]:
                errors.append(f"VRRP配置缺少必需参数: {param}")

        # VLAN ID验证
        if 'vlan_id' in form_data and form_data['vlan_id']:
            try:
                vlan_id = int(form_data['vlan_id'])
                if not (1 <= vlan_id <= 4094):
                    errors.append("VLAN ID必须在1-4094范围内")
            except ValueError:
                errors.append("VLAN ID必须是数字")

        # 接口IP地址验证
        if 'interface_ip' in form_data and form_data['interface_ip']:
            valid, msg = ConfigValidator.validate_ip_address(form_data['interface_ip'])
            if not valid:
                errors.append(f"接口IP地址错误: {msg}")

        # VRRP组ID验证
        if 'vrrp_group_id' in form_data and form_data['vrrp_group_id']:
            try:
                group_id = int(form_data['vrrp_group_id'])
                if not (1 <= group_id <= 255):
                    errors.append("VRRP组ID必须在1-255范围内")
            except ValueError:
                errors.append("VRRP组ID必须是数字")

        # 虚拟IP地址验证
        if 'virtual_ip' in form_data and form_data['virtual_ip']:
            valid, msg = ConfigValidator.validate_ip_address(form_data['virtual_ip'])
            if not valid:
                errors.append(f"虚拟IP地址错误: {msg}")

        # 优先级验证
        if 'priority' in form_data and form_data['priority']:
            try:
                priority = int(form_data['priority'])
                if not (1 <= priority <= 254):
                    errors.append("VRRP优先级必须在1-254范围内")
            except ValueError:
                errors.append("VRRP优先级必须是数字")

        # 抢占延迟验证
        if 'preempt_delay' in form_data and form_data['preempt_delay']:
            try:
                delay = int(form_data['preempt_delay'])
                if not (0 <= delay <= 3600):
                    errors.append("抢占延迟时间必须在0-3600秒范围内")
            except ValueError:
                errors.append("抢占延迟时间必须是数字")

        # 通告间隔验证
        if 'advertisement_interval' in form_data and form_data['advertisement_interval']:
            try:
                interval = int(form_data['advertisement_interval'])
                if not (1 <= interval <= 255):
                    errors.append("通告间隔必须在1-255秒范围内")
            except ValueError:
                errors.append("通告间隔必须是数字")

        # BFD快速切换参数验证
        if form_data.get('configure_bfd') == 'true':
            if 'bfd_peer_ip' in form_data and form_data['bfd_peer_ip']:
                valid, msg = ConfigValidator.validate_ip_address(form_data['bfd_peer_ip'])
                if not valid:
                    errors.append(f"BFD对端IP地址错误: {msg}")

            if 'bfd_session_name' in form_data and form_data['bfd_session_name']:
                session_name = form_data['bfd_session_name']
                if len(session_name) > 32:
                    errors.append("BFD会话名称长度不能超过32个字符")
                if not re.match(r'^[a-zA-Z0-9_-]+$', session_name):
                    errors.append("BFD会话名称只能包含字母、数字、下划线和连字符")

            if 'bfd_local_discriminator' in form_data and form_data['bfd_local_discriminator']:
                try:
                    local_disc = int(form_data['bfd_local_discriminator'])
                    if not (1 <= local_disc <= 16384):
                        errors.append("BFD本地标识符必须在1-16384范围内")
                except ValueError:
                    errors.append("BFD本地标识符必须是数字")

            if 'bfd_remote_discriminator' in form_data and form_data['bfd_remote_discriminator']:
                try:
                    remote_disc = int(form_data['bfd_remote_discriminator'])
                    if not (1 <= remote_disc <= 16384):
                        errors.append("BFD远端标识符必须在1-16384范围内")
                except ValueError:
                    errors.append("BFD远端标识符必须是数字")

            if 'bfd_priority_reduce' in form_data and form_data['bfd_priority_reduce']:
                try:
                    reduce_val = int(form_data['bfd_priority_reduce'])
                    if not (1 <= reduce_val <= 255):
                        errors.append("BFD优先级减少值必须在1-255范围内")
                except ValueError:
                    errors.append("BFD优先级减少值必须是数字")

        # BFD上行链路监控参数验证
        if form_data.get('configure_bfd_uplink') == 'true':
            if 'bfd_uplink_peer_ip' in form_data and form_data['bfd_uplink_peer_ip']:
                valid, msg = ConfigValidator.validate_ip_address(form_data['bfd_uplink_peer_ip'])
                if not valid:
                    errors.append(f"BFD上行链路对端IP地址错误: {msg}")

            if 'bfd_uplink_session_name' in form_data and form_data['bfd_uplink_session_name']:
                session_name = form_data['bfd_uplink_session_name']
                if len(session_name) > 32:
                    errors.append("BFD上行链路会话名称长度不能超过32个字符")
                if not re.match(r'^[a-zA-Z0-9_-]+$', session_name):
                    errors.append("BFD上行链路会话名称只能包含字母、数字、下划线和连字符")

            if 'bfd_uplink_local_discriminator' in form_data and form_data['bfd_uplink_local_discriminator']:
                try:
                    local_disc = int(form_data['bfd_uplink_local_discriminator'])
                    if not (1 <= local_disc <= 16384):
                        errors.append("BFD上行链路本地标识符必须在1-16384范围内")
                except ValueError:
                    errors.append("BFD上行链路本地标识符必须是数字")

            if 'bfd_uplink_remote_discriminator' in form_data and form_data['bfd_uplink_remote_discriminator']:
                try:
                    remote_disc = int(form_data['bfd_uplink_remote_discriminator'])
                    if not (1 <= remote_disc <= 16384):
                        errors.append("BFD上行链路远端标识符必须在1-16384范围内")
                except ValueError:
                    errors.append("BFD上行链路远端标识符必须是数字")

            if 'bfd_uplink_priority_reduce' in form_data and form_data['bfd_uplink_priority_reduce']:
                try:
                    reduce_val = int(form_data['bfd_uplink_priority_reduce'])
                    if not (1 <= reduce_val <= 255):
                        errors.append("BFD上行链路优先级减少值必须在1-255范围内")
                except ValueError:
                    errors.append("BFD上行链路优先级减少值必须是数字")

        # 接口监控验证
        if form_data.get('configure_interface_monitor') == 'true':
            if 'monitor_interface' in form_data and form_data['monitor_interface']:
                valid, msg = ConfigValidator.validate_interface(form_data['monitor_interface'])
                if not valid:
                    errors.append(f"监控接口名称错误: {msg}")

            if 'monitor_priority_reduce' in form_data and form_data['monitor_priority_reduce']:
                try:
                    reduce_val = int(form_data['monitor_priority_reduce'])
                    if not (1 <= reduce_val <= 255):
                        errors.append("监控接口优先级减少值必须在1-255范围内")
                except ValueError:
                    errors.append("监控接口优先级减少值必须是数字")

        # NQA配置验证
        if form_data.get('configure_nqa_uplink') == 'true':
            if 'nqa_destination_ip' in form_data and form_data['nqa_destination_ip']:
                valid, msg = ConfigValidator.validate_ip_address(form_data['nqa_destination_ip'])
                if not valid:
                    errors.append(f"NQA目的IP地址错误: {msg}")

            if 'nqa_priority_reduce' in form_data and form_data['nqa_priority_reduce']:
                try:
                    reduce_val = int(form_data['nqa_priority_reduce'])
                    if not (1 <= reduce_val <= 255):
                        errors.append("NQA优先级减少值必须在1-255范围内")
                except ValueError:
                    errors.append("NQA优先级减少值必须是数字")

    return len(errors) == 0, errors
