#include "isa.hpp"
#include "dram.hpp"
#include "sram.hpp"
#include "dma_engine.hpp"
#include "systolic_array.hpp"
#include "../telemetry/telemetry.hpp"
#include <vector>
#include <cstring>

class HardwareAccelerator {
public:
    OffChipDRAM dram;
    ScratchpadSRAM sram;
    DMAEngine dma;
    SystolicArray4x4 systolic_array;
    TelemetryCollector telemetry;
    uint32_t current_cycle = 0;

    void step() {
        current_cycle++;
        sram.update_cycle(current_cycle);
        dma.update_cycle(current_cycle);
        systolic_array.update_cycle(current_cycle);
    }

    uint32_t execute_binary(const uint8_t* binary_data, size_t size_bytes) {
        if (!binary_data || size_bytes == 0) return current_cycle;

        size_t num_instructions = size_bytes / sizeof(Instruction);
        std::vector<Instruction> program(num_instructions);
        std::memcpy(program.data(), binary_data, size_bytes);

        size_t pc = 0;
        while (pc < program.size()) {
            const auto& inst = program[pc];

            switch (inst.opcode) {
                case Opcode::DMA_LOAD_DRAM_TO_SRAM:
                case Opcode::DMA_STORE_SRAM_TO_DRAM:
                    if (dma.can_start_transfer(sram, inst.sram_bank)) {
                        telemetry.emit(current_cycle, EventType::DMA_TRANSFER_START, inst.sram_bank, inst.size_bytes);
                        dma.start_transfer(inst.size_bytes, inst.sram_bank, current_cycle, sram);
                        pc++;
                    } else {
                        telemetry.emit(current_cycle, EventType::HARDWARE_STALL, inst.sram_bank, 1);
                    }
                    break;

                case Opcode::MATMUL_TILE:
                    if (systolic_array.can_start_compute(sram, inst.sram_bank)) {
                        telemetry.emit(current_cycle, EventType::SYSTOLIC_COMPUTE_START, inst.sram_bank, 4);
                        systolic_array.start_tile_compute(inst.sram_bank, current_cycle, sram);
                        pc++;
                    } else {
                        telemetry.emit(current_cycle, EventType::SRAM_BANK_CONFLICT, inst.sram_bank, 1);
                    }
                    break;

                case Opcode::SYNC:
                    if (!dma.is_transferring && !systolic_array.is_computing) {
                        pc++;
                    }
                    break;

                case Opcode::HALT:
                    return current_cycle;

                case Opcode::NOP:
                default:
                    pc++;
                    break;
            }
            step();
        }
        return current_cycle;
    }
};

extern "C" {
    HardwareAccelerator* create_accelerator() {
        return new HardwareAccelerator();
    }

    uint32_t run_hardware_binary(HardwareAccelerator* acc, const uint8_t* binary_data, size_t size_bytes) {
        if (!acc || !binary_data || size_bytes == 0) return 0;
        return acc->execute_binary(binary_data, size_bytes);
    }

    uint32_t get_hardware_telemetry(HardwareAccelerator* acc, uint8_t* out_buffer, size_t max_bytes) {
        if (!acc || !out_buffer || max_bytes == 0) return 0;
        
        size_t total_bytes = acc->telemetry.ring_buffer.size() * sizeof(EventToken);
        size_t copy_bytes = (total_bytes > max_bytes) ? max_bytes : total_bytes;
        
        if (copy_bytes > 0) {
            std::memcpy(out_buffer, acc->telemetry.ring_buffer.data(), copy_bytes);
            acc->telemetry.clear();
        }
        return static_cast<uint32_t>(copy_bytes);
    }

    void destroy_accelerator(HardwareAccelerator* acc) {
        if (acc != nullptr) {
            delete acc;
        }
    }
}