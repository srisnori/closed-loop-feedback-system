from typing import List, Tuple
from compiler.isa import Instruction, Opcode

class TensorPartitioner:
    def __init__(self, tile_dim: int = 4, bytes_per_element: int = 4):
        self.tile_dim = tile_dim
        self.tile_size_bytes = tile_dim * tile_dim * bytes_per_element

    def partition_matmul(self, m: int, n: int, k: int, dram_a_base: int, dram_b_base: int) -> List[Instruction]:
        # Decomposes huge matrix multiplication into tiles 
        instructions: List[Instruction] = []
        
        m_tiles = (m + self.tile_dim - 1) // self.tile_dim
        n_tiles = (n + self.tile_dim - 1) // self.tile_dim
        k_tiles = (k + self.tile_dim - 1) // self.tile_dim

        for i in range(m_tiles):
            for j in range(n_tiles):
                for l in range(k_tiles):
                    # load Tile A into Bank 0
                    addr_a = dram_a_base + (i * k_tiles + l) * self.tile_size_bytes
                    instructions.append(Instruction(
                        opcode=Opcode.DMA_LOAD_DRAM_TO_SRAM,
                        src_addr=addr_a,
                        dst_addr=0,
                        size_bytes=self.tile_size_bytes,
                        sram_bank=0
                    ))

                    # load Tile B into Bank 1
                    addr_b = dram_b_base + (l * n_tiles + j) * self.tile_size_bytes
                    instructions.append(Instruction(
                        opcode=Opcode.DMA_LOAD_DRAM_TO_SRAM,
                        src_addr=addr_b,
                        dst_addr=0,
                        size_bytes=self.tile_size_bytes,
                        sram_bank=1
                    ))

                    # wait for transfers to complete
                    instructions.append(Instruction(opcode=Opcode.SYNC))

                    # compute on loaded tiles
                    instructions.append(Instruction(opcode=Opcode.MATMUL_TILE, sram_bank=0))
        instructions.append(Instruction(opcode=Opcode.HALT))
        return instructions