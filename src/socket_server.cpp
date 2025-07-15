#include "socket_server.h"
#include <iostream>
#include <thread>
#include <sstream>
#include <fstream>
#include <filesystem>
#include <algorithm>

SocketServer::SocketServer(int port, const std::string& fileDir) 
    : m_port(port)
    , m_serverSocket(INVALID_SOCKET)
    , m_running(false)
    , m_fileDirectory(fileDir)
#ifdef _WIN32
    , m_wsaInitialized(false)
#endif
{
    setupLogger();
    createFileDirectory();
}

SocketServer::~SocketServer() {
    stop();
    cleanup();
}

bool SocketServer::start() {
    if (m_running) {
        logInfo("Server is already running");
        return true;
    }

    if (!initializeSocket()) {
        return false;
    }

    // Create socket
    m_serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (m_serverSocket == INVALID_SOCKET) {
        logError("Failed to create socket");
        return false;
    }

    // Set socket options
    int opt = 1;
#ifdef _WIN32
    if (setsockopt(m_serverSocket, SOL_SOCKET, SO_REUSEADDR, 
                   (char*)&opt, sizeof(opt)) == SOCKET_ERROR) {
#else
    if (setsockopt(m_serverSocket, SOL_SOCKET, SO_REUSEADDR, 
                   &opt, sizeof(opt)) == SOCKET_ERROR) {
#endif
        logError("Failed to set socket options");
        return false;
    }

    // Bind address
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(m_port);

    if (bind(m_serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        logError("Failed to bind address, port: " + std::to_string(m_port));
        return false;
    }

    // Start listening
    if (listen(m_serverSocket, 5) == SOCKET_ERROR) {
        logError("Failed to listen");
        return false;
    }

    m_running = true;
    logInfo("Server started successfully, listening on port: " + std::to_string(m_port));
    return true;
}

void SocketServer::stop() {
    if (!m_running) {
        return;
    }

    m_running = false;
    
    if (m_serverSocket != INVALID_SOCKET) {
        closesocket(m_serverSocket);
        m_serverSocket = INVALID_SOCKET;
    }

    logInfo("Server stopped");
}

void SocketServer::run() {
    if (!m_running) {
        logError("Server not started");
        return;
    }

    logInfo("Server started accepting connections...");

    while (m_running) {
        sockaddr_in clientAddr;
        socklen_t clientAddrLen = sizeof(clientAddr);
        
        SOCKET clientSocket = accept(m_serverSocket, (sockaddr*)&clientAddr, &clientAddrLen);
        
        if (clientSocket == INVALID_SOCKET) {
            if (m_running) {
                logError("Failed to accept connection");
            }
            continue;
        }

        // Get client IP address
        char clientIP[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(clientAddr.sin_addr), clientIP, INET_ADDRSTRLEN);
        
        logInfo("New client connected: " + std::string(clientIP) + ":" + std::to_string(ntohs(clientAddr.sin_port)));

        // Handle client in new thread
        std::thread clientThread(&SocketServer::handleClient, this, clientSocket);
        clientThread.detach();
    }
}

void SocketServer::setClientHandler(ClientHandler handler) {
    m_clientHandler = std::move(handler);
}

void SocketServer::setFileDirectory(const std::string& dir) {
    m_fileDirectory = dir;
    createFileDirectory();
}

#ifdef USE_SPDLOG
void SocketServer::setLogLevel(spdlog::level::level_enum level) {
    if (m_logger) {
        m_logger->set_level(level);
    }
}
#endif

void SocketServer::setupLogger() {
#ifdef USE_SPDLOG
    try {
#ifdef NDEBUG
        // Release build: setup rotating file logger
        createLogDirectory();
        
        // Create rotating file logger with size-based rotation
        auto max_size = 1048576 * 10; // 10MB
        auto max_files = 10;
        auto rotating_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>("log/server.log", max_size, max_files);
        
        // Set pattern with timestamp, level, and message
        rotating_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] [thread %t] %v");
        rotating_sink->set_level(spdlog::level::info);
        
        // Create logger with rotating file sink
        std::vector<spdlog::sink_ptr> sinks {rotating_sink};
        m_logger = std::make_shared<spdlog::logger>("SocketServer", sinks.begin(), sinks.end());
        
        m_logger->set_level(spdlog::level::info);
        m_logger->flush_on(spdlog::level::info);
        
        // Register logger
        spdlog::register_logger(m_logger);
        
        logInfo("Logger initialized with rotating file logger");
#else
        // Debug build: setup console and file logger
        auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
        auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("socket_server.log", true);
        
        console_sink->set_level(spdlog::level::info);
        file_sink->set_level(spdlog::level::debug);
        
        // 设置日志格式
        console_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%n] [%^%l%$] %v");
        file_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] [thread %t] %v");
        
        // 创建logger
        std::vector<spdlog::sink_ptr> sinks {console_sink, file_sink};
        m_logger = std::make_shared<spdlog::logger>("SocketServer", sinks.begin(), sinks.end());
        
        m_logger->set_level(spdlog::level::debug);
        m_logger->flush_on(spdlog::level::info);
        
        // 注册logger
        spdlog::register_logger(m_logger);
        
        logInfo("Logger initialized with console and file logger");
#endif
    } catch (const spdlog::spdlog_ex& ex) {
        std::cerr << "Log initialization failed: " << ex.what() << std::endl;
    }
#endif
}

void SocketServer::createLogDirectory() {
    try {
        if (!std::filesystem::exists("log")) {
            std::filesystem::create_directory("log");
        }
    } catch (const std::filesystem::filesystem_error& ex) {
        std::cerr << "Failed to create log directory: " << ex.what() << std::endl;
    }
}

void SocketServer::logInfo(const std::string& message) {
#ifdef USE_SPDLOG
    if (m_logger) {
        m_logger->info(message);
    } else {
        std::cout << "[INFO] " << message << std::endl;
    }
#else
    std::cout << "[INFO] " << message << std::endl;
#endif
}

void SocketServer::logError(const std::string& message) {
#ifdef USE_SPDLOG
    if (m_logger) {
        m_logger->error(message);
    } else {
        std::cerr << "[ERROR] " << message << std::endl;
    }
#else
    std::cerr << "[ERROR] " << message << std::endl;
#endif
}

void SocketServer::logDebug(const std::string& message) {
#ifdef USE_SPDLOG
    if (m_logger) {
        m_logger->debug(message);
    } else {
        std::cout << "[DEBUG] " << message << std::endl;
    }
#else
    std::cout << "[DEBUG] " << message << std::endl;
#endif
}

bool SocketServer::initializeSocket() {
#ifdef _WIN32
    if (!m_wsaInitialized) {
        int result = WSAStartup(MAKEWORD(2, 2), &m_wsaData);
        if (result != 0) {
            logError("WSAStartup failed: " + std::to_string(result));
            return false;
        }
        m_wsaInitialized = true;
        logDebug("WSA initialized successfully");
    }
#endif
    return true;
}

void SocketServer::cleanup() {
#ifdef _WIN32
    if (m_wsaInitialized) {
        WSACleanup();
        m_wsaInitialized = false;
    }
#endif
}

void SocketServer::handleClient(SOCKET clientSocket) {
    try {
        while (m_running) {
            std::string message = receiveMessage(clientSocket);
            if (message.empty()) {
                break; // Client disconnected
            }

            logDebug("Received message: " + message);

            // 检查是否是文件传输命令
            if (message.substr(0, 5) == "FILE:") {
                handleFileCommand(clientSocket, message);
                continue;
            }

            // Use custom handler if set
            if (m_clientHandler) {
                m_clientHandler(clientSocket, message);
            } else {
                // Default echo message
                std::string response = "Echo: " + message;
                if (!sendMessage(clientSocket, response)) {
                    break;
                }
            }
        }
    } catch (const std::exception& e) {
        logError("Exception handling client: " + std::string(e.what()));
    }

    closesocket(clientSocket);
    logInfo("Client connection closed");
}

std::string SocketServer::receiveMessage(SOCKET clientSocket) {
    char buffer[1024];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    
    if (bytesReceived <= 0) {
        return ""; // Connection closed or error
    }
    
    buffer[bytesReceived] = '\0';
    return std::string(buffer);
}

bool SocketServer::sendMessage(SOCKET clientSocket, const std::string& message) {
    int bytesSent = send(clientSocket, message.c_str(), static_cast<int>(message.length()), 0);
    return bytesSent != SOCKET_ERROR;
}

void SocketServer::handleFileCommand(SOCKET clientSocket, const std::string& command) {
    logInfo("Processing file command: " + command);
    
    // 解析文件命令格式: FILE:ACTION:FILENAME[:SIZE]
    std::vector<std::string> parts;
    std::stringstream ss(command);
    std::string item;
    
    while (std::getline(ss, item, ':')) {
        parts.push_back(item);
    }
    
    if (parts.size() < 2) {
        sendMessage(clientSocket, "ERROR: Invalid file command format\n");
        return;
    }
    
    std::string action = parts[1];
    
    // LIST命令不需要文件名
    if (action == "LIST") {
        logInfo("File list request");
        sendFileList(clientSocket);
        return;
    }
    
    // 其他命令需要文件名
    if (parts.size() < 3) {
        sendMessage(clientSocket, "ERROR: Invalid file command format\n");
        return;
    }
    
    std::string filename = parts[2];
    
    if (action == "UPLOAD") {
        if (parts.size() < 4) {
            sendMessage(clientSocket, "ERROR: File size required for upload\n");
            return;
        }
        
        size_t fileSize = std::stoull(parts[3]);
        logInfo("File upload request: " + filename + " (" + std::to_string(fileSize) + " bytes)");
        
        if (handleFileUpload(clientSocket, filename, fileSize)) {
            sendMessage(clientSocket, "SUCCESS: File uploaded successfully\n");
        } else {
            sendMessage(clientSocket, "ERROR: File upload failed\n");
        }
    }
    else if (action == "DOWNLOAD") {
        logInfo("File download request: " + filename);
        
        if (handleFileDownload(clientSocket, filename)) {
            logInfo("File download completed: " + filename);
        } else {
            sendMessage(clientSocket, "ERROR: File not found or download failed\n");
        }
    }
    else {
        sendMessage(clientSocket, "ERROR: Unknown file action\n");
    }
}

bool SocketServer::handleFileUpload(SOCKET clientSocket, const std::string& filename, size_t fileSize) {
    // 发送确认，准备接收文件
    if (!sendMessage(clientSocket, "READY\n")) {
        return false;
    }
    
    std::string filepath = getFilePath(filename);
    return receiveFileData(clientSocket, filepath, fileSize);
}

bool SocketServer::handleFileDownload(SOCKET clientSocket, const std::string& filename) {
    std::string filepath = getFilePath(filename);
    
    // 检查文件是否存在
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return false;
    }
    
    // 获取文件大小
    size_t fileSize = file.tellg();
    file.close();
    
    // 发送文件信息
    std::string fileInfo = "FILE_INFO:" + std::to_string(fileSize) + "\n";
    if (!sendMessage(clientSocket, fileInfo)) {
        return false;
    }
    
    // 等待客户端确认
    std::string response = receiveMessage(clientSocket);
    if (response.find("READY") == std::string::npos) {
        return false;
    }
    
    return sendFileData(clientSocket, filepath);
}

bool SocketServer::sendFileList(SOCKET clientSocket) {
    try {
        std::string fileList = "FILE_LIST:\n";
        
        if (std::filesystem::exists(m_fileDirectory)) {
            for (const auto& entry : std::filesystem::directory_iterator(m_fileDirectory)) {
                if (entry.is_regular_file()) {
                    std::string filename = entry.path().filename().string();
                    size_t fileSize = entry.file_size();
                    fileList += filename + ":" + std::to_string(fileSize) + "\n";
                }
            }
        }
        
        fileList += "END_LIST\n";
        return sendMessage(clientSocket, fileList);
    } catch (const std::exception& e) {
        logError("Error listing files: " + std::string(e.what()));
        return false;
    }
}

bool SocketServer::createFileDirectory() {
    try {
        if (!std::filesystem::exists(m_fileDirectory)) {
            std::filesystem::create_directories(m_fileDirectory);
            logInfo("Created file directory: " + m_fileDirectory);
        }
        return true;
    } catch (const std::exception& e) {
        logError("Failed to create file directory: " + std::string(e.what()));
        return false;
    }
}

std::string SocketServer::getFilePath(const std::string& filename) {
    // 防止路径遍历攻击
    std::string safeName = filename;
    size_t pos = 0;
    while ((pos = safeName.find("..", pos)) != std::string::npos) {
        safeName.erase(pos, 2);
    }
    
    // 构造完整文件路径
    std::string fullPath = m_fileDirectory + "/" + safeName;
    
    // 确保父目录存在
    std::filesystem::path filePath(fullPath);
    std::filesystem::path parentDir = filePath.parent_path();
    
    try {
        if (!std::filesystem::exists(parentDir)) {
            std::filesystem::create_directories(parentDir);
            logInfo("Created directory: " + parentDir.string());
        }
    } catch (const std::filesystem::filesystem_error& e) {
        logError("Failed to create directory: " + parentDir.string() + " - " + e.what());
    }
    
    return fullPath;
}

bool SocketServer::receiveFileData(SOCKET clientSocket, const std::string& filepath, size_t fileSize) {
    std::ofstream file(filepath, std::ios::binary);
    if (!file.is_open()) {
        logError("Failed to create file: " + filepath);
        return false;
    }
    
    const size_t bufferSize = 8192;
    char buffer[bufferSize];
    size_t totalReceived = 0;
    
    while (totalReceived < fileSize) {
        size_t toReceive = (bufferSize < (fileSize - totalReceived)) ? bufferSize : (fileSize - totalReceived);
        int bytesReceived = recv(clientSocket, buffer, static_cast<int>(toReceive), 0);
        
        if (bytesReceived <= 0) {
            logError("Failed to receive file data");
            file.close();
            std::filesystem::remove(filepath);
            return false;
        }
        
        file.write(buffer, bytesReceived);
        totalReceived += bytesReceived;
        
        // 记录进度
        if (totalReceived % (1024 * 1024) == 0 || totalReceived == fileSize) {
            logDebug("Received " + std::to_string(totalReceived) + "/" + std::to_string(fileSize) + " bytes");
        }
    }
    
    file.close();
    logInfo("File received successfully: " + filepath);
    return true;
}

bool SocketServer::sendFileData(SOCKET clientSocket, const std::string& filepath) {
    std::ifstream file(filepath, std::ios::binary);
    if (!file.is_open()) {
        logError("Failed to open file: " + filepath);
        return false;
    }
    
    const size_t bufferSize = 8192;
    char buffer[bufferSize];
    size_t totalSent = 0;
    
    while (file.read(buffer, bufferSize) || file.gcount() > 0) {
        size_t bytesToSend = file.gcount();
        size_t bytesSent = 0;
        
        while (bytesSent < bytesToSend) {
            int result = send(clientSocket, buffer + bytesSent, 
                            static_cast<int>(bytesToSend - bytesSent), 0);
            if (result == SOCKET_ERROR) {
                logError("Failed to send file data");
                file.close();
                return false;
            }
            bytesSent += result;
        }
        
        totalSent += bytesToSend;
        
        // 记录进度
        if (totalSent % (1024 * 1024) == 0) {
            logDebug("Sent " + std::to_string(totalSent) + " bytes");
        }
    }
    
    file.close();
    logInfo("File sent successfully: " + filepath + " (" + std::to_string(totalSent) + " bytes)");
    return true;
}
