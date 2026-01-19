# UTF-8 编码支持说明

## 🔧 已修复的问题

### 1. **Windows 控制台 UTF-8 支持**
- ✅ 设置控制台代码页为 UTF-8 (CP_UTF8)
- ✅ 启用虚拟终端处理，支持彩色输出
- ✅ 正确显示中文日志和消息

### 2. **文件系统 UTF-8 支持**
- ✅ 使用 `std::filesystem::path` 处理文件路径
- ✅ 支持中文文件名的上传和下载
- ✅ 支持中文目录名

### 3. **路径分隔符统一**
- ✅ 自动将反斜杠 `\` 转换为正斜杠 `/`
- ✅ 跨平台兼容（Windows/Linux）
- ✅ 与 Python 客户端完美协作

### 4. **文件列表改进**
- ✅ 递归列出所有子目录中的文件
- ✅ 显示相对路径，保持目录结构
- ✅ 正确处理 UTF-8 文件名

## 📝 修改的文件

### main.cpp
```cpp
#ifdef _WIN32
    // 设置控制台代码页为UTF-8
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    // 启用虚拟终端处理
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);
#endif
```

### socket_server.cpp
- 使用 `std::filesystem::path` 打开文件
- 文件列表使用 `recursive_directory_iterator` 递归遍历
- 路径分隔符统一处理

## 🚀 如何重新编译

### 方法1: 使用提供的脚本（推荐）
```bash
rebuild.bat
```

### 方法2: 手动编译
```bash
cd build
cmake --build . --config Release
```

## ✅ 测试中文支持

### 1. 启动服务器
```bash
cd build\bin\Release
SocketServer.exe
```

### 2. 使用 Python GUI 客户端
```bash
python file_transfer_gui.py
```

### 3. 测试中文文件名
- 上传名为 `测试文件.txt` 的文件
- 上传名为 `中文文件夹` 的目录
- 列出服务器文件，检查中文显示
- 下载中文文件名的文件

## 🐛 可能遇到的问题

### Q: 控制台仍显示乱码？
A: 确保：
1. 重新编译了服务器
2. 使用 UTF-8 编码的终端（Windows Terminal、PowerShell 7+）
3. 字体支持中文（如 Microsoft YaHei、SimSun）

### Q: 文件名在文件系统中显示乱码？
A: 这是正常的，Windows 文件系统使用 UTF-16，但程序内部正确处理 UTF-8

### Q: Python 客户端上传中文文件名失败？
A: 确保 Python 脚本本身以 UTF-8 编码保存

## 💡 技术细节

### UTF-8 编码流程
```
Python 客户端 (UTF-8)
    ↓ 网络传输
C++ 服务器接收 (UTF-8 字节流)
    ↓ std::string 存储
std::filesystem::path (自动处理编码)
    ↓ 文件系统
Windows (UTF-16) / Linux (UTF-8)
```

### 关键改进
1. **不转换编码**：全程使用 UTF-8，避免编码转换
2. **filesystem 库**：C++17 的 filesystem 自动处理平台差异
3. **控制台设置**：Windows 下主动设置 UTF-8 代码页

## 📊 兼容性

| 平台 | 控制台显示 | 文件名支持 | 路径支持 |
|------|-----------|-----------|---------|
| Windows 10+ | ✅ | ✅ | ✅ |
| Windows 7/8 | ⚠️ | ✅ | ✅ |
| Linux | ✅ | ✅ | ✅ |
| macOS | ✅ | ✅ | ✅ |

⚠️ Windows 7/8 可能需要额外配置才能正确显示 UTF-8

## 🎯 最佳实践

1. **文件命名**：推荐使用中英文、数字、下划线
2. **避免特殊字符**：`:`, `*`, `?`, `"`, `<`, `>`, `|`
3. **路径分隔符**：统一使用 `/`，程序会自动处理
4. **终端选择**：Windows 推荐使用 Windows Terminal
