#!/usr/bin/env python3
"""
Socket Client Test Program
用于测试C++Socket服务器的Python客户端
"""

import socket
import threading
import time
import sys

class SocketClient:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.receive_thread = None
        
    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ 成功连接到服务器 {self.host}:{self.port}")
            
            # 启动接收消息的线程
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
                print("✓ 已断开连接")
            except:
                pass
    
    def send_message(self, message):
        """发送消息到服务器"""
        if not self.connected or not self.socket:
            print("✗ 未连接到服务器")
            return False
        
        try:
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"✗ 发送消息失败: {e}")
            self.connected = False
            return False
    
    def _receive_messages(self):
        """接收服务器消息的线程函数"""
        while self.connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    print("✗ 服务器关闭了连接")
                    self.connected = False
                    break
                
                message = data.decode('utf-8')
                print(f"📨 服务器回复: {message.strip()}")
                
            except Exception as e:
                if self.connected:
                    print(f"✗ 接收消息时出错: {e}")
                break

def print_help():
    """打印帮助信息"""
    print("\n=== Socket Client 帮助 ===")
    print("命令:")
    print("  hello          - 发送hello消息")
    print("  time           - 获取服务器时间")
    print("  quit/exit      - 退出客户端")
    print("  help           - 显示此帮助")
    print("  test           - 运行自动测试")
    print("  其他任何文本    - 发送自定义消息")
    print("========================\n")

def auto_test(client):
    """自动测试功能"""
    print("\n🔄 开始自动测试...")
    
    test_messages = [
        "hello",
        "time", 
        "这是一条测试消息",
        "Test message in English",
        "quit"
    ]
    
    for i, msg in enumerate(test_messages):
        print(f"\n📤 测试 {i+1}/{len(test_messages)}: 发送 '{msg}'")
        if client.send_message(msg):
            time.sleep(1)  # 等待响应
        else:
            print("❌ 测试失败")
            break
    
    print("\n✅ 自动测试完成")

def interactive_mode(client):
    """交互模式"""
    print("\n🎯 进入交互模式")
    print("输入 'help' 查看可用命令")
    
    while client.connected:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit']:
                print("👋 正在退出...")
                client.send_message(user_input)
                time.sleep(0.5)  # 等待服务器响应
                break
            elif user_input.lower() == 'help':
                print_help()
            elif user_input.lower() == 'test':
                auto_test(client)
            else:
                client.send_message(user_input)
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在退出...")
            break
        except EOFError:
            print("\n👋 输入结束，正在退出...")
            break

def main():
    print("🚀 Socket Client 测试程序")
    print("=" * 40)
    
    # 解析命令行参数
    host = 'localhost'
    port = 8080
    
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("❌ 无效的端口号")
            sys.exit(1)
    
    print(f"🎯 目标服务器: {host}:{port}")
    
    # 创建客户端并连接
    client = SocketClient(host, port)
    
    if not client.connect():
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        sys.exit(1)
    
    try:
        # 选择运行模式
        print("\n选择运行模式:")
        print("1. 交互模式 (默认)")
        print("2. 自动测试模式")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == '2':
            auto_test(client)
        else:
            interactive_mode(client)
            
    except Exception as e:
        print(f"❌ 程序异常: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
