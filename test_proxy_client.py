#!/usr/bin/env python3
"""
测试代理功能的示例脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_transfer_client import FileTransferClient, print_usage

def test_direct_connection():
    """测试直接连接"""
    print("=== 测试直接连接 ===")
    client = FileTransferClient('localhost', 8080)
    
    if client.connect():
        print("✅ 直接连接测试成功")
        client.send_message("hello")
        client.disconnect()
    else:
        print("❌ 直接连接测试失败")

def test_proxy_connection():
    """测试代理连接"""
    print("\n=== 测试代理连接 ===")
    # 这里使用示例代理地址，实际使用时需要替换为真实的代理地址
    proxy_host = "192.168.1.50"  # 代理服务器IP
    proxy_port = 9999           # 代理服务器端口
    target_host = "192.168.1.100"  # 目标服务器IP
    target_port = 8080          # 目标服务器端口
    
    client = FileTransferClient(target_host, target_port, proxy_host, proxy_port)
    
    if client.connect():
        print("✅ 代理连接测试成功")
        client.send_message("hello")
        client.disconnect()
    else:
        print("❌ 代理连接测试失败")

def main():
    print("🧪 代理功能测试脚本")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        print("\n测试脚本说明:")
        print("1. 确保目标服务器正在运行")
        print("2. 如果测试代理连接，确保代理服务器正在运行")
        print("3. 修改脚本中的IP地址和端口号")
        return
    
    print("注意: 请在运行测试前确保相关服务器正在运行")
    print("您可以修改脚本中的IP地址和端口号以匹配您的环境")
    print()
    
    # 测试直接连接
    test_direct_connection()
    
    # 询问是否测试代理连接
    response = input("\n是否测试代理连接? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        test_proxy_connection()
    
    print("\n测试完成")

if __name__ == "__main__":
    main()
