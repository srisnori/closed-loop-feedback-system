#ifndef SYSTOLIC_ARRAY_HPP
#define SYSTOLIC_ARRAY_HPP

#include <cstdint>
#include <array>
#include "sram.hpp"

class SystolicArray4x4 {
public:
    static constexpr size_t DIM = 4;
    static constexpr uint32_t WAVEFRONT_CYCLES = (2 * DIM) - 1; // 7 cycles for 4x4; moves in waves 

    bool is_computing = false;
    uint8_t active_bank = 0;

    bool can_start_compute(const ScratchpadSRAM& sram, uint8_t bank) const {
        return !is_computing && sram.is_bank_available(bank);
    }

    // returns 7 cycles so the loop can move the clock forward
    uint32_t start_tile_compute(uint8_t bank, uint32_t current_cycle, ScratchpadSRAM& sram) {
        sram.lock_bank(bank); // lock bank so no other part of the chip messes with the numbers
        active_bank = bank;
        return WAVEFRONT_CYCLES; // return 7 cycles so the main loop can skip the waiting process
    }
};
#endif