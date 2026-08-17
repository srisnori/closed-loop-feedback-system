from enum import Enum
from dataclasses import dataclass, field
from typing import List

class RequestState(Enum):
    WAITING   = "WAITING"
    RUNNING   = "RUNNING"
    COMPLETED = "COMPLETED"

@dataclass
class Request:
    request_id: int
    arrival_time: int
    prompt_tokens: int
    output_tokens: int
    slo_deadline: int
    kv_blocks: int
    
    # execution state
    remaining_tokens: int = field(init=False)
    allocated_block_ids: List[int] = field(default_factory=list)
    state: RequestState = RequestState.WAITING
    start_cycle: int = -1
    finish_cycle: int = -1

    def __post_init__(self):
        self.remaining_tokens = self.output_tokens

    def start_request(self, current_cycle: int):
        self.state = RequestState.RUNNING
        self.start_cycle = current_cycle

    def advance_request(self, current_cycle: int) -> bool:
        self.remaining_tokens -= 1
        if self.remaining_tokens <= 0:
            self.state = RequestState.COMPLETED
            self.finish_cycle = current_cycle
            return True
        return False

    def get_urgency_score(self, current_time: int) -> float: # deadlines checker
        slack = (self.slo_deadline - current_time) - self.remaining_tokens
        return -slack