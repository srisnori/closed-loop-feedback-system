import struct
from enum import IntEnum
from dataclasses import dataclass

class EventType(IntEnum):
    # hardware events (0x01 - 0x1F)
    DMA_TRANSFER_START      = 0x01
    DMA_TRANSFER_DONE       = 0x02
    SRAM_BANK_CONFLICT      = 0x03
    SYSTOLIC_COMPUTE_START  = 0x04
    SYSTOLIC_COMPUTE_DONE   = 0x05
    HARDWARE_STALL          = 0x06

    # runtime events (0x20 - 0x3F)
    REQUEST_ARRIVED         = 0x20
    REQUEST_SCHEDULED       = 0x21
    MEMORY_ALLOCATED        = 0x22
    MEMORY_FREED            = 0x23
    ALLOCATION_STALL        = 0x24
    REQUEST_FINISHED        = 0x25
    SLO_VIOLATION           = 0x26

@dataclass(slots=True)
class EventToken:
    timestamp_cycle: int # uint32 (4 bytes)
    event_type: EventType # uint16 (2 bytes)
    source_id: int # uint16 (2 bytes): 0=HW, 1=Scheduler, 2=Memory, 3=Runtime
    payload_1: int # int32  (4 bytes)
    payload_2: int # int32  (4 bytes)

    # format: little endian uint32, uint16, uint16, int32, int32 -> 16 bytes 
    FORMAT = "<IHHi i"

    def pack(self) -> bytes:
        return struct.pack(
            self.FORMAT,
            self.timestamp_cycle,
            int(self.event_type),
            self.source_id,
            self.payload_1,
            self.payload_2
        )

    @classmethod
    def unpack(cls, raw_bytes: bytes) -> "EventToken":
        cycle, etype, src, p1, p2 = struct.unpack(cls.FORMAT, raw_bytes)
        return cls(cycle, EventType(etype), src, p1, p2)