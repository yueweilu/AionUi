# AionUi WebUI 配置指南

## 概述

AionUi 支持 WebUI 模式，允许通过浏览器访问应用。这对于远程使用 OpenClaw 非常有用。AionUi 提供三种远程连接方式，满足不同场景的需求。

## 三种远程连接方式

| 连接方式                    | 使用场景                     | 描述                                            | 难度        |
| --------------------------- | ---------------------------- | ----------------------------------------------- | ----------- |
| **1. 局域网连接**           | 同一 WiFi/LAN 的设备访问     | 手机和电脑在同一 WiFi，使用 `--remote` 参数     | ⭐ 简单     |
| **2. 远程软件 (Tailscale)** | 跨网络访问（如办公室到家庭） | 使用 VPN 软件如 Tailscale，无需公网 IP 或服务器 | ⭐ 非常简单 |
| **3. 服务器部署**           | 多用户访问、24/7 运行        | 部署在云服务器，通过公网 IP 直接访问            | ⭐⭐ 中等   |

### 如何选择？

- **同一 WiFi 使用** → 选择 **局域网连接**
- **办公室访问家庭，或手机使用流量** → 选择 **远程软件 (Tailscale)**
- **需要多用户访问或 24/7 运行** → 选择 **服务器部署**

---

## 默认配置

- **默认端口**：25808
- **本地访问地址**：`http://localhost:25808`
- **远程访问地址**：`http://<LAN_IP>:25808`（需要 `--remote` 参数）
- **默认用户名**：`admin`
- **初始密码**：首次启动时自动生成，会在控制台显示

---

## 方式 1：局域网连接（LAN Connection）

### 适用场景

- 手机和电脑在同一 WiFi
- 同一局域网内的设备访问
- 临时远程访问

### 环境检测

在启动 WebUI 之前，需要先检测当前环境：

1. **检查是否是开发环境**：

   ```bash
   # 检查当前目录是否是 AionUi 项目目录
   test -f package.json && grep -q '"webui"' package.json && echo "开发环境" || echo "不是开发环境"
   ```

2. **检查是否已安装 AionUi 应用**：

   ```bash
   # macOS
   test -f /Applications/AionUi.app/Contents/MacOS/AionUi && echo "已安装" || echo "未安装"

   # Linux
   which aionui || test -f /opt/AionUi/aionui && echo "已安装" || echo "未安装"

   # Windows
   test -f "C:\Program Files\AionUi\AionUi.exe" && echo "已安装" || echo "未安装"
   ```

### 启动方式

#### 开发环境（npm 脚本）

**前提条件**：必须在 AionUi 项目目录中

```bash
# 在 AionUi 项目目录中
npm run webui:remote
```

**注意**：如果当前不在项目目录，需要先切换到项目目录：

```bash
cd /path/to/AionUi
npm run webui:remote
```

#### 生产环境（已安装的应用）

**前提条件**：AionUi 应用已安装到系统

**Windows:**

```cmd
"C:\Program Files\AionUi\AionUi.exe" --webui --remote
```

**macOS:**

```bash
/Applications/AionUi.app/Contents/MacOS/AionUi --webui --remote
```

**Linux:**

```bash
aionui --webui --remote
# 或
/opt/AionUi/aionui --webui --remote
```

### 获取访问地址

**重要**：WebUI 启动后，助手应该主动获取并直接提供给用户访问地址，而不是让用户自己去查找。

1. **获取局域网 IP 地址**（助手自动执行）

   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}'
   # 或
   ip addr show | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}' | cut -d/ -f1

   # Windows
   ipconfig | findstr "IPv4" | findstr /v "127.0.0.1"
   ```

2. **检查服务是否启动**（助手自动执行）

   ```bash
   # macOS/Linux
   lsof -i :25808

   # Windows
   netstat -an | findstr 25808
   ```

3. **访问地址**（助手直接提供给用户）
   - **本地访问**：`http://localhost:25808`
   - **网络访问**：`http://<获取到的局域网IP>:25808`（如果启用了远程模式）
   - **初始密码**：首次启动时会在终端显示，助手应提醒用户查看终端输出或直接提供

### 使用步骤

1. 在运行 AionUi 的电脑上启动 WebUI（使用 `--remote` 参数）
2. 获取局域网 IP 地址
3. 在同一局域网的其他设备浏览器中访问 `http://<局域网IP>:25808`
4. 使用 admin 用户名和初始密码登录

---

## 方式 2：远程软件 (Tailscale) - 跨网络访问

### 适用场景

- 从办公室访问家庭的 AionUi
- 从手机（使用流量）访问家庭的 AionUi
- 需要跨网络访问，但不想配置公网 IP

### 优势

- ⭐ 非常简单：安装软件，登录即可
- 🔒 安全：使用 VPN 加密连接
- 🚀 快速：无需配置防火墙或端口转发
- 📱 移动友好：支持手机、平板等设备

### 配置步骤

#### Step 1: 在 AionUi 电脑上启动 WebUI

在运行 AionUi 的电脑上，打开 AionUi 应用，从界面启动 WebUI 服务：

1. 打开 AionUi 应用
2. 点击设置（Settings）
3. 找到 WebUI 配置
4. 启用 WebUI 并开启"允许远程访问"
5. 记录显示的访问地址和初始密码

**或使用命令行：**

```bash
# 启动 WebUI（不需要 --remote，因为 Tailscale 会处理网络）
npm run webui
# 或
AionUi --webui
```

#### Step 2: 在 AionUi 电脑上安装并登录 Tailscale

1. 访问 [Tailscale 官网](https://tailscale.com/) 下载并安装
2. 登录 Tailscale 账户（首次使用需要注册）
3. 确保 Tailscale 显示"Connected"状态

#### Step 3: 获取 Tailscale IP 并组合访问 URL

1. 在 AionUi 电脑上，打开 Tailscale 应用
2. 查看显示的 Tailscale IP 地址（例如：`100.x.x.x`）
3. 组合访问 URL：`http://<Tailscale_IP>:25808`

#### Step 4: 在远程设备上安装并登录 Tailscale

1. 在手机或其他远程设备上安装 Tailscale
2. 使用相同的 Tailscale 账户登录
3. 确保显示"Connected"状态

#### Step 5: 在远程设备浏览器中访问

1. 打开浏览器
2. 访问 `http://<Tailscale_IP>:25808`（使用 Step 3 中的地址）
3. 使用 admin 用户名和初始密码登录

### 常见命令

```bash
# 查看 Tailscale 状态
tailscale status

# 查看 Tailscale IP
tailscale ip

# 查看所有设备
tailscale status --json
```

---

## 方式 3：服务器部署（Server Deployment）

### 适用场景

- 需要多用户访问
- 需要 24/7 运行
- 部署在云服务器上
- 通过公网 IP 或域名访问

### 前置要求

- 云服务器（Linux/macOS）
- 公网 IP 或域名
- 防火墙配置权限

---

### Linux 服务器部署（推荐）

#### Step 1: 创建 systemd 服务文件

创建 `/etc/systemd/system/aionui-webui.service`：

```ini
[Unit]
Description=AionUi WebUI Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/AionUi
ExecStart=/path/to/AionUi/AionUi --webui --remote
Restart=on-failure
RestartSec=10
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
```

**重要配置说明：**

- `User`: 替换为运行 AionUi 的用户名
- `WorkingDirectory`: 替换为 AionUi 安装目录
- `ExecStart`: 替换为 AionUi 可执行文件的完整路径

#### Step 2: 添加配置（可选）

如果需要自定义端口，可以创建配置文件 `webui.config.json`：

```json
{
  "port": 25808,
  "allowRemote": true
}
```

配置文件位置：

- Linux: `~/.config/AionUi/webui.config.json`
- macOS: `~/Library/Application Support/AionUi/webui.config.json`
- Windows: `%APPDATA%/AionUi/webui.config.json`

#### Step 3: 启用并启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable aionui-webui.service

# 启动服务
sudo systemctl start aionui-webui.service

# 检查状态
sudo systemctl status aionui-webui.service

# 查看日志
sudo journalctl -u aionui-webui.service -f
```

#### Step 4: 配置防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 25808/tcp
sudo ufw reload

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=25808/tcp
sudo firewall-cmd --reload

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 25808 -j ACCEPT
```

#### Step 5: 获取访问地址

1. 获取服务器公网 IP：

   ```bash
   curl ifconfig.me
   # 或
   curl ipinfo.io/ip
   ```

2. 访问地址：`http://<公网IP>:25808`

3. 如果配置了域名，可以使用：`http://<域名>:25808`

---

### macOS 服务器部署

#### Step 1: 创建 LaunchAgent 配置文件

创建 `~/Library/LaunchAgents/com.aionui.webui.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aionui.webui</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/AionUi.app/Contents/MacOS/AionUi</string>
        <string>--webui</string>
        <string>--remote</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/aionui-webui.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/aionui-webui.error.log</string>
</dict>
</plist>
```

#### Step 2: 启动服务

```bash
# 加载服务
launchctl load ~/Library/LaunchAgents/com.aionui.webui.plist

# 启动服务
launchctl start com.aionui.webui

# 检查状态
launchctl list | grep aionui

# 查看日志
tail -f /tmp/aionui-webui.log
```

#### Step 3: 配置防火墙

```bash
# 允许端口 25808
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/AionUi.app/Contents/MacOS/AionUi
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Applications/AionUi.app/Contents/MacOS/AionUi
```

---

## 命令行选项

### 基本选项

| 选项               | 描述                     |
| ------------------ | ------------------------ |
| `--webui`          | 启动 WebUI 模式          |
| `--remote`         | 允许远程网络访问         |
| `--webui --remote` | 组合使用，启动远程 WebUI |

### 端口配置

可以通过以下方式自定义端口（优先级从高到低）：

1. **命令行参数**：`--port 8080` 或 `--webui-port 8080`
2. **环境变量**：`AIONUI_PORT=8080` 或 `PORT=8080`
3. **配置文件**：`webui.config.json` 中的 `port` 字段

示例：

```bash
# 使用命令行参数
AionUi --webui --remote --port 8080

# 使用环境变量
AIONUI_PORT=8080 AionUi --webui --remote

# 使用配置文件
# 编辑 ~/.config/AionUi/webui.config.json
{
  "port": 8080,
  "allowRemote": true
}
```

---

## 用户配置文件

从 v1.5.0+ 开始，可以在用户数据目录中创建 `webui.config.json` 来持久化 WebUI 配置：

| 平台    | 配置文件位置                                             |
| ------- | -------------------------------------------------------- |
| Windows | `%APPDATA%/AionUi/webui.config.json`                     |
| macOS   | `~/Library/Application Support/AionUi/webui.config.json` |
| Linux   | `~/.config/AionUi/webui.config.json`                     |

示例配置：

```json
{
  "port": 25808,
  "allowRemote": true
}
```

**优先级**：命令行参数 > 环境变量 > 配置文件

---

## 密码管理

### 获取初始密码

首次启动 WebUI 时，初始密码会在控制台输出。请妥善保管。

### 重置密码

如果忘记密码，可以使用 `--resetpass` 命令重置：

**Windows:**

```cmd
"C:\Program Files\AionUi\AionUi.exe" --resetpass
# 或指定用户
"C:\Program Files\AionUi\AionUi.exe" --resetpass username
```

**macOS:**

```bash
/Applications/AionUi.app/Contents/MacOS/AionUi --resetpass
# 或指定用户
/Applications/AionUi.app/Contents/MacOS/AionUi --resetpass username
```

**Linux:**

```bash
aionui --resetpass
# 或指定用户
aionui --resetpass username
```

**注意**：重置密码会生成新的随机密码，所有现有的 JWT token 将失效。

---

## 检查 WebUI 状态

### 方法 1：检查端口

```bash
# 检查默认端口是否被占用
lsof -i :25808

# 或使用 netstat (Linux/Windows)
netstat -an | grep 25808
```

### 方法 2：检查进程

```bash
# 检查是否有 WebUI 进程在运行
ps aux | grep "webui\|AionUi" | grep -v grep
```

### 方法 3：尝试访问

```bash
# 尝试访问本地地址
curl http://localhost:25808
```

### 方法 4：检查服务状态（Linux systemd）

```bash
sudo systemctl status aionui-webui.service
```

---

## 故障排查

### 端口被占用

如果 25808 端口被占用：

1. **查找占用端口的进程**

   ```bash
   lsof -i :25808
   # 或
   sudo netstat -tlnp | grep 25808
   ```

2. **停止占用端口的进程**，或使用其他端口：
   ```bash
   AionUi --webui --remote --port 8080
   ```

### 无法远程访问

1. **确认使用了 `--remote` 参数**
2. **检查防火墙设置**
   - Linux: `sudo ufw status` 或 `sudo firewall-cmd --list-all`
   - macOS: 系统偏好设置 > 安全性与隐私 > 防火墙
   - Windows: 控制面板 > Windows Defender 防火墙
3. **确认设备在同一局域网**（局域网连接方式）
4. **检查 IP 地址是否正确**
5. **检查云服务器安全组规则**（服务器部署方式）

### 服务无法启动（Linux systemd）

1. **检查 AionUi 路径是否正确**

   ```bash
   which AionUi
   # 或
   whereis AionUi
   ```

2. **检查用户权限**

   ```bash
   # 确保服务文件中的用户有执行权限
   ls -l /path/to/AionUi/AionUi
   ```

3. **查看详细错误日志**
   ```bash
   sudo journalctl -u aionui-webui.service -n 50
   ```

### 无法从互联网访问服务器

1. **检查防火墙是否开放端口 25808**
2. **检查云服务器安全组规则是否允许端口 25808**
3. **确认 AionUi 使用 `--remote` 参数启动**
4. **验证服务正在运行**：`sudo systemctl status aionui-webui.service`

### 检查端口是否开放

```bash
# 使用 telnet 测试
telnet Your-Server-IP 25808

# 或使用 nc (netcat)
nc -zv Your-Server-IP 25808

# 检查本地端口监听
sudo netstat -tlnp | grep 25808
```

### 服务自动重启失败

1. **查看日志中的具体错误**

   ```bash
   sudo journalctl -u aionui-webui.service
   ```

2. **确认 AionUi 可执行文件路径正确**
3. **检查磁盘空间**：`df -h`
4. **检查内存使用**：`free -h`

### Tailscale 相关问题

**Q: Tailscale 显示未连接？**

- 检查网络连接
- 确认 Tailscale 账户已登录
- 重启 Tailscale 服务

**Q: 无法通过 Tailscale IP 访问？**

- 确认两端设备都已登录 Tailscale
- 检查 Tailscale 状态：`tailscale status`
- 确认 AionUi WebUI 已启动

---

## 安全建议

### 基本安全

1. **修改初始密码**：首次启动后立即修改默认密码
2. **使用强密码**：密码至少 8 位，包含字母、数字和特殊字符
3. **定期更新密码**：建议定期更换密码

### 远程访问安全

1. **仅在受信任的网络中使用 `--remote`**
2. **使用 Tailscale**：跨网络访问时，Tailscale 提供加密连接，更安全
3. **配置防火墙**：仅允许必要的 IP 地址访问
4. **使用 HTTPS**：生产环境建议配置 HTTPS（需要反向代理如 Nginx）

### 服务器部署安全

1. **配置防火墙规则**：仅开放必要端口
2. **使用强密码**：避免使用默认或弱密码
3. **定期更新**：保持 AionUi 和系统更新
4. **监控日志**：定期检查访问日志
5. **考虑使用反向代理**：使用 Nginx 等反向代理，配置 SSL/TLS

### Tailscale 的优势

- 🔒 **加密连接**：所有流量都经过加密
- 🛡️ **零信任网络**：只有授权设备可以访问
- 🚀 **无需配置**：无需配置防火墙或端口转发
- 📱 **跨平台**：支持 Windows、macOS、Linux、iOS、Android

---

## 与 OpenClaw 集成

启动 WebUI 后，可以通过浏览器访问 AionUi，然后：

1. **在首页找到 OpenClaw 入口**（ACP 代理列表）
2. **直接与 OpenClaw 对话**
3. **享受完整的 AionUi 界面功能**：
   - 文件预览和管理
   - 多对话管理
   - 完整的工具和技能支持

---

## 相关资源

- [AionUi Wiki - Remote Internet Access Guide](https://github.com/iOfficeAI/AionUi/wiki/Remote-Internet-Access-Guide)
- [AionUi Wiki - WebUI Configuration Guide](https://github.com/iOfficeAI/AionUi/wiki/WebUI-Configuration-Guide)
- [Tailscale 官方文档](https://tailscale.com/kb/)

---

## 快速参考

### 启动命令速查

```bash
# 开发环境 - 本地
npm run webui

# 开发环境 - 远程
npm run webui:remote

# 生产环境 - 本地
npm run webui:prod

# 生产环境 - 远程
npm run webui:prod:remote

# 已安装应用 - 远程
AionUi --webui --remote

# 自定义端口
AionUi --webui --remote --port 8080
```

### 常用检查命令

```bash
# 检查端口
lsof -i :25808

# 检查进程
ps aux | grep AionUi

# 获取 IP 地址
ifconfig | grep "inet " | grep -v 127.0.0.1

# 测试连接
curl http://localhost:25808
```

### 服务管理（Linux）

```bash
# 启动服务
sudo systemctl start aionui-webui.service

# 停止服务
sudo systemctl stop aionui-webui.service

# 重启服务
sudo systemctl restart aionui-webui.service

# 查看状态
sudo systemctl status aionui-webui.service

# 查看日志
sudo journalctl -u aionui-webui.service -f
```
