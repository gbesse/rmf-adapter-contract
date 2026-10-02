"""Small instrumentation sink for fleet-adapter integration."""

import json
from pathlib import Path
import time


class TraceSink:
    def __init__(self, path):
        self.path = Path(path)
        self.start_ns = time.monotonic_ns()

    def emit(self, event, *, robot=None, task=None, at_ms=None):
        record = {"at_ms": at_ms if at_ms is not None else (time.monotonic_ns() - self.start_ns) // 1_000_000, "event": event}
        if robot is not None:
            record["robot"] = robot
        if task is not None:
            record["task"] = task
        with self.path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(record, separators=(",", ":")) + "\n")
        return record
