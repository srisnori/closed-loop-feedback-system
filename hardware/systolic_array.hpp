#ifndef SYSTOLIC_ARRAY_HPP
#define SYSTOLIC_ARRAY_HPP

#include <cstdint>
#include <array>
#include "sram.hpp"

class SystolicArray4x4 {
public:
    static constexpr size_t DIM = 4;
    static constexpr uint32_t WAVEFRONT_CYCLES = (2 * DIM) - 1; // 7 cycles for 4x4

    bool is_computing = false;
    uint32_t compute_end_cycle = 0;
    uint8_t active_bank = 0;

    bool can_start_compute(const ScratchpadSRAM& sram, uint8_t bank) const {
        return !is_computing && sram.is_bank_available(bank);
    }

    void start_tile_compute(uint8_t bank, uint32_t current_cycle, ScratchpadSRAM& sram) {
        is_computing = true;
        compute_end_cycle = current_cycle + WAVEFRONT_CYCLES;
        active_bank = bank;
        sram.lock_bank(bank, WAVEFRONT_CYCLES, current_cycle);
    }

    void update_cycle(uint32_t current_cycle) {
        if (is_computing && current_cycle >= compute_end_cycle) {
            is_computing = false;
        }
    }
};

#endif