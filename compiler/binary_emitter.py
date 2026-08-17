# translates all the instructions into one 12 byte binary for hardware
import struct
from typing import List
from compiler.isa import Instruction

class BinaryEmitter:
    # opcode (1B), src_addr (4B), dst_addr (4B), size_bytes (2B), sram_bank (1B) -> 12 bytes
    INSTRUCTION_FORMAT = "<BIIHB" # 

    @classmethod
    def emit_binary(cls, instructions: List[Instruction]) -> bytes:
        binary_data = bytearray()
        for inst in instructions:
            packed = struct.pack( # flats it out so C++ can map a ptr to just read O(1)
                cls.INSTRUCTION_FORMAT,
                int(inst.opcode),
                inst.src_addr,
                inst.dst_addr,
                inst.size_bytes,
                inst.sram_bank
            )
            binary_data.extend(packed)
        return bytes(binary_data)

    @classmethod
    def save_to_file(cls, instructions: List[Instruction], filepath: str) -> None:
        binary_data = cls.emit_binary(instructions)
        with open(filepath, "wb") as f:
            f.write(binary_data)