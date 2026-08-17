from typing import List, Dict, Any, Deque
from collections import deque
from telemetry.schema import EventToken, EventType

class TelemetryBroker:
    def __init__(self, history_window: int = 100):
        self.history_window = history_window
        self.events: List[EventToken] = []
        
        # Sliding windows for live signals
        self.recent_alloc_stalls: Deque[int] = deque(maxlen=history_window)
        self.recent_bank_conflicts: Deque[int] = deque(maxlen=history_window)
        
        # State tracking
        self.memory_utilization: float = 0.0
        self.active_requests_count: int = 0

    def publish(self, token: EventToken) -> None:
        self.events.append(token)

        # Update sliding window indicators
        if token.event_type == EventType.ALLOCATION_STALL:
            self.recent_alloc_stalls.append(1)
        elif token.event_type == EventType.SRAM_BANK_CONFLICT:
            self.recent_bank_conflicts.append(1)

    def log(self, cycle: int, event_type: EventType, src_id: int, p1: int = 0, p2: int = 0) -> None:
        tok = EventToken(cycle, event_type, src_id, p1, p2)
        self.publish(tok)

    def ingest_hardware_binary(self, raw_bytes: bytes) -> int:
        """Parses batch of 16-byte tokens emitted by the C++ hardware engine."""
        token_size = 16
        num_tokens = len(raw_bytes) // token_size
        for i in range(num_tokens):
            chunk = raw_bytes[i * token_size : (i + 1) * token_size]
            token = EventToken.unpack(chunk)
            self.publish(token)
        return num_tokens

    def update_memory_state(self, utilization: float, active_count: int) -> None:
        self.memory_utilization = utilization
        self.active_requests_count = active_count

    # Feedback signals for closed-loop control
    def is_memory_congested(self) -> bool:
        return self.memory_utilization >= 0.75 or len(self.recent_alloc_stalls) >= 3

    def is_hardware_bottlenecked(self) -> bool:
        return len(self.recent_bank_conflicts) >= 5

    def get_summary(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for ev in self.events:
            name = ev.event_type.name
            counts[name] = counts.get(name, 0) + 1

        return {
            "total_events_logged": len(self.events),
            "memory_utilization_current": f"{round(self.memory_utilization * 100, 1)}%",
            "memory_congested_signal": self.is_memory_congested(),
            "hardware_bottleneck_signal": self.is_hardware_bottlenecked(),
            "event_breakdown": counts
        }