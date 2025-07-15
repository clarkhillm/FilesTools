@echo off
echo ========================================
echo Building Socket Server with vcpkg
echo ========================================

REM 设置vcpkg路径
set VCPKG_ROOT=C:\vcpkg

REM 检查vcpkg是否存在
if not exist "%VCPKG_ROOT%\vcpkg.exe" (
    echo Error: vcpkg not found at %VCPKG_ROOT%
    echo Please make sure vcpkg is installed at C:\vcpkg
    pause
    exit /b 1
)

echo Found vcpkg at %VCPKG_ROOT%

REM 安装spdlog
echo Installing spdlog...
"%VCPKG_ROOT%\vcpkg.exe" install spdlog:x64-windows
if %ERRORLEVEL% neq 0 (
    echo Failed to install spdlog
    pause
    exit /b 1
)

echo spdlog installed successfully!

REM 创建构建目录
if not exist build mkdir build
cd build

REM 配置项目（使用vcpkg工具链）
echo Configuring project with vcpkg toolchain...
cmake .. -DCMAKE_TOOLCHAIN_FILE="%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake" -DVCPKG_TARGET_TRIPLET=x64-windows
if %ERRORLEVEL% neq 0 (
    echo CMake configuration failed!
    pause
    exit /b 1
)

REM 构建项目
echo Building project...
cmake --build . --config Release
if %ERRORLEVEL% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: build\bin\Release\SocketServer.exe
echo Log file will be created as: socket_server.log
echo.
echo To run the server:
echo   cd build\bin\Release
echo   SocketServer.exe
echo.
echo To test the server:
echo   telnet localhost 8080
echo.
pause
