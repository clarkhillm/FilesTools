@echo off
echo ========================================
echo Building Socket Server with vcpkg
echo ========================================

REM 检查vcpkg是否安装
where vcpkg >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: vcpkg not found in PATH
    echo Please install vcpkg and add it to your PATH
    echo Visit: https://github.com/Microsoft/vcpkg
    pause
    exit /b 1
)

echo Found vcpkg, checking installation...

REM 安装依赖
echo Installing dependencies with vcpkg...
vcpkg install
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM 创建构建目录
if not exist build mkdir build
cd build

REM 配置项目（使用vcpkg工具链）
echo Configuring project with vcpkg toolchain...
cmake .. -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%/scripts/buildsystems/vcpkg.cmake
if %ERRORLEVEL% neq 0 (
    echo CMake configuration failed!
    echo Make sure VCPKG_ROOT environment variable is set
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
