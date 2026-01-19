#include "socket_server.h"
#include <iostream>
#include <string>
#include <thread>
#include <chrono>

#ifdef USE_SPDLOG
    #include <spdlog/spdlog.h>
#endif

#ifdef _WIN32
    #include <windows.h>
#endif

int main() {
#ifdef _WIN32
    // 设置控制台代码页为UTF-8
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    // 启用虚拟终端处理以支持ANSI转义序列（彩色输出）
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);
#endif
#ifdef USE_SPDLOG
    // 设置全局日志级别
    spdlog::set_level(spdlog::level::info);
    
    auto logger = spdlog::get("SocketServer");
    if (!logger) {
        logger = spdlog::default_logger();
    }
    
    logger->info("=== C++14 Socket Server Demo with spdlog ===");
#else
    std::cout << "=== C++14 Socket Server Demo (basic logging) ===" << std::endl;
#endif
    
    // Create server instance, listen on port 8080, files stored in ./uploads
    SocketServer server(8080, "./uploads");
    
    // Set custom client handler function
    server.setClientHandler([
#ifdef USE_SPDLOG
                            logger
#endif
                            ](SOCKET clientSocket, const std::string& message) {
#ifdef USE_SPDLOG
        logger->info("Processing message: {}", message);
#else
        std::cout << "[INFO] Processing message: " << message << std::endl;
#endif
        
        // Different responses based on message content
        std::string response;
        if (message.find("hello") != std::string::npos) {
            response = "Hello! Welcome to Socket Server with File Transfer!\n";
            response += "File commands:\n";
            response += "- FILE:LIST - List available files\n";
            response += "- FILE:UPLOAD:filename:size - Upload a file\n";
            response += "- FILE:DOWNLOAD:filename - Download a file\n";
        } else if (message.find("time") != std::string::npos) {
            auto now = std::chrono::system_clock::now();
            auto time_t = std::chrono::system_clock::to_time_t(now);
            response = "Current time: " + std::string(std::ctime(&time_t));
        } else if (message.find("help") != std::string::npos) {
            response = "Available commands:\n";
            response += "- hello - Welcome message and file commands info\n";
            response += "- time - Get server time\n";
            response += "- help - Show this help\n";
            response += "- quit/exit - Close connection\n";
            response += "File transfer commands:\n";
            response += "- FILE:LIST - List files on server\n";
            response += "- FILE:UPLOAD:filename:size - Upload file to server\n";
            response += "- FILE:DOWNLOAD:filename - Download file from server\n";
        } else if (message.find("quit") != std::string::npos || message.find("exit") != std::string::npos) {
            response = "Goodbye! Connection will be closed.\n";
            send(clientSocket, response.c_str(), static_cast<int>(response.length()), 0);
            return; // End connection
        } else {
            response = "Echo your message: " + message + "\n";
            response += "Type 'help' for available commands\n";
        }
        
        // Send response
        send(clientSocket, response.c_str(), static_cast<int>(response.length()), 0);
#ifdef USE_SPDLOG
        logger->debug("Sent response to client");
#else
        std::cout << "[DEBUG] Sent response to client" << std::endl;
#endif
    });
    
    // Start server
    if (!server.start()) {
#ifdef USE_SPDLOG
        logger->error("Failed to start server!");
#else
        std::cerr << "[ERROR] Failed to start server!" << std::endl;
#endif
        return 1;
    }
    
#ifdef USE_SPDLOG
    logger->info("Server is running... Press Ctrl+C to exit");
    logger->info("You can test with: telnet localhost 8080");
    
    // Set log level to debug if needed
    // server.setLogLevel(spdlog::level::debug);
#else
    std::cout << "[INFO] Server is running... Press Ctrl+C to exit" << std::endl;
    std::cout << "[INFO] You can test with: telnet localhost 8080" << std::endl;
#endif
    
    // Run server main loop
    try {
        server.run();
    } catch (const std::exception& e) {
#ifdef USE_SPDLOG
        logger->error("Server runtime error: {}", e.what());
#else
        std::cerr << "[ERROR] Server runtime error: " << e.what() << std::endl;
#endif
        return 1;
    }
    
    return 0;
}
