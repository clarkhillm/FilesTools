@echo off
echo ========================================
echo Building Socket Server (fallback mode)
echo ========================================
echo.
echo vcpkg not found, building with fallback mode...
echo This will build without spdlog integration.
echo.

REM 创建一个临时的CMakeLists.txt，不依赖spdlog
echo Creating fallback CMakeLists.txt...

copy CMakeLists.txt CMakeLists.txt.backup

(
echo cmake_minimum_required^(VERSION 3.10^)
echo project^(SocketServer VERSION 1.0.0^)
echo.
echo # 设置C++标准
echo set^(CMAKE_CXX_STANDARD 14^)
echo set^(CMAKE_CXX_STANDARD_REQUIRED ON^)
echo.
echo # 编译选项
echo if^(MSVC^)
echo     set^(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4"^)
echo     # Windows需要链接ws2_32库
echo     set^(SOCKET_LIBS ws2_32^)
echo else^(^)
echo     set^(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O2"^)
echo     set^(SOCKET_LIBS^)
echo endif^(^)
echo.
echo # 包含目录
echo include_directories^(include^)
echo.
echo # 源文件
echo set^(SOURCES
echo     src/main.cpp
echo     src/socket_server.cpp
echo ^)
echo.
echo # 头文件
echo set^(HEADERS
echo     include/socket_server.h
echo ^)
echo.
echo # 创建可执行文件
echo add_executable^(${PROJECT_NAME} ${SOURCES} ${HEADERS}^)
echo.
echo # 链接库
echo target_link_libraries^(${PROJECT_NAME} ${SOCKET_LIBS}^)
echo.
echo # 设置输出目录
echo set_target_properties^(${PROJECT_NAME} PROPERTIES
echo     RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
echo ^)
) > CMakeLists_fallback.txt

REM 创建构建目录
if not exist build mkdir build
cd build

REM 配置项目
echo Configuring project...
cmake .. -f ../CMakeLists_fallback.txt
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
echo Note: Built without spdlog integration
echo To use spdlog, please install vcpkg and run build-with-spdlog.bat
echo.
echo Executable location: build\bin\Release\SocketServer.exe
echo.
pause
