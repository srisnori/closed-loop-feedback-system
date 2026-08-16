#ifndef SRAM_HPP
#define SRAM_HPP

#include <cstdint>
#include <vector>
#include <array>

class ScratchpadSRAM {
public:
    static constexpr size_t NUM_BANKS = 2;
    static constexpr size_t BANK_SIZE_BYTES = 4096;

    std::array<std::vector<uint8_t>, NUM_BANKS> memory;
    std::array<bool, NUM_BANKS> bank_busy;
    std::array<uint32_t, NUM_BANKS> busy_until_cycle;

    ScratchpadSRAM() {
        for (size_t i = 0; i < NUM_BANKS; ++i) {
            memory[i].resize(BANK_SIZE_BYTES, 0);
            bank_busy[i] = false;
            busy_until_cycle[i] = 0;
        }
    }

    void update_cycle(uint32_t current_cycle) {
        for (size_t i = 0; i < NUM_BANKS; ++i) {
            if (bank_busy[i] && current_cycle >= busy_until_cycle[i]) {
                bank_busy[i] = false;
            }
        }
    }

    bool is_bank_available(uint8_t bank) const {
        if (bank >= NUM_BANKS) return false;
        return !bank_busy[bank];
    }

    void lock_bank(uint8_t bank, uint32_t duration_cycles, uint32_t current_cycle) {
        if (bank < NUM_BANKS) {
            bank_busy[bank] = true;
            busy_until_cycle[bank] = current_cycle + duration_cycles;
        }
    }
};

#endif