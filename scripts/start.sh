#!/bin/bash
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 启动 Gemini API 代理服务 ===${NC}"

# 检查环境变量
if [ -z "$CLASH_PROXIES" ]; then
    echo -e "${YELLOW}警告: 未设置 CLASH_PROXIES，将不使用代理${NC}"
    PROXY_MODE=false
else
    echo -e "${GREEN}检测到代理配置，将启动 Clash 服务${NC}"
    PROXY_MODE=true
fi

# 创建必要的目录
mkdir -p /tmp/clash
mkdir -p /tmp/gemini_webapi

# 生成 Clash 配置
if [ "$PROXY_MODE" = true ]; then
    echo -e "${GREEN}生成 Clash 配置...${NC}"
    python3 /home/appuser/app/scripts/generate_clash_config.py
    
    # 检查配置是否生成成功
    if [ ! -f "/tmp/clash/config.yaml" ]; then
        echo -e "${RED}错误: Clash 配置生成失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Clash 配置生成成功${NC}"
    
    # 启动 Clash 服务（后台运行）
    echo -e "${GREEN}启动 Clash 服务...${NC}"
    clash -d /tmp/clash > /tmp/clash.log 2>&1 &
    CLASH_PID=$!
    
    echo -e "${GREEN}Clash 服务已启动 (PID: $CLASH_PID)${NC}"
    
    # 等待 Clash 启动
    echo -e "${GREEN}等待 Clash 服务启动...${NC}"
    sleep 5
    
    # 检查 Clash 是否正常运行
    if ! kill -0 $CLASH_PID 2>/dev/null; then
        echo -e "${RED}错误: Clash 服务启动失败${NC}"
        cat /tmp/clash.log
        exit 1
    fi
    
    # 检查代理端口是否可用
    echo -e "${GREEN}检查代理端口...${NC}"
    timeout 10 bash -c 'until echo > /dev/tcp/127.0.0.1/1080; do sleep 1; done' || {
        echo -e "${RED}错误: 代理端口 1080 不可用${NC}"
        cat /tmp/clash.log
        exit 1
    }
    
    echo -e "${GREEN}代理端口 1080 可用${NC}"
fi

# 启动 FastAPI 服务
echo -e "${GREEN}启动 FastAPI 服务...${NC}"
if [ "$PROXY_MODE" = true ]; then
    echo -e "${GREEN}代理模式: 通过 Clash (socks5://127.0.0.1:1080)${NC}"
else
    echo -e "${YELLOW}直连模式: 不使用代理${NC}"
fi

# 启动 uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}