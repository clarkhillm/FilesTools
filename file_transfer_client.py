#!/usr/bin/env python3
"""
支持文件传输和代理连接的Socket客户端
"""

import socket
import os
import sys
import threading
import time
import struct
from pathlib import Path

# 代理相关常量
VRC_PROXY_STATUS_OK = 0
VRC_PROXY_STATUS_CONNECT_ERR = 1

class ProxyRequest:
    """代理请求结构 - 对应C++的ProxyRequest"""
    def __init__(self, target_ip, target_port):
        # 确保IP地址是16字节，不足的用空字符填充
        ip_bytes = target_ip.encode('utf-8')
        if len(ip_bytes) > 16:
            ip_bytes = ip_bytes[:16]
        else:
            ip_bytes = ip_bytes + b'\0' * (16 - len(ip_bytes))
        self.target_ip = ip_bytes
        self.target_port = target_port
    
    def pack(self):
        """打包为二进制数据发送给代理"""
        return struct.pack('16sH', self.target_ip, self.target_port)

class ProxyResponse:
    """代理响应结构 - 对应C++的ProxyResponse"""
    def __init__(self, data):
        if len(data) != 102:  # 2 + 100 bytes
            raise ValueError(f"Expected 102 bytes, got {len(data)}")
        
        self.status, msg_bytes = struct.unpack('H100s', data)
        # 移除空字符并解码消息
        self.msg = msg_bytes.decode('utf-8', errors='ignore').rstrip('\0')
    
    def is_success(self):
        return self.status == VRC_PROXY_STATUS_OK

class FileTransferClient:
    def __init__(self, host='localhost', port=8080, proxy_host=None, proxy_port=None):
        self.host = host
        self.port = port
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.socket = None
        self.connected = False
        self.using_proxy = proxy_host is not None and proxy_port is not None
        
    def connect(self):
        """连接到服务器（直接连接或通过代理）"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)  # 设置30秒超时，避免无限等待
            
            if self.using_proxy:
                return self._connect_via_proxy()
            else:
                return self._connect_direct()
                
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def _connect_direct(self):
        """直接连接到服务器"""
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✅ 成功直接连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 直接连接失败: {e}")
            return False
    
    def _connect_via_proxy(self):
        """通过代理连接到服务器"""
        try:
            # 1. 连接到代理服务器
            print(f"🔄 正在连接到代理服务器 {self.proxy_host}:{self.proxy_port}")
            self.socket.connect((self.proxy_host, self.proxy_port))
            
            # 2. 发送代理请求
            proxy_request = ProxyRequest(self.host, self.port)
            request_data = proxy_request.pack()
            
            print(f"📡 发送代理请求: {self.host}:{self.port}")
            self.socket.send(request_data)
            
            # 3. 接收代理响应
            response_data = self.socket.recv(102)  # ProxyResponse大小固定为102字节
            if len(response_data) != 102:
                print(f"❌ 代理响应长度错误: 期望102字节，收到{len(response_data)}字节")
                return False
            
            proxy_response = ProxyResponse(response_data)
            
            # 4. 检查代理连接状态
            if proxy_response.is_success():
                self.connected = True
                print(f"✅ 成功通过代理连接到服务器 {self.host}:{self.port}")
                print(f"📝 代理响应: {proxy_response.msg}")
                return True
            else:
                print(f"❌ 代理连接失败 (状态码: {proxy_response.status})")
                print(f"📝 错误信息: {proxy_response.msg}")
                return False
                
        except Exception as e:
            print(f"❌ 代理连接失败: {e}")
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
        
        # 检查是否是文件夹
        if os.path.isdir(local_file_path):
            return self.upload_folder(local_file_path)
        
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
    
    def upload_folder(self, folder_path):
        """上传整个文件夹到服务器"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return False
        
        if not os.path.isdir(folder_path):
            print(f"❌ 文件夹不存在: {folder_path}")
            return False
        
        try:
            # 获取文件夹名称
            folder_name = os.path.basename(os.path.abspath(folder_path))
            
            # 收集所有文件
            files_to_upload = []
            total_size = 0
            
            print(f"📁 正在扫描文件夹: {folder_name}")
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径以保持目录结构
                    relative_path = os.path.relpath(file_path, folder_path)
                    # 使用正斜杠作为路径分隔符（跨平台兼容）
                    relative_path = relative_path.replace('\\', '/')
                    server_filename = f"{folder_name}/{relative_path}"
                    
                    file_size = os.path.getsize(file_path)
                    files_to_upload.append((file_path, server_filename, file_size))
                    total_size += file_size
            
            if not files_to_upload:
                print(f"❌ 文件夹为空: {folder_path}")
                return False
            
            print(f"📊 发现 {len(files_to_upload)} 个文件，总大小: {total_size} bytes")
            
            # 询问用户确认
            try:
                response = input(f"确认上传文件夹 '{folder_name}' 吗? (y/N): ").strip().lower()
                if response not in ['y', 'yes', '是']:
                    print("❌ 用户取消上传")
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\n❌ 用户取消上传")
                return False
            
            # 上传所有文件
            successful_uploads = 0
            failed_uploads = 0
            
            for i, (local_path, server_filename, file_size) in enumerate(files_to_upload, 1):
                print(f"\n📤 上传文件 {i}/{len(files_to_upload)}: {server_filename}")
                
                if self._upload_single_file(local_path, server_filename, file_size):
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                    print(f"❌ 文件上传失败: {server_filename}")
            
            # 显示上传结果
            print(f"\n📊 文件夹上传完成:")
            print(f"  ✅ 成功: {successful_uploads} 个文件")
            if failed_uploads > 0:
                print(f"  ❌ 失败: {failed_uploads} 个文件")
            
            return failed_uploads == 0
            
        except Exception as e:
            print(f"❌ 上传文件夹失败: {e}")
            return False
    
    def _upload_single_file(self, local_file_path, server_filename, file_size):
        """上传单个文件（内部使用）"""
        try:
            # 发送上传命令
            upload_command = f"FILE:UPLOAD:{server_filename}:{file_size}"
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
                    print(f"  📊 进度: {progress:.1f}% ({bytes_sent}/{file_size} bytes)", end='\r')
            
            print(f"  ✅ 完成: {server_filename}")
            
            # 接收最终确认
            final_response = self.socket.recv(1024).decode('utf-8')
            if "SUCCESS" not in final_response:
                print(f"  ❌ 服务器错误: {final_response.strip()}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ 上传失败: {e}")
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
    print("  📤 up <路径>         - 上传文件或文件夹 (别名: upload, u)")
    print("  📥 down <文件>       - 下载文件 (别名: download, d)")
    print("  📂 ls               - 列出文件 (别名: list, l)")
    print("")
    print("其他命令:")
    print("  💬 hello            - 服务器问候")
    print("  🕒 time             - 服务器时间")
    print("  ❓ help             - 显示帮助 (别名: h, ?)")
    print("  🚪 quit             - 退出程序 (别名: exit, q)")
    print("")
    print("💡 提示:")
    print("  - 上传文件: up myfile.txt")
    print("  - 上传文件夹: up ./documents (保持目录结构)")
    print("  - 输入其他文本将直接发送给服务器")
    print("=" * 50)

def print_usage():
    """显示使用说明"""
    print("使用方法:")
    print("  python file_transfer_client.py [目标主机] [目标端口] [代理主机] [代理端口]")
    print("")
    print("参数:")
    print("  目标主机    - 目标服务器IP地址 (默认: localhost)")
    print("  目标端口    - 目标服务器端口 (默认: 8080)")
    print("  代理主机    - 代理服务器IP地址 (可选)")
    print("  代理端口    - 代理服务器端口 (可选)")
    print("")
    print("示例:")
    print("  # 直接连接")
    print("  python file_transfer_client.py 192.168.1.100 8080")
    print("")
    print("  # 通过代理连接")
    print("  python file_transfer_client.py 192.168.1.100 8080 192.168.1.50 9999")
    print("")
    print("💡 如果指定了代理，所有通信将通过代理服务器转发")

def main():
    print("🚀 文件传输客户端")
    print("=" * 30)
    
    # 检查是否需要显示帮助
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # 解析命令行参数
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    # 可选的代理参数
    proxy_host = sys.argv[3] if len(sys.argv) > 3 else None
    proxy_port = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    # 显示连接信息
    if proxy_host and proxy_port:
        print(f"🎯 目标服务器: {host}:{port}")
        print(f"🔄 代理服务器: {proxy_host}:{proxy_port}")
        print("📡 将通过代理连接到目标服务器")
    else:
        print(f"🎯 目标服务器: {host}:{port}")
        print("🔗 将直接连接到服务器")
    
    client = FileTransferClient(host, port, proxy_host, proxy_port)
    
    if not client.connect():
        print("\n💡 提示: 使用 --help 查看使用说明")
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
                    print("❌ 请指定要上传的文件或文件夹")
                    print("💡 用法: up <文件路径或文件夹路径>")
                    print("📝 例如: up test.txt 或 up ./documents")
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
