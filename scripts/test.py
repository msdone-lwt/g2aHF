#!/usr/bin/env python3
"""
测试 Clash 配置生成和代理功能
"""

import json
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# 添加脚本路径到 Python 路径
sys.path.insert(0, '/home/appuser/app/scripts')

def test_clash_config_generation():
    """测试 Clash 配置生成"""
    print("=== 测试 Clash 配置生成 ===")
    
    # 测试数据
    test_proxy = {
        "name": "[vmess]日本-iij-0.5x",
        "type": "vmess",
        "server": "141.98.197.233",
        "port": 39688,
        "uuid": "9ad0db3f-9b2f-4dac-a8d3-2f4169ae4024",
        "alterId": 0,
        "cipher": "auto",
        "udp": True,
        "tls": True,
        "skip-cert-verify": True,
        "servername": "hxsis232dxxx.green.nbb.news",
        "network": "ws",
        "ws-opts": {
            "path": "/414sacsa1241235",
            "headers": {"Host": "bing.com"}
        }
    }
    
    # 设置环境变量
    os.environ['CLASH_PROXIES'] = json.dumps(test_proxy)
    
    try:
        from generate_clash_config import generate_clash_config
        config = generate_clash_config()
        
        print("✅ Clash 配置生成成功")
        print(f"代理节点数量: {len(config['proxies'])}")
        if config['proxies']:
            print(f"代理节点名称: {config['proxies'][0]['name']}")
            print(f"代理类型: {config['proxies'][0]['type']}")
        
        return True
    except Exception as e:
        print(f"❌ Clash 配置生成失败: {e}")
        return False

def test_proxy_parsing():
    """测试代理解析功能"""
    print("\n=== 测试代理解析功能 ===")
    
    try:
        sys.path.insert(0, '/home/appuser/app')
        from app.main import parse_clash_proxy
        
        test_proxy = {
            "name": "[vmess]日本-iij-0.5x",
            "type": "vmess",
            "server": "141.98.197.233",
            "port": 39688,
            "uuid": "9ad0db3f-9b2f-4dac-a8d3-2f4169ae4024",
            "alterId": 0,
            "cipher": "auto",
            "udp": True,
            "tls": True,
            "skip-cert-verify": True,
            "servername": "hxsis232dxxx.green.nbb.news",
            "network": "ws",
            "ws-opts": {
                "path": "/414sacsa1241235",
                "headers": {"Host": "bing.com"}
            }
        }
        
        proxy_url = parse_clash_proxy(json.dumps(test_proxy))
        print(f"✅ 代理解析成功: {proxy_url}")
        return True
    except Exception as e:
        print(f"❌ 代理解析失败: {e}")
        return False

def test_docker_build():
    """测试 Docker 构建（可选）"""
    print("\n=== Docker 构建说明 ===")
    print("要测试完整的 Docker 构建，请运行:")
    print("docker build -t gemini-api-proxy .")
    print("docker run -p 7860:7860 -p 1080:1080 -e CLASH_PROXIES='...' gemini-api-proxy")

def main():
    """主测试函数"""
    print("🧪 Gemini API 代理服务测试")
    print("=" * 50)
    
    # 测试配置生成
    config_ok = test_clash_config_generation()
    
    # 测试代理解析
    proxy_ok = test_proxy_parsing()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"Clash 配置生成: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"代理解析功能: {'✅ 通过' if proxy_ok else '❌ 失败'}")
    
    if config_ok and proxy_ok:
        print("\n🎉 所有测试通过！")
        print("\n📝 使用说明:")
        print("1. 设置 CLASH_PROXIES 环境变量")
        print("2. 运行 docker build -t gemini-api-proxy .")
        print("3. 运行 docker run -p 7860:7860 -p 1080:1080 -e CLASH_PROXIES='...' gemini-api-proxy")
        print("4. 访问 http://localhost:7860 查看 API 状态")
    else:
        print("\n❌ 部分测试失败，请检查配置")
        sys.exit(1)
    
    test_docker_build()

if __name__ == '__main__':
    main()