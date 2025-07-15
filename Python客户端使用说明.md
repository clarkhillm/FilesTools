# Python测试客户端使用说明

本目录包含两个Python客户端程序用于测试C++ Socket服务器。

## 文件说明

- `test_client.py` - 功能完整的交互式客户端
- `simple_test.py` - 简单的自动化测试工具

## 使用方法

### 1. 简单测试 (推荐先用这个)

```bash
python simple_test.py
```

或指定服务器地址和端口：

```bash
python simple_test.py localhost 8080
```

这个脚本会自动发送几个测试消息并显示服务器的响应。

### 2. 交互式测试

```bash
python test_client.py
```

启动后选择运行模式：
- **交互模式**: 手动输入命令与服务器交互
- **自动测试模式**: 自动运行一系列测试

#### 可用命令 (交互模式)

- `hello` - 发送问候消息
- `time` - 获取服务器时间
- `quit` 或 `exit` - 退出客户端
- `help` - 显示帮助信息
- `test` - 运行自动测试
- 任何其他文本 - 发送自定义消息

## 测试步骤

1. **启动C++服务器**
   ```bash
   cd build/bin/Debug
   ./SocketServer.exe
   ```

2. **在另一个终端运行Python客户端**
   ```bash
   python simple_test.py
   ```

## 预期输出示例

### 服务器端：
```
[INFO] Server started successfully, listening on port: 8080
[INFO] Server started accepting connections...
[INFO] New client connected: 127.0.0.1:xxxxx
[DEBUG] Received message: hello
[DEBUG] Received message: time
[INFO] Client connection closed
```

### 客户端端：
```
🔧 Socket服务器简单测试工具
------------------------------
✓ 成功连接到 localhost:8080

📤 发送: hello
📨 响应: Hello! Welcome to Socket Server!

📤 发送: time  
📨 响应: Current time: Mon Jul 14 xx:xx:xx 2025

📤 发送: This is a test message
📨 响应: Echo your message: This is a test message
Supported commands: hello, time, quit/exit

📤 发送: quit
📨 响应: Goodbye! Connection will be closed.

✅ 测试完成
```

## 故障排除

1. **连接被拒绝**: 确保C++服务器正在运行且监听正确的端口
2. **Python不存在**: 确保安装了Python 3.x
3. **权限问题**: 在Windows上可能需要管理员权限

## 扩展功能

`test_client.py` 还支持：
- 多线程消息接收
- 自定义服务器地址和端口
- 自动化测试套件
- 友好的用户界面
