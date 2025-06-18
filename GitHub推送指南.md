# GitHub推送指南

## 📋 准备工作

### 1. 安装Git
确保您的系统已安装Git：

**Windows:**
- 下载并安装 [Git for Windows](https://git-scm.com/download/win)

**macOS:**
```bash
# 使用Homebrew安装
brew install git

# 或使用Xcode命令行工具
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

### 2. 配置Git
首次使用Git需要配置用户信息：

```bash
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"
```

### 3. 创建GitHub账户
如果还没有GitHub账户，请访问 [GitHub](https://github.com) 注册。

## 🚀 推送到GitHub的步骤

### 步骤1：在GitHub上创建仓库

1. 登录GitHub
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `switch-config-generator`
   - **Description**: `一个功能强大的交换机配置命令生成平台`
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 "Create repository"

### 步骤2：初始化本地Git仓库

在项目根目录下执行：

```bash
# 初始化Git仓库
git init

# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "Initial commit: 交换机配置命令生成平台"
```

### 步骤3：连接到GitHub仓库

```bash
# 添加远程仓库（替换为您的GitHub用户名）
git remote add origin https://github.com/您的用户名/switch-config-generator.git

# 设置主分支名称
git branch -M main
```

### 步骤4：推送代码到GitHub

```bash
# 推送代码到GitHub
git push -u origin main
```

如果遇到认证问题，可能需要：

#### 选项A：使用Personal Access Token（推荐）

1. 在GitHub上生成Personal Access Token：
   - 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token (classic)"
   - 选择适当的权限（至少需要 `repo` 权限）
   - 复制生成的token

2. 使用token进行认证：
```bash
# 当提示输入密码时，输入您的Personal Access Token
git push -u origin main
```

#### 选项B：使用SSH密钥

1. 生成SSH密钥：
```bash
ssh-keygen -t ed25519 -C "您的邮箱@example.com"
```

2. 添加SSH密钥到GitHub：
   - 复制公钥内容：`cat ~/.ssh/id_ed25519.pub`
   - 在GitHub Settings → SSH and GPG keys 中添加

3. 使用SSH URL：
```bash
git remote set-url origin git@github.com:您的用户名/switch-config-generator.git
git push -u origin main
```

## 📝 后续开发流程

### 日常提交流程

```bash
# 查看文件状态
git status

# 添加修改的文件
git add .
# 或添加特定文件
git add 文件名

# 提交更改
git commit -m "描述您的更改"

# 推送到GitHub
git push
```

### 提交信息规范

建议使用以下格式的提交信息：

```
类型: 简短描述

详细描述（可选）
```

**类型示例：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

**示例：**
```bash
git commit -m "feat: 添加思科设备OSPF配置支持"
git commit -m "fix: 修复路由引入界面重复ID问题"
git commit -m "docs: 更新README文档"
```

### 分支管理

对于功能开发，建议使用分支：

```bash
# 创建并切换到新分支
git checkout -b feature/新功能名称

# 开发完成后切换回主分支
git checkout main

# 合并分支
git merge feature/新功能名称

# 删除已合并的分支
git branch -d feature/新功能名称
```

## 🔧 常见问题解决

### 问题1：推送被拒绝
```bash
# 如果远程仓库有更新，先拉取
git pull origin main

# 解决冲突后再推送
git push
```

### 问题2：忘记添加.gitignore
```bash
# 如果已经提交了不需要的文件
git rm -r --cached __pycache__/
git commit -m "Remove cached files"
```

### 问题3：修改最后一次提交
```bash
# 修改最后一次提交信息
git commit --amend -m "新的提交信息"

# 添加文件到最后一次提交
git add 遗漏的文件
git commit --amend --no-edit
```

## 📊 项目维护

### 定期更新依赖
```bash
# 更新requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: 更新依赖包版本"
```

### 创建发布版本
```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 备份重要分支
```bash
# 创建备份分支
git checkout -b backup/main-$(date +%Y%m%d)
git push origin backup/main-$(date +%Y%m%d)
```

## 🎯 最佳实践

1. **频繁提交**：小步快跑，经常提交代码
2. **清晰的提交信息**：让其他人（包括未来的自己）能理解更改
3. **使用分支**：为新功能或修复创建专门的分支
4. **定期同步**：经常从远程仓库拉取最新代码
5. **代码审查**：重要更改前先在本地测试
6. **备份重要数据**：定期推送到远程仓库

## 📞 获取帮助

如果在推送过程中遇到问题：

1. 查看Git官方文档：https://git-scm.com/doc
2. GitHub帮助文档：https://docs.github.com/
3. 常用Git命令参考：https://git-scm.com/docs

---

🎉 恭喜！您的项目现在已经在GitHub上了！
