#pragma once

#include <stdint.h>


#define VRC_PROXY_STATUS_OK 0
#define VRC_PROXY_STATUS_CONNECT_ERR 1

namespace vappvrc
{
#pragma pack(1)
    struct ProxyRequest
    {
        char tgt_ip[16];
        uint16_t tgt_port;
    };

    struct ProxyResponse
    {
        uint16_t status;
        char msg[100];
    };
#pragma pack()
}
