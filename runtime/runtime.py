from typing import List, Dict, Any
from runtime.memory.allocator import Allocator
from runtime.scheduler import Scheduler
from compiler.tensor_partitioner import TensorPartitioner
from hardware.driver import HardwareDriver
from telemetry.broker import TelemetryBroker
from telemetry.schema import EventType

class Runtime:
    def __init__(self, allocator: Allocator, scheduler: Scheduler, requests: List, broker: TelemetryBroker, closed_loop: bool = True):
        self.allocator = allocator
        self.scheduler = scheduler
        self.broker = broker
        self.closed_loop = closed_loop
        self.requests_to_arrive = sorted(requests, key=lambda r: r.arrival_time)
        
        self.running_requests = []
        self.completed_requests = []
        self.current_cycle = 0

        # Compiler & Hardware Engine
        self.partitioner = TensorPartitioner(tile_dim=4, bytes_per_element=4)
        self.driver = HardwareDriver()

    def run(self) -> Dict[str, Any]:
        while self.requests_to_arrive or self.scheduler.has_waiting_requests() or self.running_requests:
            
            # take arrivals
            while self.requests_to_arrive and self.requests_to_arrive[0].arrival_time <= self.current_cycle:
                req = self.requests_to_arrive.pop(0)
                self.scheduler.add_request(req)
                self.broker.log(self.current_cycle, EventType.REQUEST_ARRIVED, src_id=3, p1=req.request_id, p2=req.kv_blocks)

            # Update memory state
            mem_status = self.allocator.memory_status()
            self.broker.update_memory_state(
                utilization=mem_status["utilization"],
                active_count=len(self.running_requests)
            )

            # Closed-Loop Scheduling Decision
            urgent_mode = self.closed_loop and self.broker.is_memory_congested()

            # Schedule & Allocate
            while self.scheduler.has_waiting_requests():
                candidate = self.scheduler.schedule(self.current_cycle, prioritize_urgent=urgent_mode)
                if not candidate:
                    break

                if self.allocator.allocate(candidate, self.current_cycle):
                    candidate.start_request(self.current_cycle)
                    self.running_requests.append(candidate)
                    self.broker.log(self.current_cycle, EventType.MEMORY_ALLOCATED, src_id=2, p1=candidate.request_id, p2=candidate.kv_blocks)
                else:
                    self.scheduler.requeue_front(candidate)
                    self.broker.log(self.current_cycle, EventType.ALLOCATION_STALL, src_id=2, p1=candidate.request_id, p2=candidate.kv_blocks)
                    break

            # Hardware Execution & Telemetry Ingestion
            for req in self.running_requests:
                hw_instructions = []
                for bid in req.allocated_block_ids:
                    dram_addr = self.allocator.blocks[bid].dram_base_addr
                    hw_instructions.extend(
                        self.partitioner.partition_matmul(m=4, n=4, k=4, dram_a_base=dram_addr, dram_b_base=0x00)
                    )
                
                # Run on accelerator; ingest hardware tokens
                hw_cycles, raw_hw_telemetry = self.driver.execute_and_collect_telemetry(hw_instructions)
                if raw_hw_telemetry:
                    self.broker.ingest_hardware_binary(raw_hw_telemetry)

            # advance tokens
            still_running = []
            for req in self.running_requests:
                if req.advance_request(self.current_cycle):
                    self.allocator.free(req)
                    self.completed_requests.append(req)
                    if req.finish_cycle > req.slo_deadline:
                        self.broker.log(self.current_cycle, EventType.SLO_VIOLATION, src_id=1, p1=req.request_id, p2=req.finish_cycle - req.slo_deadline)
                    self.broker.log(self.current_cycle, EventType.REQUEST_FINISHED, src_id=3, p1=req.request_id, p2=req.finish_cycle - req.arrival_time)
                else:
                    still_running.append(req)
            self.running_requests = still_running

            self.current_cycle += 1

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        latencies = [r.finish_cycle - r.arrival_time for r in self.completed_requests]
        violations = sum(1 for r in self.completed_requests if r.finish_cycle > r.slo_deadline)
        total = len(self.completed_requests)

        avg_lat = sum(latencies) / total if total > 0 else 0.0
        attainment = ((total - violations) / total * 100.0) if total > 0 else 100.0

        return {
            "completed_requests": total,
            "total_cycles": self.current_cycle,
            "average_latency": round(avg_lat, 2),
            "slo_violations": violations,
            "slo_attainment": f"{round(attainment, 2)}%",
            "telemetry_events": len(self.broker.events)
        }