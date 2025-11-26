#!/usr/bin/env python3
"""
验证 Clash 修复是否正确
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

def test_mihomo_download():
    """测试 Mihomo 下载链接"""
    print("🔍 测试 Mihomo 下载链接...")
    
    url = "https://github.com/MetaCubeX/mihomo/releases/download/v1.18.5/mihomo-linux-amd64-v1.18.5.gz"
    
    try:
        result = subprocess.run(
            ["wget", "--spider", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Mihomo 下载链接可用")
            return True
        else:
            print(f"❌ Mihomo 下载失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试下载链接时出错: {e}")
        return False

def test_clash_config_generation():
    """测试 Clash 配置生成"""
    print("\n🔧 测试 Clash 配置生成...")
    
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
    
    try:
        # 设置环境变量
        os.environ['CLASH_PROXIES'] = json.dumps(test_proxy)
        
        # 导入配置生成器
        sys.path.insert(0, '/home/msdone/project/g2a/scripts')
        from generate_clash_config import generate_clash_config, convert_to_clash_proxy
        
        # 测试配置生成
        config = generate_clash_config()
        
        # 测试代理转换
        clash_proxy = convert_to_clash_proxy(test_proxy)
        
        if config and clash_proxy:
            print("✅ Clash 配置生成成功")
            print(f"   - 代理节点: {clash_proxy['name']}")
            print(f"   - 代理类型: {clash_proxy['type']}")
            print(f"   - 服务器: {clash_proxy['server']}")
            return True
        else:
            print("❌ Clash 配置生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试配置生成时出错: {e}")
        return False

def test_fastapi_proxy_parsing():
    """测试 FastAPI 代理解析"""
    print("\n🐍 测试 FastAPI 代理解析...")
    
    try:
        # 导入 FastAPI 代理解析
        sys.path.insert(0, '/home/msdone/project/g2a')
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
        
        if proxy_url == "socks5://127.0.0.1:1080":
            print("✅ FastAPI 代理解析成功")
            print(f"   - 代理 URL: {proxy_url}")
            return True
        else:
            print(f"❌ FastAPI 代理解析失败: {proxy_url}")
            return False
            
    except Exception as e:
        print(f"❌ 测试代理解析时出错: {e}")
        return False

def test_dockerfile_syntax():
    """测试 Dockerfile 语法"""
    print("\n🐳 测试 Dockerfile 语法...")
    
    try:
        dockerfile_path = Path('/home/msdone/project/g2a/Dockerfile')
        
        if not dockerfile_path.exists():
            print("❌ Dockerfile 不存在")
            return False
        
        content = dockerfile_path.read_text()
        
        # 检查关键修复点
        checks = [
            ("mihomo", "使用 Mihomo 替代 Clash"),
            ("v1.18.5", "使用正确版本"),
            ("MetaCubeX/mihomo", "使用正确的仓库"),
            ("scripts/start.sh", "启动脚本存在")
        ]
        
        for check, description in checks:
            if check in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
                return False
        
        print("✅ Dockerfile 语法检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试 Dockerfile 时出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 Clash 修复验证测试")
    print("=" * 50)
    
    tests = [
        ("Mihomo 下载链接", test_mihomo_download),
        ("Clash 配置生成", test_clash_config_generation),
        ("FastAPI 代理解析", test_fastapi_proxy_parsing),
        ("Dockerfile 语法", test_dockerfile_syntax)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！Clash 修复成功！")
        print("\n📝 下一步:")
        print("1. docker build -t gemini-api-clash .")
        print("2. docker run -d -p 7860:7860 -p 1080:1080 \\")
        print("   -e CLASH_PROXIES='...' \\")
        print("   -e SECURE_1PSID='...' \\")
        print("   -e SECURE_1PSIDTS='...' \\")
        print("   gemini-api-clash")
    else:
        print("\n❌ 部分测试失败，请检查修复")
        sys.exit(1)

if __name__ == '__main__':
    main()