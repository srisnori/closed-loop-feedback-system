class Telemetry:
    def __init__(self, allocator, enabled=True):
        self.allocator = allocator
        self.enabled = enabled
        self.event_log = []

    def log_event(self, event_name, data, cycle):
        if not self.enabled:
            return
        entry = {"cycle": cycle, "event": event_name, "data": data}
        self.event_log.append(entry)

    def get_memory_pressure(self):
        if not self.enabled:
            return "LOW"
        return self.allocator.memory_status()["pressure"]

    def get_memory_state(self):
        if not self.enabled:
            return None
        return self.allocator.memory_status()