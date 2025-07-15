#pragma once

#define RSVP_SERVICE_VERSION "2.3.0"

#include <stdint.h>

constexpr uint32_t RSVP_ERR_SESSION_LIMITED = 7900;
constexpr uint32_t RSVP_ERR_SESSION_CONFLICT = 7901;
constexpr uint32_t RSVP_ERR_RCM_TIMEDOUT = 7902;
constexpr uint32_t RSVP_ERR_REG_FAILED = 7903;
constexpr uint32_t RSVP_ERR_CTRL_PROC_FAILED = 7904;
constexpr uint32_t RSVP_ERR_CLIENT_VERSION = 7905;
constexpr uint32_t RSVP_ERR_AUTH_FAILED = 7906;
constexpr uint32_t RSVP_ERR_MONITOR_INVALID = 7907;
constexpr uint32_t RSVP_ERR_CONSOLE_SESSION_NOT_FOUND = 7908;
constexpr uint32_t RSVP_ERR_SEND_SAS_FAILED = 7909;
constexpr uint32_t RSVP_ERR_IDD_PROC_FAILED = 7910;
constexpr uint32_t RSVP_ERR_CLIP_PROC_FAILED = 7911;
constexpr uint32_t RSVP_ERR_LICENSE_EXCEEDED = 7912;
constexpr uint32_t RSVP_ERR_SCREEN_PROC_FAILED = 7913;
constexpr uint32_t RSVP_ERR_HOMEDIR_NOT_FOUND = 7914;
constexpr uint32_t RSVP_ERR_CREATE_SESSION_FILE_FAILED = 7915;
constexpr uint32_t RSVP_ERR_START_SESSION_FAILED = 7916;

constexpr uint32_t RSVP_SIG_CLIENT_HEARTBEAT = 0;
constexpr uint32_t RSVP_SIG_CONSOLE_SESSION_CHANGED = 1;
constexpr uint32_t RSVP_SIG_CONSOLE_CTRL_RESTART = 2;
constexpr uint32_t RSVP_SIG_CONSOLE_SESSION_REUSED = 3;
constexpr uint32_t RSVP_SIG_CONSOLE_CLIP_RESTART = 4;
constexpr uint32_t RSVP_SIG_CLIENT_SAS = 5;
constexpr uint32_t RSVP_SIG_CLIENT_LOCK_SCREEN = 6;
constexpr uint32_t RSVP_SIG_CONSOLE_SCREEN_RESTART = 7;

namespace rsvp
{
	enum class RequestType
	{
		IGNORED,
		GREETING,
		CLIENT,
		RCM,
		MGMT,
		TRANS,
		CONSOLE,
	};

	enum class ResponseStatus
	{
		SUCCESS,
		FAILED,
		READY,
		IGNORED,
	};

	enum class VideoQuality
	{
		AUTO,
		SLD,
		LD,
		MD,
		HD,
		SHD
	};

	enum class TransType
	{
		CONTROL,
		VIDEO,
		CLIPBOARD_IN,
		CLIPBOARD_OUT,
		MOUSE_POINTER,
		VIDEO_REQ,
	};

	enum class TerminalType
	{
		CONSOLE,
		SESSION,
	};

	enum class ClipboardDataType
	{
		TEXT,
		IMAGE,
		FILE,
		DIRECTORY,
		META,
	};

	enum class ClipboardTransType
	{
		CLIP_IN,
		CLIP_OUT,
	};

#pragma pack(1)

	struct MonitorInfo
	{
		uint16_t width;
		uint16_t height;
		uint16_t scale;
	};

	struct ClientLoginRequest
	{
		char domain[40];
		char username[60];
		char password[60];
		char version[20];
		VideoQuality quality;
		MonitorInfo monitors[4];
	};

	struct ConsoleLoginRequest
	{
		char rkey[33];
		char version[20];
		VideoQuality quality;
		MonitorInfo monitors[4];
	};

	struct ServerResponse
	{
		ResponseStatus status;
		uint32_t code;
		uint32_t session;
		char token[33];
		char message[100];
	};

	struct ClientSignal
	{
		uint32_t code;
		char message[100];
	};

	struct RCMRequest
	{
		uint32_t sequence;
		char domain[40];
		char username[60];
		char password[60];
		uint16_t ttl;
		bool operator==(const RCMRequest &other) const
		{
			return sequence == other.sequence;
		}
	};

	struct RCMResponse
	{
		uint32_t sequence;
		uint32_t code;
		uint32_t session;
		bool operator==(const RCMResponse &other) const
		{
			return sequence == other.sequence;
		}
	};

	struct ClientTransRequest
	{
		TransType type;
		char token[33];
		char clientUID[33];
		uint16_t index;
	};

	struct LocalTransRequest
	{
		TransType type;
		uint32_t session;
		uint16_t index;
	};

	struct TransResponse
	{
		ResponseStatus status;
		char message[100];
	};

	struct VideoTrackInfo
	{
		uint16_t seq;
		uint32_t length;
		int64_t timestamp;
		uint16_t width;
		uint16_t height;
		uint16_t scale;
	};

	struct MousePoint
	{
		int32_t x;
		int32_t y;
	};

	struct MouseControlInfo
	{
		MousePoint point;
		uint32_t msg;
		uint32_t modifier;
		uint64_t action;
	};

	/*
	 * code: Qt::key
	 * modifier:
	 *   NoModifier           = 0x00000000,
	 *   ShiftModifier        = 0x02000000,
	 *   ControlModifier      = 0x04000000,
	 *   AltModifier          = 0x08000000,
	 *   MetaModifier         = 0x10000000,
	 *   KeypadModifier       = 0x20000000,
	 *   GroupSwitchModifier  = 0x40000000,
	 *   KeyboardModifierMask = 0xfe000000
	 * action: key down(1) or up(0)
	 */
	struct KeyboardControlInfo
	{
		uint32_t code;
		uint32_t modifier;
		uint32_t action;
	};

	struct ControlTrackPkg
	{
		MouseControlInfo mouse;
		KeyboardControlInfo keyboard;
		int64_t timestamp;
		uint16_t display;
	};

	struct ClipboardDataDesc
	{
		ClipboardDataType dataType;
		ClipboardTransType transType;
		char clientID[33];
		uint32_t length;
		uint32_t offset;
		uint32_t sequence;
	};

	struct DXGI_OUTDUPL_POINTER_SHAPE_INFO
	{
		uint32_t Type;
		uint32_t Width;
		uint32_t Height;
		uint32_t Pitch;
		MousePoint HotSpot;
	};

	struct MousePointerDesc
	{
		uint16_t seq;
		DXGI_OUTDUPL_POINTER_SHAPE_INFO shape;
		uint32_t length;
		int64_t timestamp;
	};

	struct VideoReqPkg
	{
		uint8_t type; /* always vdsFramebufferUpdateRequest */
		uint8_t incremental;
		uint16_t x;
		uint16_t y;
		uint16_t w;
		uint16_t h;
	};

#pragma pack()

}
