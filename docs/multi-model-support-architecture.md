# 多模型支持架构文档

## 概述

本项目通过分层架构实现了对 20+ 个 AI 模型提供商的统一支持，包括 OpenAI、Claude、Gemini、DeepSeek、通义千问等国内外主流模型。核心设计理念是通过适配器模式和协议转换，让用户无感知地切换不同的 AI 模型。

## 架构设计

### 核心思路：适配器模式

就像使用万能充电器给不同设备充电一样，本项目实现了一个统一的接口层，屏蔽了不同 AI 模型的协议差异。

### 架构分层

```
┌─────────────────────────────────────────┐
│         用户界面层 (UI Layer)            │
│    - 模型选择下拉菜单                     │
│    - 对话界面                            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      模型管理层 (Model Manager)          │
│    - GeminiAgentManager                 │
│    - AcpAgentManager                    │
│    - CodexAgentManager                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      客户端工厂 (ClientFactory)          │
│    - 根据平台类型创建对应客户端           │
│    - URL 规范化                          │
│    - 协议识别                            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      协议适配器层 (Adapters)             │
│    - OpenAIRotatingClient               │
│    - GeminiRotatingClient               │
│    - AnthropicRotatingClient            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      API 密钥管理 (ApiKeyManager)        │
│    - 多密钥轮换                          │
│    - 失败密钥黑名单                      │
│    - 自动重试机制                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      AI 模型服务 (AI Services)           │
│    - OpenAI API                         │
│    - Gemini API                         │
│    - DeepSeek API                       │
│    - 其他 20+ 平台                       │
└─────────────────────────────────────────┘
```

## 核心组件详解

### 1. 模型平台配置 (modelPlatforms.ts)

**位置**: `src/renderer/config/modelPlatforms.ts`

**功能**: 集中管理所有 AI 平台的配置信息

**支持的平台**:
- 官方平台: Gemini, Gemini Vertex AI, OpenAI, Anthropic
- 国内平台: DeepSeek, Zhipu, Moonshot, Qwen, Baidu, Tencent
- 聚合平台: OpenRouter, SiliconFlow, New API 网关
- 云服务: AWS Bedrock

**配置结构**:
```typescript
interface PlatformConfig {
  name: string;        // 平台名称
  value: string;       // 平台标识
  logo: string | null; // Logo 图标
  platform: PlatformType; // 平台类型
  baseUrl?: string;    // API 基础 URL
  i18nKey?: string;    // 国际化 key
}
```

**示例配置**:
```typescript
{
  name: 'DeepSeek',
  value: 'DeepSeek',
  logo: DeepSeekLogo,
  platform: 'custom',
  baseUrl: 'https://api.deepseek.com/v1'
}
```

### 2. 客户端工厂 (ClientFactory)

**位置**: `src/common/ClientFactory.ts`

**功能**: 根据平台类型创建对应的 API 客户端

**支持的认证类型**:
- `AuthType.USE_OPENAI` → OpenAIRotatingClient
- `AuthType.USE_GEMINI` → GeminiRotatingClient
- `AuthType.USE_VERTEX_AI` → GeminiRotatingClient (Vertex AI 模式)
- `AuthType.USE_ANTHROPIC` → AnthropicRotatingClient
- `AuthType.USE_BEDROCK` → BedrockClient

**核心方法**:
```typescript
static async createRotatingClient(
  provider: TProviderWithModel,
  options: ClientOptions = {}
): Promise<RotatingClient>
```

**处理流程**:
1. 识别认证类型 (`getProviderAuthType`)
2. URL 规范化 (特别是 New API 网关)
3. 创建对应的客户端实例
4. 配置代理、超时、请求头等

### 3. 协议适配器 (Rotating Clients)

#### OpenAIRotatingClient
**位置**: `src/common/adapters/OpenAIRotatingClient.ts`

**功能**: 
- 支持 OpenAI 及所有兼容 OpenAI 协议的平台
- 提供统一的聊天、图像生成、嵌入等接口

**核心方法**:
```typescript
async createChatCompletion(
  params: OpenAI.Chat.Completions.ChatCompletionCreateParams,
  options?: OpenAI.RequestOptions
): Promise<OpenAI.Chat.Completions.ChatCompletion>
```

#### GeminiRotatingClient
**位置**: `src/common/adapters/GeminiRotatingClient.ts`

**功能**:
- 支持 Google Gemini 和 Vertex AI
- 提供 OpenAI 格式到 Gemini 格式的转换

**特性**:
- 内置 `OpenAI2GeminiConverter` 协议转换器
- 支持流式响应
- 自动处理 Vertex AI 认证

#### AnthropicRotatingClient
**位置**: `src/common/adapters/AnthropicRotatingClient.ts`

**功能**:
- 支持 Anthropic Claude 系列模型
- 处理 Claude 特有的消息格式

### 4. API 密钥管理器 (ApiKeyManager)

**位置**: `src/common/ApiKeyManager.ts`

**功能**: 智能管理多个 API 密钥，提供负载均衡和容错能力

**核心特性**:

1. **多密钥轮换**
   - 支持配置多个 API 密钥（逗号或换行分隔）
   - 随机初始化，避免热点
   - 自动轮换使用

2. **失败密钥黑名单**
   - 失败的密钥自动加入黑名单
   - 黑名单持续时间: 90 秒
   - 90 秒后自动恢复可用

3. **智能重试**
   - 遇到速率限制 (429) 自动切换密钥
   - 最多重试 3 次
   - 指数退避策略

**使用示例**:
```typescript
// 配置多个密钥
API Key: sk-key1, sk-key2, sk-key3

// 自动管理
- 初始随机选择 sk-key2
- sk-key2 失败 → 黑名单 90 秒 → 切换到 sk-key3
- 90 秒后 sk-key2 自动恢复
```

### 5. 认证类型识别 (platformAuthType)

**位置**: `src/common/utils/platformAuthType.ts`

**功能**: 智能识别平台的认证类型

**识别策略**:
1. 优先使用明确指定的 `authType`
2. New API 平台支持按模型名称覆盖协议
3. 根据平台名称自动推断

**识别规则**:
```typescript
// Gemini 相关
"gemini-vertex-ai" → AuthType.USE_VERTEX_AI
"gemini" → AuthType.USE_GEMINI

// Anthropic 相关
"anthropic" | "claude" → AuthType.USE_ANTHROPIC

// AWS Bedrock
"bedrock" → AuthType.USE_BEDROCK

// 其他默认
* → AuthType.USE_OPENAI
```

### 6. 存储层 (storage.ts)

**位置**: `src/common/storage.ts`

**功能**: 定义配置存储结构

**核心接口**:
```typescript
interface IProvider {
  id: string;                    // 唯一标识
  platform: string;              // 平台类型
  name: string;                  // 显示名称
  baseUrl: string;               // API 地址
  apiKey: string;                // API 密钥
  model: string[];               // 可用模型列表
  capabilities?: ModelCapability[]; // 模型能力标签
  modelProtocols?: Record<string, string>; // New API 按模型协议
  bedrockConfig?: {...};         // AWS Bedrock 配置
}
```

## 完整流程示例

### 场景 1: 使用预设平台 DeepSeek

#### 步骤 1: 用户配置

用户在设置页面选择 DeepSeek:
```
平台: DeepSeek (预设)
Base URL: https://api.deepseek.com/v1 (自动填充)
API Key: sk-deepseek-xxxxx (用户输入)
可用模型: deepseek-chat, deepseek-coder (用户输入)
```

#### 步骤 2: 存储配置

系统保存配置:
```typescript
{
  id: "deepseek-001",
  platform: "custom",
  name: "DeepSeek",
  baseUrl: "https://api.deepseek.com/v1",
  apiKey: "sk-deepseek-xxxxx",
  model: ["deepseek-chat", "deepseek-coder"]
}
```

#### 步骤 3: 创建对话

用户新建对话，选择 `deepseek-chat` 模型

#### 步骤 4: 初始化客户端

```typescript
// ClientFactory 创建客户端
ClientFactory.createRotatingClient({
  platform: "custom",
  baseUrl: "https://api.deepseek.com/v1",
  apiKey: "sk-deepseek-xxxxx",
  useModel: "deepseek-chat"
})

↓

// 识别认证类型
getProviderAuthType({platform: "custom"})
→ AuthType.USE_OPENAI

↓

// 创建 OpenAI 兼容客户端
new OpenAIRotatingClient(
  apiKeys: "sk-deepseek-xxxxx",
  config: {
    baseURL: "https://api.deepseek.com/v1",
    timeout: 60000,
    defaultHeaders: {
      'HTTP-Referer': 'https://aionui.com',
      'X-Title': 'AionUi'
    }
  }
)
```

#### 步骤 5: 发送消息

用户输入: "写个快速排序"

```typescript
// 构造 OpenAI 格式请求
const request = {
  model: "deepseek-chat",
  messages: [
    {role: "system", content: "你是一个编程助手"},
    {role: "user", content: "写个快速排序"}
  ],
  temperature: 0.7,
  stream: true
}

↓

// 发送 HTTP 请求
POST https://api.deepseek.com/v1/chat/completions
Headers:
  Authorization: Bearer sk-deepseek-xxxxx
  Content-Type: application/json
  HTTP-Referer: https://aionui.com
  X-Title: AionUi
Body: {上述 request}
```

#### 步骤 6: 接收响应

DeepSeek 返回流式响应:
```
data: {"choices":[{"delta":{"content":"好"}}]}
data: {"choices":[{"delta":{"content":"的"}}]}
data: {"choices":[{"delta":{"content":"，"}}]}
...
data: [DONE]
```

#### 步骤 7: 显示结果

界面实时显示 AI 回复，一个字一个字蹦出来

### 场景 2: 使用自定义模型

#### 步骤 1: 用户配置

```
平台: Custom (自定义)
名称: 我的内网模型
Base URL: http://192.168.1.100:8000/v1
API Key: sk-abc123xyz
可用模型: my-custom-gpt, my-fast-model
```

#### 步骤 2-7: 流程与 DeepSeek 完全相同

唯一区别是 Base URL 不同，其他处理逻辑完全一致

### 场景 3: 使用 New API 网关 (多协议)

#### 步骤 1: 配置网关

```
平台: new-api
Base URL: http://gateway.com
API Key: sk-gateway-key
模型列表:
  - gemini-pro
  - claude-3
  - gpt-4

模型协议映射:
{
  "gemini-pro": "gemini",
  "claude-3": "anthropic",
  "gpt-4": "openai"
}
```

#### 步骤 2: 选择 gemini-pro 模型

```typescript
// 识别协议
getProviderAuthType({
  platform: "new-api",
  useModel: "gemini-pro",
  modelProtocols: {"gemini-pro": "gemini"}
})
→ AuthType.USE_GEMINI  // 根据 modelProtocols 查找

↓

// URL 规范化
normalizeNewApiBaseUrl("http://gateway.com/v1", USE_GEMINI)
→ "http://gateway.com"  // Gemini 不需要 /v1 后缀

↓

// 创建 Gemini 客户端
new GeminiRotatingClient(...)

↓

// 请求转换
用户消息 → OpenAI 格式 → Gemini 格式 → 发送到网关
```

## 错误处理机制

### 1. API 密钥错误 (401)

```typescript
POST https://api.deepseek.com/v1/chat/completions
← 401 Unauthorized

↓

// 不重试，直接返回错误
throw new Error("API 密钥无效，请检查配置")

↓

// 界面显示
❌ API 密钥无效，请检查配置
```

### 2. 速率限制 (429)

```typescript
POST https://api.deepseek.com/v1/chat/completions
← 429 Too Many Requests

↓

// ApiKeyManager 处理
1. 将当前密钥加入黑名单 (90 秒)
2. 检查是否有其他可用密钥
3. 切换到下一个密钥
4. 重试请求 (最多 3 次)

↓

// 如果所有密钥都失败
throw new Error("所有 API 密钥都已达到速率限制，请稍后重试")
```

### 3. 网络超时

```typescript
// 默认超时: 60 秒
timeout: 60000

↓

// 超时后重试
executeWithRetry() {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await request()
    } catch (error) {
      if (i < maxRetries - 1) {
        await sleep(retryDelay * (i + 1)) // 指数退避
        continue
      }
      throw error
    }
  }
}
```

## 多密钥配置示例

### 配置方式

```
API Key: sk-key1, sk-key2, sk-key3
```

或

```
API Key: 
sk-key1
sk-key2
sk-key3
```

### 工作流程

```typescript
// 初始化
ApiKeyManager.constructor("sk-key1, sk-key2, sk-key3")
→ keys: ["sk-key1", "sk-key2", "sk-key3"]
→ currentIndex: 1  // 随机选择

↓

// 第一次请求使用 sk-key2
Authorization: Bearer sk-key2

↓

// sk-key2 返回 429
1. sk-key2 → 黑名单 (90 秒)
2. 切换到 sk-key3
3. 重试请求

↓

// 90 秒后
sk-key2 自动从黑名单移除，可再次使用
```

## New API 网关特殊支持

### 功能特性

1. **多协议支持**: 一个网关后面可以接多个不同协议的模型
2. **按模型配置协议**: 每个模型可以指定不同的协议
3. **自动 URL 规范化**: 根据目标协议自动调整 URL 路径

### 配置示例

```typescript
{
  platform: "new-api",
  baseUrl: "http://gateway.com",
  apiKey: "sk-gateway-key",
  model: ["gemini-pro", "claude-3", "gpt-4"],
  modelProtocols: {
    "gemini-pro": "gemini",
    "claude-3": "anthropic",
    "gpt-4": "openai"
  }
}
```

### URL 规范化规则

```typescript
// OpenAI 协议
"http://gateway.com" → "http://gateway.com/v1"

// Gemini 协议
"http://gateway.com/v1" → "http://gateway.com"

// Anthropic 协议
"http://gateway.com/v1" → "http://gateway.com"
```

### 协议选择流程

```typescript
// 1. 检查是否明确指定 authType
if (provider.authType) {
  return provider.authType
}

// 2. 检查 New API 的 modelProtocols
if (isNewApiPlatform(provider.platform) && 
    provider.useModel && 
    provider.modelProtocols) {
  const protocol = provider.modelProtocols[provider.useModel]
  if (protocol) {
    return getAuthTypeFromPlatform(protocol)
  }
}

// 3. 根据平台名称推断
return getAuthTypeFromPlatform(provider.platform)
```

## 扩展新平台指南

### 添加预设平台

**步骤 1**: 在 `modelPlatforms.ts` 添加配置

```typescript
{
  name: 'NewPlatform',
  value: 'NewPlatform',
  logo: NewPlatformLogo,
  platform: 'custom',  // 如果兼容 OpenAI 协议
  baseUrl: 'https://api.newplatform.com/v1'
}
```

**步骤 2**: 添加 Logo 图标

将 Logo 文件放到 `src/renderer/assets/logos/` 目录

**步骤 3**: 导入 Logo

```typescript
import NewPlatformLogo from '@/renderer/assets/logos/newplatform.svg';
```

完成！用户即可在界面选择新平台

### 添加新协议支持

如果新平台不兼容 OpenAI 协议，需要：

**步骤 1**: 创建新的 RotatingClient

```typescript
// src/common/adapters/NewPlatformRotatingClient.ts
export class NewPlatformRotatingClient extends RotatingApiClient<NewPlatformSDK> {
  constructor(apiKeys: string, config: NewPlatformConfig, options: RotatingApiClientOptions) {
    const createClient = (apiKey: string) => {
      return new NewPlatformSDK({ apiKey, ...config })
    }
    super(apiKeys, AuthType.USE_NEWPLATFORM, createClient, options)
  }
  
  async createChatCompletion(params: any): Promise<any> {
    return await this.executeWithRetry(async (client) => {
      return await client.chat.create(params)
    })
  }
}
```

**步骤 2**: 在 ClientFactory 添加分支

```typescript
case AuthType.USE_NEWPLATFORM: {
  const clientConfig: NewPlatformConfig = {
    baseURL: baseUrl,
    timeout: options.timeout,
  }
  return new NewPlatformRotatingClient(provider.apiKey, clientConfig, rotatingOptions)
}
```

**步骤 3**: 在 platformAuthType 添加识别规则

```typescript
if (platformLower.includes('newplatform')) {
  return AuthType.USE_NEWPLATFORM
}
```

## 性能优化

### 1. 客户端复用

```typescript
// 同一个 provider 复用客户端实例
const clientCache = new Map<string, RotatingClient>()

function getOrCreateClient(provider: TProviderWithModel): RotatingClient {
  const key = `${provider.id}-${provider.useModel}`
  if (!clientCache.has(key)) {
    clientCache.set(key, ClientFactory.createRotatingClient(provider))
  }
  return clientCache.get(key)
}
```

### 2. 连接池管理

```typescript
// OpenAI SDK 内置连接池
const client = new OpenAI({
  maxRetries: 3,
  timeout: 60000,
  httpAgent: new Agent({
    keepAlive: true,
    maxSockets: 10
  })
})
```

### 3. 流式响应

所有客户端都支持流式响应，减少首字延迟:

```typescript
const stream = await client.createChatCompletion({
  model: "deepseek-chat",
  messages: [...],
  stream: true  // 启用流式
})

for await (const chunk of stream) {
  // 实时显示每个 token
  displayToken(chunk.choices[0].delta.content)
}
```

## 安全考虑

### 1. API 密钥存储

- 密钥加密存储在本地
- 不会上传到服务器
- 使用系统密钥链 (Keychain/Credential Manager)

### 2. 请求头安全

```typescript
defaultHeaders: {
  'HTTP-Referer': 'https://aionui.com',  // 标识来源
  'X-Title': 'AionUi'                    // 应用标识
}
```

### 3. 代理支持

```typescript
// 支持 HTTP/HTTPS 代理
if (options.proxy) {
  const { HttpsProxyAgent } = await import('https-proxy-agent')
  clientConfig.httpAgent = new HttpsProxyAgent(options.proxy)
}
```

## 常见问题

### Q1: 为什么 DeepSeek 是 custom 平台类型？

A: `custom` 表示使用 OpenAI 兼容协议。DeepSeek 虽然是预设平台，但它的 API 完全兼容 OpenAI，所以归类为 `custom`。这样可以复用 OpenAIRotatingClient，无需单独实现。

### Q2: 如何判断一个平台是否兼容 OpenAI？

A: 查看平台文档，如果支持 `/v1/chat/completions` 端点，且请求/响应格式与 OpenAI 一致，就可以使用 `custom` 平台类型。

### Q3: New API 网关和普通平台有什么区别？

A: New API 是一个多模型网关，可以在一个 URL 后面接多个不同协议的模型。普通平台只支持一种协议。

### Q4: 多密钥轮换会影响对话连续性吗？

A: 不会。密钥轮换是透明的，对话历史存储在本地，切换密钥不影响上下文。

### Q5: 如何添加不兼容 OpenAI 的新平台？

A: 需要实现新的 RotatingClient 适配器，参考 GeminiRotatingClient 或 AnthropicRotatingClient 的实现。

## 总结

本项目的多模型支持架构具有以下优势:

1. **高度解耦**: 各层职责清晰，易于维护
2. **易于扩展**: 添加新平台只需配置，无需修改核心代码
3. **统一接口**: 用户无感知切换不同模型
4. **智能容错**: 多密钥轮换、自动重试、黑名单机制
5. **协议自适应**: 自动识别和转换不同协议
6. **性能优化**: 连接池、流式响应、客户端复用

通过这套架构，项目能够快速支持新的 AI 模型平台，为用户提供统一、流畅的使用体验。
