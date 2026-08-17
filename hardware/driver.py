import ctypes
import os
from typing import List, Tuple
from compiler.isa import Instruction
from compiler.binary_emitter import BinaryEmitter

lib_path = os.path.join(os.path.dirname(__file__), "libaccel.so")
lib = ctypes.CDLL(lib_path)

lib.create_accelerator.restype = ctypes.c_void_p
lib.destroy_accelerator.argtypes = [ctypes.c_void_p]
lib.destroy_accelerator.restype = None

lib.run_hardware_binary.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
lib.run_hardware_binary.restype = ctypes.c_uint32

lib.get_hardware_telemetry.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
lib.get_hardware_telemetry.restype = ctypes.c_uint32

class HardwareDriver:
    def __init__(self):
        self.accel_ptr = lib.create_accelerator()
        self._telemetry_buf_size = 65536  # 64 KB buffer
        self._telemetry_buf = (ctypes.c_uint8 * self._telemetry_buf_size)()

    def execute_and_collect_telemetry(self, instructions: List[Instruction]) -> Tuple[int, bytes]:
        if not instructions or not self.accel_ptr:
            return 0, b""

        binary_bytes = BinaryEmitter.emit_binary(instructions)
        c_buffer = (ctypes.c_uint8 * len(binary_bytes)).from_buffer_copy(binary_bytes)
        
        cycles = lib.run_hardware_binary(self.accel_ptr, c_buffer, len(binary_bytes))
        bytes_copied = lib.get_hardware_telemetry(self.accel_ptr, self._telemetry_buf, self._telemetry_buf_size)
        raw_telemetry = bytes(self._telemetry_buf[:bytes_copied])

        return cycles, raw_telemetry

    def close(self):
        if hasattr(self, "accel_ptr") and self.accel_ptr:
            lib.destroy_accelerator(self.accel_ptr)
            self.accel_ptr = None

    def __del__(self):
        # Let OS reclaim process memory cleanly on shutdown to prevent GC race crashes
        pass