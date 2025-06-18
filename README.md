# 🌐 交换机配置命令生成平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能强大的Web应用程序，用于自动生成多厂商交换机的标准化配置命令。支持华为、H3C、思科、锐捷等主流厂商设备，提供直观的用户界面和丰富的配置选项。

## ✨ 功能特性

### 🏢 支持的厂商
- **华为 (Huawei)** - 企业级交换机全系列
- **新华三 (H3C)** - 数据中心和企业网络设备
- **思科 (Cisco)** - 全球领先的网络设备
- **锐捷 (Ruijie)** - 国产化网络解决方案

### ⚙️ 支持的配置类型
- **VLAN管理** - 创建、删除、批量配置VLAN
- **接口配置** - 端口模式、VLAN分配、IP地址配置
- **端口聚合** - LACP、静态聚合、负载均衡
- **DHCP服务** - 地址池、接口配置、选项设置
- **静态路由** - 路由表配置、下一跳设置
- **STP配置** - RSTP/MSTP、根桥、端口保护
- **OSPF路由** - 区域配置、认证、路由引入
- **VLAN一体化配置** - 一键完成VLAN创建和接口配置

### 🎯 核心优势
- **标准化命令** - 基于官方文档的准确命令格式
- **批量操作** - 支持端口范围、VLAN范围批量配置
- **智能验证** - 实时参数验证和错误提示
- **模板化设计** - 易于扩展和维护
- **响应式界面** - 适配桌面和移动设备
- **一键复制** - 生成的命令可直接复制到设备

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- 现代Web浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/faawrqweqw/switch-config-generator.git
cd switch-config-generator
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python run.py
```

5. **访问应用**
打开浏览器访问：http://localhost:5000

## 📖 使用指南

### 基本使用流程

1. **选择厂商** - 从下拉菜单中选择设备厂商
2. **选择配置类型** - 根据需要选择相应的配置功能
3. **填写参数** - 根据界面提示填写配置参数
4. **生成配置** - 点击"生成配置命令"按钮
5. **复制命令** - 将生成的命令复制到设备中执行

### 配置示例

#### VLAN配置示例
```bash
# 华为交换机VLAN配置
vlan batch 10 20 30 to 40
vlan 10
 description Sales_Department
vlan 20
 description IT_Department
```

#### 接口配置示例
```bash
# 思科交换机接口配置
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 description User_Port
```

#### OSPF配置示例
```bash
# H3C交换机OSPF配置
ospf 1
 router-id 1.1.1.1
 area 0.0.0.0
  network 192.168.1.0 0.0.0.255
 import-route static cost 100 type 2
```

### 高级功能

#### 批量配置
支持多种批量配置格式：
- **端口范围**：`GigabitEthernet1/0/1-4`
- **VLAN范围**：`10,20,30-40`
- **IP地址段**：`192.168.1.0/24`

#### 参数验证
- **实时验证** - 输入时即时检查参数格式
- **范围检查** - 确保参数在有效范围内
- **依赖检查** - 验证参数间的逻辑关系

#### 示例数据
每个配置类型都提供示例数据，点击"填入示例数据"按钮可快速体验功能。

## 🏗️ 项目结构

```
switch-config-generator/
├── app/                    # 应用核心代码
│   ├── __init__.py        # Flask应用初始化
│   ├── routes.py          # 路由和视图函数
│   ├── template_engine.py # 模板引擎
│   ├── utils.py           # 工具函数
│   └── validators.py      # 参数验证
├── config_templates/       # 配置模板文件
│   ├── huawei.yaml        # 华为设备模板
│   ├── h3c.yaml           # H3C设备模板
│   ├── cisco.yaml         # 思科设备模板
│   └── ruijie.yaml        # 锐捷设备模板
├── templates/             # HTML模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 主页面
│   └── result.html        # 结果页面
├── static/                # 静态资源
├── config.py              # 配置文件
├── run.py                 # 应用启动文件
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明
```

## 🔧 技术架构

### 后端技术栈
- **Flask** - 轻量级Web框架
- **Jinja2** - 模板引擎，用于命令生成
- **PyYAML** - YAML配置文件解析
- **WTForms** - 表单验证

### 前端技术栈
- **Bootstrap 5** - 响应式UI框架
- **Font Awesome** - 图标库
- **JavaScript** - 动态交互逻辑

### 核心组件
- **模板引擎** - 基于YAML的配置模板系统
- **参数验证器** - 多层级参数验证机制
- **命令生成器** - 厂商特定的命令生成逻辑

## 📝 配置模板

项目使用YAML格式的配置模板，每个厂商对应一个模板文件：

```yaml
vlan_config:
  description: "VLAN配置"
  parameters:
    vlan_id:
      type: "string"
      required: true
      description: "VLAN ID"
      placeholder: "10,20,30-40"
  commands: |
    vlan batch {{ vlan_id }}
    {% for vlan in vlan_list %}
    vlan {{ vlan }}
     description {{ description }}
    {% endfor %}
```

## 🎨 界面预览

### 主界面
- 简洁直观的厂商和配置类型选择
- 动态生成的参数表单
- 实时参数验证和提示

### OSPF路由引入界面
- 美观的卡片式路由类型选择
- 直观的图标和颜色区分
- 悬停和选中状态的视觉反馈

### 配置结果页面
- 清晰的命令展示
- 语法高亮显示
- 一键复制功能

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档
- 确保所有测试通过
- 更新相关文档

### 添加新厂商支持
1. 在 `config_templates/` 目录下创建新的YAML文件
2. 在 `app/template_engine.py` 中添加厂商支持
3. 更新前端厂商选择列表
4. 添加相应的测试用例

### 添加新配置类型
1. 在相应厂商的YAML文件中添加配置模板
2. 实现必要的参数验证逻辑
3. 添加前端交互逻辑（如需要）
4. 更新文档和示例

## 🐛 问题反馈

如果您遇到问题，请提供以下信息：

1. **环境信息**
   - 操作系统版本
   - Python版本
   - 浏览器版本

2. **问题描述**
   - 详细的问题描述
   - 重现步骤
   - 期望的行为

3. **错误信息**
   - 完整的错误日志
   - 浏览器控制台错误（如有）

## 📈 版本历史

### v2.0.0 (2025-01-XX)
- ✨ 新增思科(Cisco)厂商支持
- ✨ 新增OSPF路由配置功能
- ✨ 新增STP配置功能
- ✨ 新增路由引入功能
- 🎨 优化用户界面，采用卡片式设计
- 🐛 修复重复ID问题
- 📝 完善文档和示例

### v1.0.0 (2024-XX-XX)
- 🎉 初始版本发布
- ✨ 支持华为、H3C、锐捷三大厂商
- ✨ 基础网络配置功能
- 🎨 响应式Web界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢各厂商提供的官方文档
- 感谢开源社区的支持
- 感谢所有贡献者的努力

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/switch-config-generator/issues)
- 发送邮件至：your-email@example.com

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
