# runtime/tracer.py
import time

class Tracer:
    def __init__(self):
        self.events = []

    def log(self, event, data=None):
        self.events.append({
            "event": event,
            "data": data,
            "ts": time.time()
        })

    def dump(self):
        return self.events