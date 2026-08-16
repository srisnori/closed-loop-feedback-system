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

    void step() {
        current_cycle++;
        sram.update_cycle(current_cycle);
        dma.update_cycle(current_cycle);
        systolic_array.update_cycle(current_cycle);
    }

    bool execute_program(const std::vector<Instruction>& program) {
        size_t pc = 0;
        while (pc < program.size()) {
            const auto& inst = program[pc];

            switch (inst.opcode) {
                case Opcode::DMA_LOAD_DRAM_TO_SRAM:
                case Opcode::DMA_STORE_SRAM_TO_DRAM:
                    if (dma.can_start_transfer(sram, inst.sram_bank)) {
                        dma.start_transfer(inst.size_bytes, inst.sram_bank, current_cycle, sram);
                        pc++;
                    }
                    break;

                case Opcode::MATMUL_TILE:
                    if (systolic_array.can_start_compute(sram, inst.sram_bank)) {
                        systolic_array.start_tile_compute(inst.sram_bank, current_cycle, sram);
                        pc++;
                    }
                    break;

                case Opcode::SYNC:
                    if (!dma.is_transferring && !systolic_array.is_computing) {
                        pc++;
                    }
                    break;

                case Opcode::HALT:
                    return true;

                case Opcode::NOP:
                default:
                    pc++;
                    break;
            }
            step();
        }
        return true;
    }
};

int main() {
    HardwareAccelerator acc;
    std::vector<Instruction> sample_prog = {
        {Opcode::DMA_LOAD_DRAM_TO_SRAM, 0x1000, 0x00, 64, 0},
        {Opcode::DMA_LOAD_DRAM_TO_SRAM, 0x2000, 0x00, 64, 1},
        {Opcode::SYNC, 0, 0, 0, 0},
        {Opcode::MATMUL_TILE, 0, 0, 0, 0},
        {Opcode::HALT, 0, 0, 0, 0}
    };

    acc.execute_program(sample_prog);
    std::cout << "Hardware execution finished cleanly at cycle: " << acc.current_cycle << std::endl;
    return 0;
}