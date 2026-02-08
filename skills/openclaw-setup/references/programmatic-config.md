# OpenClaw 程序化配置指南

本指南说明如何通过读取和写入配置文件的方式，而非交互式命令来配置 OpenClaw。

## 配置文件位置

- **主配置文件**: `~/.openclaw/openclaw.json`（JSON5 格式）
- **工作区**: `~/.openclaw/workspace`（默认）
- **凭证目录**: `~/.openclaw/credentials/`

## 配置方式对比

### 方式 1：使用 `openclaw config set` 命令（推荐）

这是最安全的方式，OpenClaw 会自动验证配置格式和权限。

```bash
# 设置 Gateway 模式
openclaw config set gateway.mode local

# 设置 Gateway 端口
openclaw config set gateway.port 18789

# 设置 Gateway 绑定地址
openclaw config set gateway.bind 127.0.0.1

# 设置默认模型
openclaw config set agents.defaults.model anthropic/claude-opus-4-5

# 设置工作区路径
openclaw config set agents.defaults.workspace ~/.openclaw/workspace
```

### 方式 2：直接读写 JSON 配置文件

适用于批量配置或需要复杂配置结构的场景。

**读取配置：**

```bash
cat ~/.openclaw/openclaw.json
```

**修改配置：**

1. 读取现有配置（如果存在）
2. 合并或更新配置项
3. 写入文件（确保 JSON5 格式正确）
4. 设置文件权限：`chmod 600 ~/.openclaw/openclaw.json`

## 最小化初始配置

要让 OpenClaw 基本可用，至少需要配置：

### 1. Gateway 配置（必需）

```bash
# 设置 Gateway 为本地模式
openclaw config set gateway.mode local

# 设置端口（默认 18789）
openclaw config set gateway.port 18789

# 设置绑定地址
openclaw config set gateway.bind 127.0.0.1
```

### 2. Agent 默认配置（推荐）

```bash
# 设置默认模型（需要用户提供 API Key）
openclaw config set agents.defaults.model anthropic/claude-opus-4-5

# 设置工作区路径
openclaw config set agents.defaults.workspace ~/.openclaw/workspace
```

### 3. API 密钥配置

API 密钥可以通过环境变量或配置文件设置：

**环境变量方式（推荐）：**

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

**配置文件方式：**
需要直接修改 `~/.openclaw/openclaw.json`，在 `agents.defaults` 中添加 `apiKey` 字段（注意：这种方式安全性较低，建议使用环境变量）。

## 程序化配置流程

### 步骤 1：检查配置目录是否存在

```bash
if [ ! -d ~/.openclaw ]; then
  mkdir -p ~/.openclaw
fi
```

### 步骤 2：检查配置文件是否存在

```bash
if [ ! -f ~/.openclaw/openclaw.json ]; then
  # 创建最小化配置文件
  echo '{}' > ~/.openclaw/openclaw.json
  chmod 600 ~/.openclaw/openclaw.json
fi
```

### 步骤 3：设置基本配置

```bash
# 使用 config set 命令设置基本配置
openclaw config set gateway.mode local
openclaw config set gateway.port 18789
openclaw config set gateway.bind 127.0.0.1
openclaw config set agents.defaults.workspace ~/.openclaw/workspace
```

### 步骤 4：创建工作区（如果需要）

```bash
if [ ! -d ~/.openclaw/workspace ]; then
  mkdir -p ~/.openclaw/workspace
fi
```

### 步骤 5：验证配置

```bash
# 运行健康检查
openclaw doctor

# 或检查特定配置项
openclaw config get gateway.mode
openclaw config get gateway.port
```

## 在 AionUi 中的实现建议

### 方案 A：使用 `openclaw config set` 命令（推荐）

优点：

- 自动验证配置格式
- 自动处理文件权限
- 更安全可靠

实现示例：

```javascript
const { execSync } = require('child_process');

function configureOpenClaw(config) {
  const commands = [];

  if (config.gateway?.mode) {
    commands.push(`openclaw config set gateway.mode ${config.gateway.mode}`);
  }
  if (config.gateway?.port) {
    commands.push(`openclaw config set gateway.port ${config.gateway.port}`);
  }
  if (config.agents?.defaults?.workspace) {
    commands.push(`openclaw config set agents.defaults.workspace ${config.agents.defaults.workspace}`);
  }

  commands.forEach((cmd) => {
    try {
      execSync(cmd, { stdio: 'inherit' });
    } catch (error) {
      console.error(`Failed to execute: ${cmd}`, error);
    }
  });
}
```

### 方案 B：直接读写 JSON 文件

优点：

- 可以批量设置多个配置项
- 可以设置复杂嵌套结构

注意事项：

- 需要处理 JSON5 格式（支持注释）
- 需要合并现有配置，避免覆盖
- 需要设置正确的文件权限

实现示例：

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

function readOpenClawConfig() {
  const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
  if (!fs.existsSync(configPath)) {
    return {};
  }
  const content = fs.readFileSync(configPath, 'utf-8');
  // 注意：OpenClaw 使用 JSON5，但 Node.js 默认只支持 JSON
  // 如果配置文件包含注释，需要使用 json5 库解析
  try {
    return JSON.parse(content);
  } catch (error) {
    // 如果解析失败，可能需要使用 json5 库
    console.error('Failed to parse config:', error);
    return {};
  }
}

function writeOpenClawConfig(config) {
  const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
  const configDir = path.dirname(configPath);

  // 确保目录存在
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  // 读取现有配置并合并
  const existing = readOpenClawConfig();
  const merged = { ...existing, ...config };

  // 写入文件
  fs.writeFileSync(configPath, JSON.stringify(merged, null, 2), 'utf-8');

  // 设置文件权限
  fs.chmodSync(configPath, 0o600);
}
```

## 推荐的工作流程

1. **安装完成后**：
   - 检查 `~/.openclaw/openclaw.json` 是否存在
   - 如果不存在，创建最小化配置

2. **设置基本配置**：
   - 使用 `openclaw config set` 设置 Gateway 基本配置
   - 创建工作区目录

3. **询问用户敏感信息**：
   - API Key（通过环境变量设置，或询问用户后设置）
   - 渠道 Token（如 Telegram Bot Token）

4. **验证配置**：
   - 运行 `openclaw doctor` 检查配置完整性
   - 根据检查结果补充缺失的配置

5. **启动 Gateway**：
   - 如果配置完整，可以启动 Gateway 服务
   - 使用 `openclaw gateway start` 或 `openclaw gateway install`

## 注意事项

1. **文件权限**：配置文件应设置为 `600`（仅所有者可读写）
2. **JSON5 格式**：OpenClaw 配置文件支持 JSON5（带注释的 JSON），如果直接读写文件，需要注意处理注释
3. **配置合并**：直接修改文件时，应合并现有配置，避免覆盖用户已设置的配置
4. **敏感信息**：API Key 等敏感信息建议通过环境变量设置，而非直接写入配置文件
5. **验证配置**：每次修改配置后，应运行 `openclaw doctor` 验证配置有效性

## 参考

- OpenClaw 配置管理：`references/configuration.md`
- OpenClaw 部署指南：`references/deployment.md`
- OpenClaw 故障排查：`references/troubleshooting.md`
