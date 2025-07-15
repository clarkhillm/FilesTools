#!/usr/bin/env python3
"""
简单的Socket客户端测试工具
"""

import socket
import sys

def test_server(host='localhost', port=8080):
    """测试服务器连接和基本功能"""
    try:
        # 创建socket连接
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"✓ 成功连接到 {host}:{port}")
        
        # 测试消息列表
        test_messages = [
            "hello",
            "time",
            "This is a test message",
            "quit"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n📤 发送: {message}")
            
            # 发送消息
            client_socket.send(message.encode('utf-8'))
            
            # 接收响应
            response = client_socket.recv(1024).decode('utf-8')
            print(f"📨 响应: {response.strip()}")
            
            # 如果是quit命令，就退出
            if message == "quit":
                break
        
        client_socket.close()
        print("\n✅ 测试完成")
        
    except ConnectionRefusedError:
        print(f"❌ 无法连接到 {host}:{port} - 请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("🔧 Socket服务器简单测试工具")
    print("-" * 30)
    
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    test_server(host, port)
