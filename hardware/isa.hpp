#ifndef ISA_HPP
#define ISA_HPP
#include <cstdint>

enum class Opcode : uint8_t {
    NOP = 0x00,
    DMA_LOAD_DRAM_TO_SRAM = 0x01,
    DMA_STORE_SRAM_TO_DRAM = 0x02,
    MATMUL_TILE = 0x03,
    SYNC = 0x04,
    HALT = 0xFF
};

struct Instruction {
    Opcode opcode;
    uint32_t src_addr;
    uint32_t dst_addr;
    uint16_t size_bytes;
    uint8_t  sram_bank; // 0 or 1
};

#endif