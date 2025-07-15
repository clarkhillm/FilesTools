# Socket Server

一个基于C++14的简单Socket服务器实现，集成了spdlog日志库。

## 特性

- 支持多客户端并发连接
- 跨平台支持（Windows/Linux）
- 基于C++14标准
- 使用CMake构建系统
- 集成spdlog高性能日志库
- 支持控制台和文件日志输出
- 简单易用的API

## 构建要求

- CMake 3.10 或更高版本
- 支持C++14的编译器（GCC 5+, Clang 3.4+, MSVC 2015+）
- vcpkg包管理器（用于管理spdlog依赖）

## 构建说明

### 安装vcpkg（如果尚未安装）

```bash
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install
```

### Windows (使用vcpkg和Visual Studio)

#### 方法1：使用构建脚本（推荐）

```bash
.\build-with-spdlog.bat
```

#### 方法2：手动构建

```bash
# 安装依赖
vcpkg install spdlog:x64-windows

# 构建项目
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=[vcpkg根目录]/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
```

### Linux/macOS

```bash
# 安装依赖
vcpkg install spdlog

# 构建项目
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=[vcpkg根目录]/scripts/buildsystems/vcpkg.cmake
make
```

## 运行

构建完成后，可执行文件位于 `build/bin/` 目录下：

```bash
# Windows
.\build\bin\Release\SocketServer.exe

# Linux/macOS
./build/bin/SocketServer
```

## 测试连接

服务器启动后，默认监听8080端口。你可以使用以下方式测试：

### 使用telnet

```bash
telnet localhost 8080
```

### 使用netcat (Linux/macOS)

```bash
nc localhost 8080
```

## 支持的命令

- `hello` - 获取欢迎消息
- `time` - 获取当前服务器时间
- `quit` 或 `exit` - 断开连接
- 其他任何文本 - 服务器会回显你的消息

## 日志功能

服务器集成了spdlog日志库，提供以下功能：

- **控制台日志**：彩色输出，显示重要信息
- **文件日志**：详细日志保存到 `socket_server.log` 文件
- **多级别日志**：支持debug、info、warn、error等级别
- **自定义格式**：时间戳、线程ID、日志级别等信息

### 日志级别设置

```cpp
// 在代码中设置日志级别
server.setLogLevel(spdlog::level::debug);  // 显示所有日志
server.setLogLevel(spdlog::level::info);   // 只显示info及以上级别
```

## 项目结构

```
.
├── CMakeLists.txt          # CMake配置文件
├── vcpkg.json             # vcpkg依赖配置
├── README.md              # 项目说明
├── build-with-spdlog.bat  # Windows构建脚本
├── include/
│   └── socket_server.h    # 服务器头文件
└── src/
    ├── main.cpp           # 主程序入口
    └── socket_server.cpp  # 服务器实现
```

## API 使用示例

```cpp
#include "socket_server.h"
#include <spdlog/spdlog.h>

// 创建服务器
SocketServer server(8080);

// 设置日志级别
server.setLogLevel(spdlog::level::debug);

// 设置自定义消息处理函数
server.setClientHandler([](SOCKET clientSocket, const std::string& message) {
    // 处理客户端消息（使用spdlog记录日志）
    spdlog::info("Processing client message: {}", message);
    
    std::string response = "Hello: " + message;
    send(clientSocket, response.c_str(), response.length(), 0);
});

// 启动并运行服务器
if (server.start()) {
    server.run();
}
```

## 许可证

本项目仅供学习和演示使用。
