@echo off
echo ========================================
echo Building Socket Server Project
echo ========================================

REM 创建构建目录
if not exist build mkdir build
cd build

REM 配置项目
echo Configuring project...
cmake ..
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
echo.
echo To run the server:
echo   cd build\bin\Release
echo   SocketServer.exe
echo.
echo To test the server:
echo   telnet localhost 8080
echo.
pause
