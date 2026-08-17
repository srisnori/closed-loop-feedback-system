from typing import List, Optional
from runtime.request import Request

class Scheduler:
    def __init__(self):
        self.waiting_queue: List[Request] = []

    def add_request(self, request: Request):
        self.waiting_queue.append(request)

    def schedule(self, current_time: int, prioritize_urgent: bool = False) -> Optional[Request]:
        if not self.waiting_queue:
            return None

        if prioritize_urgent:
            # closed loop feedback true: prioritize requests closest to SLO deadline
            self.waiting_queue.sort(
                key=lambda req: req.get_urgency_score(current_time),
                reverse=True
            )
        else:
            # baseline open loop: standard first come first serve (FCFS)
            self.waiting_queue.sort(key=lambda req: req.arrival_time)

        return self.waiting_queue.pop(0)

    def requeue_front(self, request: Request):
        self.waiting_queue.insert(0, request)

    def has_waiting_requests(self) -> bool:
        return len(self.waiting_queue) > 0