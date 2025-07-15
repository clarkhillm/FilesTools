#include <iostream>
#include <string>
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
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

class SocketClient {
private:
    SOCKET clientSocket;
#ifdef _WIN32
    WSADATA wsaData;
#endif

public:
    SocketClient() : clientSocket(INVALID_SOCKET) {
#ifdef _WIN32
        WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
    }

    ~SocketClient() {
        disconnect();
#ifdef _WIN32
        WSACleanup();
#endif
    }

    bool connect(const std::string& host, int port) {
        clientSocket = socket(AF_INET, SOCK_STREAM, 0);
        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Failed to create socket" << std::endl;
            return false;
        }

        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(port);
        
        if (inet_pton(AF_INET, host.c_str(), &serverAddr.sin_addr) <= 0) {
            std::cerr << "Invalid address" << std::endl;
            return false;
        }

        if (::connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "Connection failed" << std::endl;
            return false;
        }

        std::cout << "Connected to " << host << ":" << port << std::endl;
        return true;
    }

    void disconnect() {
        if (clientSocket != INVALID_SOCKET) {
            closesocket(clientSocket);
            clientSocket = INVALID_SOCKET;
        }
    }

    bool sendMessage(const std::string& message) {
        if (clientSocket == INVALID_SOCKET) return false;
        
        int result = send(clientSocket, message.c_str(), static_cast<int>(message.length()), 0);
        return result != SOCKET_ERROR;
    }

    std::string receiveMessage() {
        if (clientSocket == INVALID_SOCKET) return "";
        
        char buffer[1024];
        int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
        
        if (bytesReceived <= 0) return "";
        
        buffer[bytesReceived] = '\0';
        return std::string(buffer);
    }
};

int main() {
    std::cout << "=== Socket Client Test ===" << std::endl;
    
    SocketClient client;
    
    if (!client.connect("127.0.0.1", 8080)) {
        std::cerr << "Failed to connect to server" << std::endl;
        return 1;
    }
    
    std::cout << "Connected! Type messages (or 'quit' to exit):" << std::endl;
    
    std::string input;
    while (true) {
        std::cout << "> ";
        std::getline(std::cin, input);
        
        if (input == "quit" || input == "exit") {
            break;
        }
        
        if (client.sendMessage(input)) {
            std::string response = client.receiveMessage();
            std::cout << "Server response: " << response << std::endl;
        } else {
            std::cerr << "Failed to send message" << std::endl;
            break;
        }
    }
    
    std::cout << "Disconnecting..." << std::endl;
    return 0;
}
