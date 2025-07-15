#pragma once

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <fstream>
#include <filesystem>

#ifdef USE_SPDLOG
    #include <spdlog/spdlog.h>
    #include <spdlog/sinks/stdout_color_sinks.h>
    #include <spdlog/sinks/basic_file_sink.h>
    #include <spdlog/sinks/rotating_file_sink.h>
#endif

class SocketServer {
public:
    using ClientHandler = std::function<void(SOCKET, const std::string&)>;

    SocketServer(int port = 8080, const std::string& fileDir = "./files");
    ~SocketServer();

    // 禁用拷贝构造和赋值
    SocketServer(const SocketServer&) = delete;
    SocketServer& operator=(const SocketServer&) = delete;

    bool start();
    void stop();
    void run();
    
    // 设置客户端消息处理函数
    void setClientHandler(ClientHandler handler);
    
    // 设置文件传输目录
    void setFileDirectory(const std::string& dir);
    
#ifdef USE_SPDLOG
    // 设置日志级别
    void setLogLevel(spdlog::level::level_enum level);
#endif

private:
    bool initializeSocket();
    void cleanup();
    void setupLogger();
    void createLogDirectory();
    void handleClient(SOCKET clientSocket);
    std::string receiveMessage(SOCKET clientSocket);
    bool sendMessage(SOCKET clientSocket, const std::string& message);
    void logInfo(const std::string& message);
    void logError(const std::string& message);
    void logDebug(const std::string& message);
    
    // 文件传输相关方法
    void handleFileCommand(SOCKET clientSocket, const std::string& command);
    bool handleFileUpload(SOCKET clientSocket, const std::string& filename, size_t fileSize);
    bool handleFileDownload(SOCKET clientSocket, const std::string& filename);
    bool sendFileList(SOCKET clientSocket);
    bool createFileDirectory();
    std::string getFilePath(const std::string& filename);
    bool receiveFileData(SOCKET clientSocket, const std::string& filepath, size_t fileSize);
    bool sendFileData(SOCKET clientSocket, const std::string& filepath);

    int m_port;
    SOCKET m_serverSocket;
    bool m_running;
    ClientHandler m_clientHandler;
    std::string m_fileDirectory;

#ifdef USE_SPDLOG
    std::shared_ptr<spdlog::logger> m_logger;
#endif

#ifdef _WIN32
    WSADATA m_wsaData;
    bool m_wsaInitialized;
#endif
};
