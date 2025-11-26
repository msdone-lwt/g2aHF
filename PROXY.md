# 代理配置说明

## 🚀 Docker 集成 Clash 代理

本项目已完全集成 Clash 代理服务，无需外部 Clash 客户端。Docker 容器会自动启动 Clash 服务并连接指定节点。

## 📦 快速开始

### 1. 构建镜像

```bash
docker build -t gemini-api-proxy .
```

### 2. 运行容器

```bash
# 设置代理节点信息并运行
docker run -d \
  --name gemini-api \
  -p 7860:7860 \
  -p 1080:1080 \
  -e CLASH_PROXIES='{
    "name": "[vmess]日本-iij-0.5x",
    "type": "vmess",
    "server": "141.98.197.233",
    "port": 39688,
    "uuid": "9ad0db3f-9b2f-4dac-a8d3-2f4169ae4024",
    "alterId": 0,
    "cipher": "auto",
    "udp": true,
    "tls": true,
    "skip-cert-verify": true,
    "servername": "hxsis232dxxx.green.nbb.news",
    "network": "ws",
    "ws-opts": {
      "path": "/414sacsa1241235",
      "headers": {"Host": "bing.com"}
    }
  }' \
  -e SECURE_1PSID="your_1psid" \
  -e SECURE_1PSIDTS="your_1psidts" \
  gemini-api-proxy
```

### 3. 验证服务

```bash
# 检查 API 状态
curl http://localhost:7860/

# 检查代理状态
curl http://localhost:7860/ | jq '.proxy_info'
```

## 🔧 环境变量配置

### CLASH_PROXIES 环境变量

设置 `CLASH_PROXIES` 环境变量来配置代理节点。支持以下代理类型：

#### 支持的代理类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **vmess** | V2Ray VMess 协议 | 见下方示例 |
| **vless** | V2Ray VLESS 协议 | 类似 vmess，无 alterId |
| **trojan** | Trojan 协议 | 需要 password 字段 |
| **ss** | Shadowsocks 协议 | 需要 cipher 和 password |
| **ssr** | ShadowsocksR 协议 | 需要 protocol 和 obfs |
| **http** | HTTP 代理 | 需要 username/password |
| **socks5** | SOCKS5 代理 | 需要 username/password |

#### 完整配置示例

```bash
# VMess 节点（推荐）
export CLASH_PROXIES='{
  "name": "[vmess]日本-iij-0.5x",
  "type": "vmess",
  "server": "141.98.197.233",
  "port": 39688,
  "uuid": "9ad0db3f-9b2f-4dac-a8d3-2f4169ae4024",
  "alterId": 0,
  "cipher": "auto",
  "udp": true,
  "tls": true,
  "skip-cert-verify": true,
  "servername": "hxsis232dxxx.green.nbb.news",
  "network": "ws",
  "ws-opts": {
    "path": "/414sacsa1241235",
    "headers": {"Host": "bing.com"}
  }
}'

# Trojan 节点
export CLASH_PROXIES='{
  "name": "[trojan]美国",
  "type": "trojan",
  "server": "trojan.example.com",
  "port": 443,
  "password": "your_password",
  "udp": true,
  "tls": true,
  "skip-cert-verify": false,
  "servername": "trojan.example.com"
}'

# Shadowsocks 节点
export CLASH_PROXIES='{
  "name": "[ss]新加坡",
  "type": "ss",
  "server": "ss.example.com",
  "port": 8388,
  "cipher": "aes-256-gcm",
  "password": "your_password",
  "udp": true
}'
```

## 🏗️ 架构说明

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gemini API    │    │   Clash 服务     │    │   外部代理节点    │
│   (FastAPI)     │───▶│   (127.0.0.1:1080)│───▶│   (vmess/trojan) │
│   :7860         │    │   自动配置       │    │   :39688        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

1. **FastAPI 应用** 监听 7860 端口
2. **Clash 服务** 在容器内运行，监听 1080 端口
3. **Gemini API 请求** 通过 `socks5://127.0.0.1:1080` 转发到外部代理节点

## 📊 监控和调试

### 查看服务状态

```bash
# 查看容器日志
docker logs gemini-api

# 查看 Clash 日志
docker exec gemini-api cat /tmp/clash.log

# 检查代理配置
docker exec gemini-api cat /tmp/clash/config.yaml
```

### API 状态检查

```bash
# 根路径显示完整状态
curl http://localhost:7860/ | jq

# 返回示例
{
  "status": "online",
  "message": "Gemini API FastAPI Server is running",
  "proxy_enabled": true,
  "proxy_info": {
    "name": "[vmess]日本-iij-0.5x",
    "type": "vmess",
    "server": "141.98.197.233",
    "port": 39688
  }
}
```

## 🛠️ 开发和测试

### 本地测试

```bash
# 测试配置生成
python3 scripts/test.py

# 手动生成 Clash 配置
python3 scripts/generate_clash_config.py
```

### 故障排除

1. **代理连接失败**
   - 检查节点信息是否正确
   - 确认外部代理节点可访问
   - 查看 Clash 日志：`docker logs gemini-api`

2. **配置错误**
   - 验证 JSON 格式是否正确
   - 检查必填字段是否完整
   - 使用测试脚本验证：`python3 scripts/test.py`

3. **端口冲突**
   - 确保 1080 端口未被占用
   - 检查防火墙设置

## 📝 注意事项

- ✅ **自动启动**：容器启动时自动配置和启动 Clash 服务
- ✅ **智能转换**：所有代理类型自动转换为本地 SOCKS5 代理
- ✅ **健康检查**：启动时验证代理端口可用性
- ✅ **日志记录**：详细的启动和运行日志
- ✅ **容错机制**：代理失败时自动回退到直连模式

## 🔄 更新和维护

```bash
# 重新构建镜像
docker build -t gemini-api-proxy .

# 停止旧容器
docker stop gemini-api && docker rm gemini-api

# 启动新容器
docker run -d ... (同上)
```