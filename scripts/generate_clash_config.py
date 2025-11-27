#!/usr/bin/env python3
"""
Clash 配置生成器
根据 CLASH_PROXIES 环境变量动态生成 Clash 配置文件
"""

import json
import os
import sys
import yaml
from pathlib import Path


def generate_clash_config():
    """生成 Clash 配置文件"""
    
    # 基础 Clash 配置 - 全局代理模式
    config = {
        'mixed-port': 1080,
        'allow-lan': False,
        'bind-address': '127.0.0.1',
        'mode': 'global',  # 设置为全局代理模式
        'log-level': 'info',
        'external-controller': '127.0.0.1:9090',
        'dns': {
            'enable': True,
            'ipv6': False,
            'default-nameserver': ['223.5.5.5', '114.114.114.114'],
            'nameserver': ['223.5.5.5', '114.114.114.114']
        },
        'proxies': [],
        'proxy-groups': [
            {
                'name': 'PROXY',
                'type': 'select',
                'proxies': ['DIRECT'],
                'url': 'http://www.gstatic.com/generate_204'
            }
        ],
        'rules': [
            'GEOIP,CN,DIRECT',
            'MATCH,PROXY'
        ]
    }
    
    # 解析 CLASH_PROXIES 环境变量
    clash_proxies = os.getenv('CLASH_PROXIES', '')
    if not clash_proxies:
        print("警告: 未设置 CLASH_PROXIES 环境变量，将不使用代理", file=sys.stderr)
        return config
    
    try:
        proxy_config = json.loads(clash_proxies)
        
        # 转换为 Clash 代理格式
        clash_proxy = convert_to_clash_proxy(proxy_config)
        if clash_proxy:
            config['proxies'].append(clash_proxy)
            # 在全局模式下，设置默认代理
            config['proxy-groups'][0]['proxies'].insert(0, clash_proxy['name'])
            print(f"成功添加代理节点: {clash_proxy['name']} (全局代理模式)")
        else:
            print("警告: 代理配置转换失败", file=sys.stderr)
            
    except json.JSONDecodeError as e:
        print(f"错误: 解析 CLASH_PROXIES 失败: {e}", file=sys.stderr)
    except Exception as e:
        print(f"错误: 处理代理配置时出错: {e}", file=sys.stderr)
    
    return config


def convert_to_clash_proxy(proxy_config):
    """将代理配置转换为 Clash 格式"""
    
    proxy_type = proxy_config.get('type', '').lower()
    name = proxy_config.get('name', f'proxy-{proxy_type}')
    
    if proxy_type == 'vmess':
        return {
            'name': name,
            'type': 'vmess',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'uuid': proxy_config.get('uuid'),
            'alterId': proxy_config.get('alterId', 0),
            'cipher': proxy_config.get('cipher', 'auto'),
            'udp': proxy_config.get('udp', True),
            'tls': proxy_config.get('tls', False),
            'skip-cert-verify': proxy_config.get('skip-cert-verify', False),
            'servername': proxy_config.get('servername'),
            'network': proxy_config.get('network', 'tcp'),
            'ws-opts': proxy_config.get('ws-opts', {}),
            'http-opts': proxy_config.get('http-opts', {}),
            'h2-opts': proxy_config.get('h2-opts', {})
        }
    
    elif proxy_type == 'vless':
        return {
            'name': name,
            'type': 'vless',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'uuid': proxy_config.get('uuid'),
            'udp': proxy_config.get('udp', True),
            'tls': proxy_config.get('tls', False),
            'skip-cert-verify': proxy_config.get('skip-cert-verify', False),
            'servername': proxy_config.get('servername'),
            'network': proxy_config.get('network', 'tcp'),
            'ws-opts': proxy_config.get('ws-opts', {}),
            'http-opts': proxy_config.get('http-opts', {}),
            'h2-opts': proxy_config.get('h2-opts', {})
        }
    
    elif proxy_type == 'trojan':
        return {
            'name': name,
            'type': 'trojan',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'password': proxy_config.get('password'),
            'udp': proxy_config.get('udp', True),
            'tls': proxy_config.get('tls', True),
            'skip-cert-verify': proxy_config.get('skip-cert-verify', False),
            'servername': proxy_config.get('servername'),
            'alpn': proxy_config.get('alpn', ['http/1.1']),
            'sni': proxy_config.get('sni')
        }
    
    elif proxy_type == 'ss':
        return {
            'name': name,
            'type': 'ss',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'cipher': proxy_config.get('cipher'),
            'password': proxy_config.get('password'),
            'udp': proxy_config.get('udp', True)
        }
    
    elif proxy_type == 'ssr':
        return {
            'name': name,
            'type': 'ssr',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'cipher': proxy_config.get('cipher'),
            'password': proxy_config.get('password'),
            'protocol': proxy_config.get('protocol'),
            'obfs': proxy_config.get('obfs'),
            'udp': proxy_config.get('udp', True)
        }
    
    elif proxy_type == 'http':
        return {
            'name': name,
            'type': 'http',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'username': proxy_config.get('username'),
            'password': proxy_config.get('password'),
            'tls': proxy_config.get('tls', False),
            'skip-cert-verify': proxy_config.get('skip-cert-verify', False)
        }
    
    elif proxy_type == 'socks5':
        return {
            'name': name,
            'type': 'socks5',
            'server': proxy_config.get('server'),
            'port': proxy_config.get('port'),
            'username': proxy_config.get('username'),
            'password': proxy_config.get('password'),
            'tls': proxy_config.get('tls', False),
            'skip-cert-verify': proxy_config.get('skip-cert-verify'),
            'udp': proxy_config.get('udp', True)
        }
    
    else:
        print(f"错误: 不支持的代理类型: {proxy_type}", file=sys.stderr)
        return None


def main():
    """主函数"""
    config = generate_clash_config()
    
    # 输出配置到标准输出（用于调试）
    print("生成的 Clash 配置:", json.dumps(config, indent=2, ensure_ascii=False))
    
    # 保存配置文件
    config_dir = Path('/tmp/clash')
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / 'config.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"Clash 配置已保存到: {config_file}")
    
    # 设置权限
    os.chmod(config_file, 0o644)


if __name__ == '__main__':
    main()