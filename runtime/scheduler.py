from typing import List, Optional
from runtime.request import Request

class Scheduler:
    def __init__(self):
        self.waiting_queue: List[Request] = []

    def add_request(self, request: Request):
        self.waiting_queue.append(request)

    # continuous batching
    def form_batch(self, current_time: int, max_batch_size: int, current_active_count: int, prioritize_urgent: bool = False, broker=None) -> List[Request]:
        if not self.waiting_queue:
            return []

        available_slots = max_batch_size - current_active_count
        if available_slots <= 0:
            return []
        original_front = self.waiting_queue[0].request_id

        if prioritize_urgent: # closed loop: earlier deadlines first
            self.waiting_queue.sort(key=lambda req: req.get_urgency_score(current_time), reverse=True)
            new_front = self.waiting_queue[0].request_id
            if broker and new_front != original_front:
                broker.log_trace(current_time, f"BATCH INJECTION: Req {new_front} prioritized into active batch over Req {original_front}")
        else: # baseline: First Come First Serve
            self.waiting_queue.sort(key=lambda req: req.arrival_time)

        # pull requests up to available slots
        new_batch_members = []
        while self.waiting_queue and len(new_batch_members) < available_slots:
            new_batch_members.append(self.waiting_queue.pop(0))
        return new_batch_members

    def requeue_front(self, request: Request):
        self.waiting_queue.insert(0, request)

    def has_waiting_requests(self) -> bool:
        return len(self.waiting_queue) > 0