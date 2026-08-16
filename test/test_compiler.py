from compiler.tensor_partitioner import TensorPartitioner
from compiler.binary_emitter import BinaryEmitter

def test_compile():
    partitioner = TensorPartitioner(tile_dim=4, bytes_per_element=4)
    instructions = partitioner.partition_matmul(m=8, n=8, k=4, dram_a_base=0x1000, dram_b_base=0x2000)
    binary = BinaryEmitter.emit_binary(instructions)
    print(f"Generated {len(instructions)} instructions ({len(binary)} bytes).")

if __name__ == "__main__":
    test_compile()