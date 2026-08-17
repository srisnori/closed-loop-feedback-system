class Block:
    # 1 Block = 16 tokens * 64 hidden_dim * 4 bytes (float32) = 4096 Bytes (4KB)
    BLOCK_SIZE_BYTES = 4096

    def __init__(self, block_id: int):
        self.block_id = block_id
        self.dram_base_addr = block_id * self.BLOCK_SIZE_BYTES
        self.request_id = None
        self.last_accessed_cycle = 0
    
    def is_free(self) -> bool:
        return self.request_id is None

    def assign(self, request_id: int, cycle: int = 0):
        self.request_id = request_id
        self.last_accessed_cycle = cycle

    def release(self):
        self.request_id = None
        self.last_accessed_cycle = 0