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
                # 处理范围，如 GigabitEthernet0/0/1-4
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
                    return False, f"接口范围格式不正确: {part}"
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

            # H3C/锐捷格式
            r'^GigabitEthernet\d+/\d+$',          # 千兆以太网
            r'^TenGigabitEthernet\d+/\d+$',       # 万兆以太网
            r'^XGigabitEthernet\d+/\d+$',         # 万兆以太网(X格式)
            r'^40GE\d+/\d+$',                     # 40G以太网
            r'^100GE\d+/\d+$',                    # 100G以太网
            r'^10GE\d+/\d+$',                     # 10G以太网简写
            r'^GE\d+/\d+$',                       # 千兆以太网简写
            r'^FE\d+/\d+$',                       # 快速以太网简写

            # 通用格式
            r'^Ethernet\d+/\d+$',                 # 通用以太网
            r'^FastEthernet\d+/\d+$',             # 快速以太网

            # 思科格式
            r'^GigabitEthernet\d+/\d+/\d+$',      # 思科千兆
            r'^TenGigabitEthernet\d+/\d+/\d+$',   # 思科万兆
            r'^FortyGigabitEthernet\d+/\d+/\d+$', # 思科40G
            r'^HundredGigE\d+/\d+/\d+$',          # 思科100G
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

def validate_form_data(config_type: str, form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
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

        # 验证租期时间格式
        if 'lease_time' in form_data and form_data['lease_time']:
            lease_time_str = form_data['lease_time'].strip()
            if lease_time_str:
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
            import re
            if not re.match(r'^\d+:\d+(,\d+)*(;\d+:\d+(,\d+)*)*$', mapping):
                errors.append("实例VLAN映射格式不正确，应类似：1:10,20;2:30,40")

    return len(errors) == 0, errors
