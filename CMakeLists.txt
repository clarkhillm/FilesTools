cmake_minimum_required(VERSION 3.10)
project(SocketServer VERSION 1.0.0)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 尝试查找spdlog包（可选）
find_package(spdlog CONFIG QUIET)

if(spdlog_FOUND)
    message(STATUS "Found spdlog, enabling advanced logging")
    add_definitions(-DUSE_SPDLOG)
    set(SPDLOG_LIBS spdlog::spdlog)
else()
    message(STATUS "spdlog not found, using basic logging")
    set(SPDLOG_LIBS)
endif()

# 编译选项
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
    # Windows需要链接ws2_32库
    set(SOCKET_LIBS ws2_32)
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O2")
    set(SOCKET_LIBS)
endif()

# 包含目录
include_directories(include)

# 源文件
set(SOURCES
    src/main.cpp
    src/socket_server.cpp
)

# 头文件
set(HEADERS
    include/socket_server.h
)

# 创建可执行文件
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# 链接库
target_link_libraries(${PROJECT_NAME} ${SOCKET_LIBS} ${SPDLOG_LIBS})

# 设置输出目录
set_target_properties(${PROJECT_NAME} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
