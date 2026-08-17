# make allocation decisions based on if block.py determines if block is free or not
from runtime.memory.block import Block

class Allocator:
    def __init__(self, total_blocks):
        self.total_blocks = total_blocks
        self.blocks = [Block(i) for i in range(total_blocks)]
    
    def allocate(self, request, current_cycle=0):
        free_blocks = [b for b in self.blocks if b.is_free()]
        if len(free_blocks) < request.kv_blocks:
            return False
        
        allocated = free_blocks[:request.kv_blocks]
        request.allocated_block_ids = []
        for block in allocated:
            block.assign(request.request_id, current_cycle)
            request.allocated_block_ids.append(block.block_id)
        return True
    
    def free(self, request):
        for block in self.blocks:
            if block.request_id == request.request_id:
                block.release()
        request.allocated_block_ids = []

    def get_free_blocks(self):
        return [b for b in self.blocks if b.is_free()]
    
    def get_allocated_blocks(self):
        return [b for b in self.blocks if not b.is_free()]
    
    def memory_status(self):
        free_cnt = len(self.get_free_blocks())
        alloc_cnt = len(self.get_allocated_blocks())
        utilization = alloc_cnt / self.total_blocks if self.total_blocks > 0 else 0.0
        
        pressure = "LOW"
        if utilization >= 0.85:
            pressure = "HIGH"
        elif utilization >= 0.60:
            pressure = "MEDIUM"

        return {
            "total_blocks": self.total_blocks,
            "free_blocks": free_cnt,
            "allocated_blocks": alloc_cnt,
            "utilization": utilization,
            "pressure": pressure
        }