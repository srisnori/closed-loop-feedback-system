#ifndef TELEMETRY_HPP
#define TELEMETRY_HPP

#include <cstdint>
#include <vector>

enum class EventType : uint16_t {
    DMA_TRANSFER_START      = 0x01,
    DMA_TRANSFER_DONE       = 0x02,
    SRAM_BANK_CONFLICT      = 0x03,
    SYSTOLIC_COMPUTE_START  = 0x04,
    SYSTOLIC_COMPUTE_DONE   = 0x05,
    HARDWARE_STALL          = 0x06
};

#pragma pack(push, 1)
struct EventToken {
    uint32_t timestamp_cycle; // 4 bytes
    uint16_t event_type;      // 2 bytes
    uint16_t source_id;       // 2 bytes (0 = Hardware)
    int32_t  payload_1;       // 4 bytes
    int32_t  payload_2;       // 4 bytes
};
#pragma pack(pop)

static_assert(sizeof(EventToken) == 16, "EventToken must be exactly 16 bytes for binary ABI alignment");

class TelemetryCollector {
public:
    std::vector<EventToken> ring_buffer;

    void emit(uint32_t cycle, EventType type, int32_t p1 = 0, int32_t p2 = 0) {
        ring_buffer.push_back({
            cycle,
            static_cast<uint16_t>(type),
            0, // Source: Hardware
            p1,
            p2
        });
    }

    void clear() {
        ring_buffer.clear();
    }

    size_t count() const {
        return ring_buffer.size();
    }
};

#endif