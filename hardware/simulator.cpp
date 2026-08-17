#include <iostream>
#include <vector>
#include "../include/isa.hpp"
#include "../include/sram.hpp"
#include "../include/dma_engine.hpp"
#include "../include/systolic_array.hpp"

class HardwareAccelerator {
public:
    ScratchpadSRAM sram;
    DMAEngine dma;
    SystolicArray4x4 systolic_array;
    uint32_t current_cycle = 0;

    bool execute_program(const std::vector<Instruction>& program) {
        size_t pc = 0;
        while (pc < program.size()) {
            const auto& inst = program[pc];

            switch (inst.opcode) {
                case Opcode::DMA_LOAD_DRAM_TO_SRAM:
                case Opcode::DMA_STORE_SRAM_TO_DRAM:
                    if (dma.can_start_transfer(sram, inst.sram_bank)) {
                        // start transfer and get the cycle time
                        uint32_t transfer_cycles = dma.start_transfer(inst.size_bytes, inst.sram_bank, current_cycle, sram);
                        
                        // teleport clock forward and unlock the bank
                        current_cycle += transfer_cycles;
                        sram.unlock_bank(inst.sram_bank);
                        pc++;
                    }
                    break;

                case Opcode::MATMUL_TILE:
                    // using bank 2 for output 
                    if (systolic_array.can_start_compute(sram, 2)) { 
                        // start math calculation and get the wavefront cycle time (7)
                        uint32_t compute_cycles = systolic_array.start_tile_compute(2, current_cycle, sram);
                        
                        // teleport clock forward 7 cycles and unlock  bank
                        current_cycle += compute_cycles;
                        sram.unlock_bank(2);
                        pc++;
                    }
                    break;

                case Opcode::SYNC:
                    pc++;
                    break;

                case Opcode::HALT:
                    return true;

                case Opcode::NOP:
                default:
                    pc++;
                    break;
            }
        }
        return true;
    }
};

int main() {
    HardwareAccelerator acc;
    // Updated sample program to match our new 3-bank compiler logic (Loading to 0 and 1, storing from 2)
    std::vector<Instruction> sample_prog = {
        {Opcode::DMA_LOAD_DRAM_TO_SRAM, 0x1000, 0x00, 64, 0}, // 4 cycles (64B / 16B bandwidth)
        {Opcode::DMA_LOAD_DRAM_TO_SRAM, 0x2000, 0x00, 64, 1}, // 4 cycles
        {Opcode::SYNC, 0, 0, 0, 0}, // 0 cycles
        {Opcode::MATMUL_TILE, 0, 0, 0, 2}, // 7 cycles 
        {Opcode::HALT, 0, 0, 0, 0}
    };

    acc.execute_program(sample_prog);
    std::cout << "Cycle: " << acc.current_cycle << std::endl;
    return 0;
}