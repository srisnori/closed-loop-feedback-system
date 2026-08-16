#ifndef DRAM_HPP
#define DRAM_HPP

#include <cstdint>
#include <vector>

class OffChipDRAM {
public:
    static constexpr size_t DRAM_SIZE_BYTES = 1024 * 1024; // 1MB simulated DRAM
    std::vector<uint8_t> memory;
    OffChipDRAM() : memory(DRAM_SIZE_BYTES, 0) {}
    
    uint8_t read(uint32_t addr) const {
        if (addr < DRAM_SIZE_BYTES) return memory[addr];
        return 0;
    }

    void write(uint32_t addr, uint8_t val) {
        if (addr < DRAM_SIZE_BYTES) memory[addr] = val;
    }
};

#endif