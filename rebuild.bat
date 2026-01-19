@echo off
chcp 65001 > nul
echo ======================================
echo 重新编译文件传输服务器（UTF-8支持）
echo ======================================
echo.

echo [1/3] 清理旧的构建文件...
cd build
cmake --build . --target clean 2>nul
cd ..

echo.
echo [2/3] 配置CMake项目...
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
if errorlevel 1 (
    echo ❌ CMake配置失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 编译项目（Release版本）...
cmake --build . --config Release
if errorlevel 1 (
    echo ❌ 编译失败！
    pause
    exit /b 1
)

cd ..

echo.
echo ======================================
echo ✅ 编译成功！
echo ======================================
echo.
echo 💡 可执行文件位于: build\bin\Release\SocketServer.exe
echo 💡 直接运行: build\bin\Release\SocketServer.exe
echo.
pause
