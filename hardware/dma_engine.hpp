#ifndef DMA_ENGINE_HPP
#define DMA_ENGINE_HPP

#include <cstdint>
#include <vector>
#include "sram.hpp"

class DMAEngine {
public:
    static constexpr uint32_t BYTES_PER_CYCLE = 16; // 16B per cycle memory bandwidth for transfer from DRAM to SRAM

    bool is_transferring = false;
    uint32_t transfer_end_cycle = 0;
    uint8_t active_bank = 0;

    // will return number of cycles to tranfer data or if in transfer
    bool can_start_transfer(const ScratchpadSRAM& sram, uint8_t target_bank) const {
        return !is_transferring && sram.is_bank_available(target_bank);
    }

    uint32_t start_transfer(uint32_t size_bytes, uint8_t target_bank, uint32_t current_cycle, ScratchpadSRAM& sram) {
        uint32_t transfer_cycles = (size_bytes + BYTES_PER_CYCLE - 1) / BYTES_PER_CYCLE;
        sram.lock_bank(target_bank, transfer_cycles, current_cycle); // lock bank for the calculated cycles
        return transfer_cycles; // number of cycles so loop doesn't constantly check is transfer is over
};

#endif