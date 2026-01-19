#!/usr/bin/env python3
"""
文件传输客户端 - 图形界面版本
使用tkinter提供简单易用的GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import json
from pathlib import Path
from file_transfer_client import FileTransferClient


class FileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 文件传输客户端")
        self.root.geometry("700x600")
        
        self.client = None
        self.connected = False
        self.config_file = Path.home() / ".file_transfer_config.json"
        
        self.create_widgets()
        self.load_config()  # 启动时加载配置
        
    def create_widgets(self):
        """创建GUI组件"""
        # ========== 连接配置区域 ==========
        config_frame = ttk.LabelFrame(self.root, text="🔧 连接配置", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 目标服务器
        ttk.Label(config_frame, text="目标服务器:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.host_entry = ttk.Entry(config_frame, width=20)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(config_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.port_entry = ttk.Entry(config_frame, width=10)
        self.port_entry.insert(0, "8080")
        self.port_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 代理服务器（可选）
        self.use_proxy_var = tk.BooleanVar()
        self.proxy_check = ttk.Checkbutton(
            config_frame, 
            text="使用代理", 
            variable=self.use_proxy_var,
            command=self.toggle_proxy
        )
        self.proxy_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(config_frame, text="代理服务器:").grid(row=1, column=0, sticky=tk.W, pady=2, padx=(80, 0))
        self.proxy_host_entry = ttk.Entry(config_frame, width=20, state=tk.DISABLED)
        self.proxy_host_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(config_frame, text="端口:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.proxy_port_entry = ttk.Entry(config_frame, width=10, state=tk.DISABLED)
        self.proxy_port_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 连接按钮
        self.connect_btn = ttk.Button(
            config_frame, 
            text="🔗 连接", 
            command=self.toggle_connection
        )
        self.connect_btn.grid(row=0, column=4, rowspan=2, padx=10, pady=2)
        
        # 连接状态指示
        self.status_label = ttk.Label(config_frame, text="⚫ 未连接", foreground="gray")
        self.status_label.grid(row=0, column=5, rowspan=2, padx=5)
        
        # ========== 文件操作区域 ==========
        operations_frame = ttk.LabelFrame(self.root, text="📂 文件操作", padding="10")
        operations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 按钮区
        btn_frame = ttk.Frame(operations_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.upload_file_btn = ttk.Button(
            btn_frame, 
            text="📤 上传文件", 
            command=self.upload_file,
            state=tk.DISABLED
        )
        self.upload_file_btn.pack(side=tk.LEFT, padx=5)
        
        self.upload_folder_btn = ttk.Button(
            btn_frame, 
            text="📁 上传文件夹", 
            command=self.upload_folder,
            state=tk.DISABLED
        )
        self.upload_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.list_btn = ttk.Button(
            btn_frame, 
            text="📋 列出文件", 
            command=self.list_files,
            state=tk.DISABLED
        )
        self.list_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_btn = ttk.Button(
            btn_frame, 
            text="📥 下载文件", 
            command=self.download_file,
            state=tk.DISABLED
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="🗑️ 清空日志", 
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # 进度条区域
        progress_frame = ttk.Frame(operations_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # 日志显示区
        log_label = ttk.Label(operations_frame, text="📝 操作日志:")
        log_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            operations_frame, 
            height=20, 
            width=80,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 配置日志文本颜色标签
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("warning", foreground="orange")
        
    def toggle_proxy(self):
        """切换代理设置的启用状态"""
        if self.use_proxy_var.get():
            self.proxy_host_entry.config(state=tk.NORMAL)
            self.proxy_port_entry.config(state=tk.NORMAL)
        else:
            self.proxy_host_entry.config(state=tk.DISABLED)
            self.proxy_port_entry.config(state=tk.DISABLED)
            
    def log(self, message, tag=None):
        """在日志区域添加消息"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, value, text=""):
        """更新进度条"""
        self.progress_bar['value'] = value
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def reset_progress(self):
        """重置进度条"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="就绪")
        self.root.update_idletasks()
    
    def load_config(self):
        """加载保存的配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 填充配置到界面
                if 'host' in config:
                    self.host_entry.delete(0, tk.END)
                    self.host_entry.insert(0, config['host'])
                
                if 'port' in config:
                    self.port_entry.delete(0, tk.END)
                    self.port_entry.insert(0, str(config['port']))
                
                if 'use_proxy' in config and config['use_proxy']:
                    self.use_proxy_var.set(True)
                    self.toggle_proxy()
                    
                    if 'proxy_host' in config:
                        self.proxy_host_entry.delete(0, tk.END)
                        self.proxy_host_entry.insert(0, config['proxy_host'])
                    
                    if 'proxy_port' in config:
                        self.proxy_port_entry.delete(0, tk.END)
                        self.proxy_port_entry.insert(0, str(config['proxy_port']))
                
                self.log("✅ 已加载上次的连接配置", "success")
                
        except Exception as e:
            # 如果配置文件损坏或格式错误，忽略并使用默认值
            pass
    
    def save_config(self):
        """保存当前配置"""
        try:
            config = {
                'host': self.host_entry.get().strip(),
                'port': int(self.port_entry.get().strip()),
                'use_proxy': self.use_proxy_var.get()
            }
            
            if self.use_proxy_var.get():
                config['proxy_host'] = self.proxy_host_entry.get().strip()
                config['proxy_port'] = int(self.proxy_port_entry.get().strip())
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.log("💾 连接配置已保存", "success")
            
        except Exception as e:
            self.log(f"⚠️ 保存配置失败: {e}", "warning")
        
    def toggle_connection(self):
        """切换连接状态"""
        if self.connected:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        """连接到服务器"""
        try:
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            proxy_host = None
            proxy_port = None
            
            if self.use_proxy_var.get():
                proxy_host = self.proxy_host_entry.get().strip()
                proxy_port = int(self.proxy_port_entry.get().strip())
                
                if not proxy_host or not proxy_port:
                    messagebox.showerror("错误", "请填写完整的代理服务器信息")
                    return
            
            self.log(f"🔄 正在连接到 {host}:{port}...", "info")
            
            if proxy_host and proxy_port:
                self.log(f"🔄 使用代理: {proxy_host}:{proxy_port}", "info")
            
            # 在后台线程中连接
            def connect_thread():
                self.client = FileTransferClient(host, port, proxy_host, proxy_port)
                if self.client.connect():
                    self.connected = True
                    self.root.after(0, self.on_connected)
                else:
                    self.root.after(0, self.on_connect_failed)
            
            threading.Thread(target=connect_thread, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
        except Exception as e:
            self.log(f"❌ 连接错误: {e}", "error")
            
    def on_connected(self):
        """连接成功后的处理"""
        self.log("✅ 连接成功！", "success")
        self.status_label.config(text="🟢 已连接", foreground="green")
        self.connect_btn.config(text="🔌 断开")
        
        # 保存配置
        self.save_config()
        
        # 禁用连接配置
        self.host_entry.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.DISABLED)
        self.proxy_check.config(state=tk.DISABLED)
        self.proxy_host_entry.config(state=tk.DISABLED)
        self.proxy_port_entry.config(state=tk.DISABLED)
        
        # 启用操作按钮
        self.upload_file_btn.config(state=tk.NORMAL)
        self.upload_folder_btn.config(state=tk.NORMAL)
        self.list_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.NORMAL)
        
    def on_connect_failed(self):
        """连接失败后的处理"""
        self.log("❌ 连接失败", "error")
        self.status_label.config(text="🔴 连接失败", foreground="red")
        
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.disconnect()
        
        self.connected = False
        self.log("🔌 已断开连接", "info")
        self.status_label.config(text="⚫ 未连接", foreground="gray")
        self.connect_btn.config(text="🔗 连接")
        
        # 启用连接配置
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.proxy_check.config(state=tk.NORMAL)
        self.toggle_proxy()
        
        # 禁用操作按钮
        self.upload_file_btn.config(state=tk.DISABLED)
        self.upload_folder_btn.config(state=tk.DISABLED)
        self.list_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        
    def upload_file(self):
        """上传文件"""
        file_path = filedialog.askopenfilename(title="选择要上传的文件")
        if file_path:
            filename = os.path.basename(file_path)
            self.log(f"📤 准备上传文件: {filename}", "info")
            self.reset_progress()
            
            def upload_thread():
                try:
                    file_size = os.path.getsize(file_path)
                    self.root.after(0, lambda: self.update_progress(0, f"上传: {filename} (0%)"))
                    
                    # 发送上传命令
                    upload_command = f"FILE:UPLOAD:{filename}:{file_size}"
                    self.client.socket.send(upload_command.encode('utf-8'))
                    
                    # 等待服务器确认
                    response = self.client.socket.recv(1024).decode('utf-8')
                    if "READY" not in response:
                        self.root.after(0, lambda: self.log(f"❌ 服务器不准备接收文件: {response}", "error"))
                        self.root.after(0, self.reset_progress)
                        return
                    
                    # 发送文件数据
                    with open(file_path, 'rb') as file:
                        bytes_sent = 0
                        buffer_size = 8192
                        
                        while bytes_sent < file_size:
                            data = file.read(buffer_size)
                            if not data:
                                break
                            
                            self.client.socket.send(data)
                            bytes_sent += len(data)
                            
                            # 更新进度条
                            progress = (bytes_sent / file_size) * 100
                            self.root.after(0, lambda p=progress, s=bytes_sent, t=file_size: 
                                          self.update_progress(p, f"上传: {filename} ({p:.1f}% - {s}/{t} bytes)"))
                    
                    # 接收最终确认
                    final_response = self.client.socket.recv(1024).decode('utf-8')
                    
                    self.root.after(0, lambda: self.log(f"✅ 文件上传成功: {filename}", "success"))
                    self.root.after(0, lambda: self.log(f"📨 服务器确认: {final_response.strip()}"))
                    self.root.after(0, lambda: self.update_progress(100, f"完成: {filename}"))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"❌ 上传文件失败: {e}", "error"))
                    self.root.after(0, self.reset_progress)
            
            threading.Thread(target=upload_thread, daemon=True).start()
            
    def upload_folder(self):
        """上传文件夹"""
        folder_path = filedialog.askdirectory(title="选择要上传的文件夹")
        if folder_path:
            folder_name = os.path.basename(os.path.abspath(folder_path))
            result = messagebox.askyesno(
                "确认上传", 
                f"确认上传文件夹 '{folder_name}' 吗？\n\n这将上传文件夹内的所有文件。"
            )
            
            if result:
                self.log(f"📁 准备上传文件夹: {folder_name}", "info")
                self.reset_progress()
                
                def upload_thread():
                    try:
                        # 收集所有文件
                        files_to_upload = []
                        total_size = 0
                        
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                relative_path = os.path.relpath(file_path, folder_path)
                                relative_path = relative_path.replace('\\', '/')
                                server_filename = f"{folder_name}/{relative_path}"
                                
                                file_size = os.path.getsize(file_path)
                                files_to_upload.append((file_path, server_filename, file_size))
                                total_size += file_size
                        
                        if not files_to_upload:
                            self.root.after(0, lambda: self.log(f"❌ 文件夹为空: {folder_path}", "error"))
                            self.root.after(0, self.reset_progress)
                            return
                        
                        self.root.after(0, lambda: self.log(f"📊 发现 {len(files_to_upload)} 个文件，总大小: {total_size} bytes", "info"))
                        
                        # 上传所有文件
                        successful_uploads = 0
                        failed_uploads = 0
                        uploaded_size = 0
                        
                        for i, (local_path, server_filename, file_size) in enumerate(files_to_upload, 1):
                            self.root.after(0, lambda idx=i, total=len(files_to_upload), name=server_filename:
                                          self.log(f"📤 上传文件 {idx}/{total}: {name}", "info"))
                            
                            # 发送上传命令
                            upload_command = f"FILE:UPLOAD:{server_filename}:{file_size}"
                            self.client.socket.send(upload_command.encode('utf-8'))
                            
                            # 等待服务器确认
                            response = self.client.socket.recv(1024).decode('utf-8')
                            if "READY" not in response:
                                failed_uploads += 1
                                continue
                            
                            # 发送文件数据
                            with open(local_path, 'rb') as file:
                                bytes_sent = 0
                                buffer_size = 8192
                                
                                while bytes_sent < file_size:
                                    data = file.read(buffer_size)
                                    if not data:
                                        break
                                    
                                    self.client.socket.send(data)
                                    bytes_sent += len(data)
                                    
                                    # 更新总进度
                                    current_total = uploaded_size + bytes_sent
                                    progress = (current_total / total_size) * 100
                                    self.root.after(0, lambda p=progress, idx=i, total=len(files_to_upload):
                                                  self.update_progress(p, f"上传文件夹: {idx}/{total} ({p:.1f}%)"))
                            
                            uploaded_size += file_size
                            
                            # 接收确认
                            final_response = self.client.socket.recv(1024).decode('utf-8')
                            if "SUCCESS" in final_response:
                                successful_uploads += 1
                            else:
                                failed_uploads += 1
                        
                        # 显示结果
                        self.root.after(0, lambda: self.log(f"\n📊 文件夹上传完成:", "success"))
                        self.root.after(0, lambda s=successful_uploads: self.log(f"  ✅ 成功: {s} 个文件", "success"))
                        if failed_uploads > 0:
                            self.root.after(0, lambda f=failed_uploads: self.log(f"  ❌ 失败: {f} 个文件", "error"))
                        
                        self.root.after(0, lambda: self.update_progress(100, "文件夹上传完成"))
                        
                    except Exception as e:
                        self.root.after(0, lambda: self.log(f"❌ 上传文件夹失败: {e}", "error"))
                        self.root.after(0, self.reset_progress)
                
                threading.Thread(target=upload_thread, daemon=True).start()
                
    def list_files(self):
        """列出服务器文件"""
        self.log("📋 正在获取文件列表...", "info")
        
        def list_thread():
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.client.list_files()
            
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            self.root.after(0, lambda: self.log(output))
        
        threading.Thread(target=list_thread, daemon=True).start()
        
    def download_file(self):
        """下载文件"""
        # 弹出对话框让用户输入文件名
        filename = tk.simpledialog.askstring("下载文件", "请输入要下载的文件名:")
        
        if filename:
            save_dir = filedialog.askdirectory(title="选择保存位置")
            
            if save_dir:
                self.log(f"📥 准备下载文件: {filename}", "info")
                self.reset_progress()
                
                def download_thread():
                    try:
                        # 发送下载命令
                        download_command = f"FILE:DOWNLOAD:{filename}"
                        self.client.socket.send(download_command.encode('utf-8'))
                        
                        # 接收文件信息
                        response = self.client.socket.recv(1024).decode('utf-8')
                        
                        if response.startswith("ERROR"):
                            self.root.after(0, lambda: self.log(f"❌ 下载失败: {response}", "error"))
                            self.root.after(0, self.reset_progress)
                            return
                        
                        if not response.startswith("FILE_INFO:"):
                            self.root.after(0, lambda: self.log(f"❌ 意外的服务器响应: {response}", "error"))
                            self.root.after(0, self.reset_progress)
                            return
                        
                        # 解析文件大小
                        file_size = int(response.split(':')[1].strip())
                        self.root.after(0, lambda: self.log(f"📋 文件大小: {file_size} bytes", "info"))
                        
                        # 发送准备确认
                        self.client.socket.send("READY".encode('utf-8'))
                        
                        # 接收文件数据
                        local_file_path = os.path.join(save_dir, filename)
                        bytes_received = 0
                        
                        with open(local_file_path, 'wb') as file:
                            while bytes_received < file_size:
                                remaining = file_size - bytes_received
                                buffer_size = min(8192, remaining)
                                
                                data = self.client.socket.recv(buffer_size)
                                if not data:
                                    break
                                
                                file.write(data)
                                bytes_received += len(data)
                                
                                # 更新进度
                                progress = (bytes_received / file_size) * 100
                                self.root.after(0, lambda p=progress, r=bytes_received, t=file_size:
                                              self.update_progress(p, f"下载: {filename} ({p:.1f}% - {r}/{t} bytes)"))
                        
                        self.root.after(0, lambda: self.log(f"✅ 文件下载成功: {local_file_path}", "success"))
                        self.root.after(0, lambda: self.update_progress(100, f"下载完成: {filename}"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", f"文件下载成功！\n保存到: {local_file_path}"))
                        
                    except Exception as e:
                        self.root.after(0, lambda: self.log(f"❌ 下载文件失败: {e}", "error"))
                        self.root.after(0, self.reset_progress)
                
                threading.Thread(target=download_thread, daemon=True).start()

            
    def on_closing(self):
        """关闭窗口时的处理"""
        if self.connected:
            result = messagebox.askyesno("确认退出", "当前已连接到服务器，确认退出吗？")
            if result:
                self.disconnect()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    
    # 设置图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = FileTransferGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    # 需要添加simpledialog导入
    import tkinter.simpledialog
    main()
