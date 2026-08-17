from telemetry.schema import EventToken, EventType
from telemetry.broker import TelemetryBroker

def test_telemetry_system():
    broker = TelemetryBroker(history_window=10)

    # 1. Test binary serialization & round-trip
    token = EventToken(
        timestamp_cycle=1054,
        event_type=EventType.SRAM_BANK_CONFLICT,
        source_id=0,
        payload_1=1, # Bank 1
        payload_2=7  # 7 cycle stall
    )
    packed_bytes = token.pack()
    assert len(packed_bytes) == 16, f"Expected 16 bytes, got {len(packed_bytes)}"
    
    unpacked_token = EventToken.unpack(packed_bytes)
    assert unpacked_token.timestamp_cycle == 1054
    assert unpacked_token.event_type == EventType.SRAM_BANK_CONFLICT
    assert unpacked_token.payload_1 == 1

    # 2. Test broker event logging & feedback triggers
    broker.log(10, EventType.REQUEST_ARRIVED, src_id=3, p1=101, p2=0)
    broker.log(12, EventType.ALLOCATION_STALL, src_id=2, p1=101, p2=0)
    broker.log(13, EventType.ALLOCATION_STALL, src_id=2, p1=101, p2=0)
    broker.log(14, EventType.ALLOCATION_STALL, src_id=2, p1=101, p2=0)
    broker.update_memory_state(utilization=0.82, active_count=4)

    # 3. Verify closed-loop signals
    assert broker.is_memory_congested() is True

    print("Telemetry module verified: 16-byte ABI packing, parsing, and signal triggers pass.")
    print("Summary Snapshot:", broker.get_summary())

if __name__ == "__main__":
    test_telemetry_system()