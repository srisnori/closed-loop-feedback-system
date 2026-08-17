# define instructions
from enum import IntEnum
from dataclasses import dataclass

class Opcode(IntEnum):
    NOP = 0x00
    DMA_LOAD_DRAM_TO_SRAM = 0x01
    DMA_STORE_SRAM_TO_DRAM= 0x02
    MATMUL_TILE = 0x03
    SYNC = 0x04
    HALT = 0xFF

@dataclass(slots=True)
class Instruction:
    opcode: Opcode
    src_addr: int = 0
    dst_addr: int = 0
    size_bytes: int = 0
    sram_bank: int = 0  # 0 or 1