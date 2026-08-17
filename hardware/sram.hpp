#ifndef SRAM_HPP
#define SRAM_HPP

#include <cstdint>
#include <vector>
#include <array>

class ScratchpadSRAM {
public:
    static constexpr size_t NUM_BANKS = 3; 
    static constexpr size_t BANK_SIZE_BYTES = 4096;

    std::array<std::vector<uint8_t>, NUM_BANKS> memory;
    std::array<bool, NUM_BANKS> bank_busy;

    ScratchpadSRAM() {
        for (size_t i = 0; i < NUM_BANKS; ++i) {
            memory[i].resize(BANK_SIZE_BYTES, 0);
            bank_busy[i] = false;
        }
    }

    bool is_bank_available(uint8_t bank) const {
        if (bank >= NUM_BANKS) return false;
        return !bank_busy[bank];
    }

    void lock_bank(uint8_t bank) { // lock bank during transfer or if calculation starts
        if (bank < NUM_BANKS) {
            bank_busy[bank] = true;
        }
    }

    void unlock_bank(uint8_t bank) { // unlock bank when fast-forward finishes
        if (bank < NUM_BANKS) {
            bank_busy[bank] = false;
        }
    }
};

#endif