#!/usr/bin/env python3
"""
支持文件传输的Socket客户端
"""

import socket
import os
import sys
import threading
import time
from pathlib import Path

class FileTransferClient:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✅ 成功连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
                print("✅ 已断开连接")
            except:
                pass
    
    def send_message(self, message):
        """发送普通消息"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return False
        
        try:
            self.socket.send(message.encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            print(f"📨 服务器回复:\n{response}")
            return True
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False
    
    def upload_file(self, local_file_path):
        """上传文件到服务器"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return False
        
        if not os.path.exists(local_file_path):
            print(f"❌ 文件不存在: {local_file_path}")
            return False
        
        try:
            # 获取文件信息
            file_size = os.path.getsize(local_file_path)
            filename = os.path.basename(local_file_path)
            
            print(f"📤 开始上传文件: {filename} ({file_size} bytes)")
            
            # 发送上传命令
            upload_command = f"FILE:UPLOAD:{filename}:{file_size}"
            self.socket.send(upload_command.encode('utf-8'))
            
            # 等待服务器确认
            response = self.socket.recv(1024).decode('utf-8')
            if "READY" not in response:
                print(f"❌ 服务器不准备接收文件: {response}")
                return False
            
            # 发送文件数据
            with open(local_file_path, 'rb') as file:
                bytes_sent = 0
                buffer_size = 8192
                
                while bytes_sent < file_size:
                    data = file.read(buffer_size)
                    if not data:
                        break
                    
                    self.socket.send(data)
                    bytes_sent += len(data)
                    
                    # 显示进度
                    progress = (bytes_sent / file_size) * 100
                    print(f"📊 上传进度: {progress:.1f}% ({bytes_sent}/{file_size} bytes)", end='\r')
            
            print(f"\n✅ 文件上传成功: {filename}")
            
            # 接收最终确认
            final_response = self.socket.recv(1024).decode('utf-8')
            print(f"📨 服务器确认: {final_response.strip()}")
            
            return True
            
        except Exception as e:
            print(f"❌ 上传文件失败: {e}")
            return False
    
    def download_file(self, filename, local_dir="./downloads"):
        """从服务器下载文件"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return False
        
        try:
            # 确保下载目录存在
            os.makedirs(local_dir, exist_ok=True)
            
            print(f"📥 开始下载文件: {filename}")
            
            # 发送下载命令
            download_command = f"FILE:DOWNLOAD:{filename}"
            self.socket.send(download_command.encode('utf-8'))
            
            # 接收文件信息
            response = self.socket.recv(1024).decode('utf-8')
            
            if response.startswith("ERROR"):
                print(f"❌ 下载失败: {response}")
                return False
            
            if not response.startswith("FILE_INFO:"):
                print(f"❌ 意外的服务器响应: {response}")
                return False
            
            # 解析文件大小
            file_size = int(response.split(':')[1].strip())
            print(f"📋 文件大小: {file_size} bytes")
            
            # 发送准备确认
            self.socket.send("READY".encode('utf-8'))
            
            # 接收文件数据
            local_file_path = os.path.join(local_dir, filename)
            bytes_received = 0
            
            with open(local_file_path, 'wb') as file:
                while bytes_received < file_size:
                    remaining = file_size - bytes_received
                    buffer_size = min(8192, remaining)
                    
                    data = self.socket.recv(buffer_size)
                    if not data:
                        break
                    
                    file.write(data)
                    bytes_received += len(data)
                    
                    # 显示进度
                    progress = (bytes_received / file_size) * 100
                    print(f"📊 下载进度: {progress:.1f}% ({bytes_received}/{file_size} bytes)", end='\r')
            
            print(f"\n✅ 文件下载成功: {local_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 下载文件失败: {e}")
            return False
    
    def list_files(self):
        """列出服务器上的文件"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return False
        
        try:
            # 发送列表命令
            self.socket.send("FILE:LIST".encode('utf-8'))
            
            # 接收文件列表
            response = self.socket.recv(4096).decode('utf-8')
            
            if response.startswith("FILE_LIST:"):
                print("📂 服务器文件列表:")
                lines = response.split('\n')
                file_count = 0
                
                for line in lines[1:]:  # 跳过第一行 "FILE_LIST:"
                    if line.strip() == "END_LIST":
                        break
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            filename = parts[0]
                            file_size = parts[1]
                            print(f"  📄 {filename} ({file_size} bytes)")
                            file_count += 1
                
                print(f"总共 {file_count} 个文件")
            else:
                print(f"❌ 获取文件列表失败: {response}")
            
            return True
            
        except Exception as e:
            print(f"❌ 列出文件失败: {e}")
            return False

def print_help():
    """显示帮助信息"""
    print("\n📋 可用命令:")
    print("文件操作:")
    print("  📤 up <文件>         - 上传文件 (别名: upload, u)")
    print("  📥 down <文件>       - 下载文件 (别名: download, d)")
    print("  📂 ls               - 列出文件 (别名: list, l)")
    print("")
    print("其他命令:")
    print("  💬 hello            - 服务器问候")
    print("  🕒 time             - 服务器时间")
    print("  ❓ help             - 显示帮助 (别名: h, ?)")
    print("  🚪 quit             - 退出程序 (别名: exit, q)")
    print("")
    print("💡 提示: 输入其他文本将直接发送给服务器")
    print("=" * 45)

def main():
    print("🚀 文件传输客户端")
    print("=" * 30)
    
    # 解析命令行参数
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    client = FileTransferClient(host, port)
    
    if not client.connect():
        sys.exit(1)
    
    print("🎯 连接成功！输入 'help' 或 'h' 查看命令")
    
    try:
        while client.connected:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            
            # 退出命令 (支持多种别名)
            if command in ['quit', 'exit', 'q']:
                print("👋 正在断开连接...")
                client.send_message("quit")
                break
                
            # 帮助命令 (支持多种别名)
            elif command in ['help', 'h', '?']:
                print_help()
                
            # 上传命令 (支持多种别名)
            elif command in ['upload', 'up', 'u']:
                if len(parts) < 2:
                    print("❌ 请指定要上传的文件")
                    print("💡 用法: up <文件路径>")
                    print("📝 例如: up test.txt 或 up ./documents/file.pdf")
                else:
                    file_path = ' '.join(parts[1:])  # 支持带空格的文件名
                    client.upload_file(file_path)
                    
            # 下载命令 (支持多种别名)
            elif command in ['download', 'down', 'd']:
                if len(parts) < 2:
                    print("❌ 请指定要下载的文件名")
                    print("💡 用法: down <文件名>")
                    print("📝 例如: down test.txt")
                else:
                    filename = parts[1]
                    client.download_file(filename)
                    
            # 列表命令 (支持多种别名)
            elif command in ['list', 'ls', 'l']:
                client.list_files()
                
            # 其他已知命令
            elif command in ['hello', 'time']:
                client.send_message(user_input)
                
            # 未知命令处理
            else:
                # 如果输入看起来像是错误的命令，给出提示
                if len(parts) == 1 and len(command) > 1:
                    similar_commands = {
                        'upload': ['up', 'u'],
                        'download': ['down', 'd'], 
                        'list': ['ls', 'l'],
                        'help': ['h', '?'],
                        'quit': ['q', 'exit']
                    }
                    
                    suggestions = []
                    for cmd, aliases in similar_commands.items():
                        if command.startswith(cmd[:2]) or command in aliases:
                            suggestions.append(f"'{cmd}' 或 '{aliases[0]}'")
                    
                    if suggestions:
                        print(f"❓ 未知命令 '{command}'，您是否想输入: {', '.join(suggestions)}?")
                        print("💡 输入 'h' 查看所有可用命令")
                    else:
                        print(f"📨 发送消息: {user_input}")
                        client.send_message(user_input)
                else:
                    print(f"📨 发送消息: {user_input}")
                    client.send_message(user_input)
                
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
    except EOFError:
        print("\n👋 输入结束，正在退出...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
