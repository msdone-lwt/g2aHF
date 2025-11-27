---
title: G2
emoji: 🐢
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---
# g2aHF

一个部署在 Hugging Face Spaces 上的 Gemini WebAPI 代理服务。支持 OpenAI 兼容的 Chat Completions API，流式响应，图片输入以及多种代理配置。

## 功能特性

- 🚀 OpenAI 兼容的 Chat Completions API
- 🧰 支持 function call、mcp
- 🔄 支持流式响应 (SSE)
- 🖼️ 支持图片输入 (base64 data URLs)
- 🌐 代理支持 (VMess, VLESS, Trojan, SS, HTTP, SOCKS5)
- 🔐 可选的 API 密钥认证
- 📝 支持思考模式 (ENABLE_THINKING)
- 🐳 Docker 部署支持

## 快速开始

### 环境变量配置
需要在 Hugging Face Spaces 的 Secrets 中设置以下环境变量：
- SECURE_1PSID: 登录 gemini app，打开控制台在 Application - Cookie 找到 PSID
- SECURE_1PSIDTS: 登录 gemini app，打开控制台在 Application - Cookie 找到 PDIDTS
- API_KEY: 自定义的 API 密钥
- ENABLE_THINKING: 可选，是否启用思考模式，默认 false
- CLASH_PROXIES: 由于 gemini 拉黑了 HF 的 IP，建议配置代理，格式为 JSON
支持多种代理类型，配置示例：

#### VMess 节点
```json
{
  "name": "[vmess]节点名称",
  "type": "vmess",
  "server": "your_server_ip",
  "port": your_port,
  "uuid": "your_uuid",
  "alterId": 0,
  "cipher": "auto",
  "udp": true,
  "tls": true,
  "skip-cert-verify": true,
  "servername": "your_servername",
  "network": "ws",
  "ws-opts": {
    "path": "/your_path",
    "headers": {"Host": "your_host"}
  }
}
```

#### 其他代理类型
```bash
# Trojan
CLASH_PROXIES={"name": "[trojan]节点名称", "type": "trojan", "server": "your_server", "port": 443, "password": "your_password", "tls": true}

# Shadowsocks
CLASH_PROXIES={"name": "[ss]节点名称", "type": "ss", "server": "your_server", "port": 8388, "cipher": "aes-256-gcm", "password": "your_password"}

# HTTP 代理
CLASH_PROXIES={"name": "HTTP代理", "type": "http", "server": "proxy.example.com", "port": 8080, "username": "user", "password": "pass"}

# SOCKS5 代理
CLASH_PROXIES={"name": "SOCKS5代理", "type": "socks5", "server": "proxy.example.com", "port": 1080, "username": "user", "password": "pass"}
```
## API 接口

### 1. 服务状态
```
GET /
```

返回服务器状态和配置信息。

### 2. 模型列表
```
GET /v1/models
```

返回所有可用的 Gemini 模型。

### 3. 聊天
```
POST /v1/chat/completions
```

OpenAI 兼容的聊天接口，支持：
- 流式响应 (`stream: true`)
- 图片输入 (base64 data URLs)
- 多种模型选择


本项目仅供学习和研究使用。请遵守相关法律法规和 Google Gemini 的使用条款。
