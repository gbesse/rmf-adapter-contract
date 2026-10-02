import unittest
from pathlib import Path
import tempfile
from rmf_adapter_contract import check
from trace_sink import TraceSink


class ContractTests(unittest.TestCase):
    def test_healthy(self):
        events = [
            {"at_ms": 0, "event": "robot_online", "robot": "r1"},
            {"at_ms": 1, "event": "task_requested", "task": "t"},
            {"at_ms": 2, "event": "task_assigned", "task": "t", "robot": "r1"},
            {"at_ms": 3, "event": "task_started", "task": "t", "robot": "r1"},
            {"at_ms": 4, "event": "task_completed", "task": "t", "robot": "r1"},
        ]
        for locale in ("fr", "en", "es"):
            self.assertEqual(check(events, locale=locale)["status"], "pass")

    def test_disconnect_during_task(self):
        events = [
            {"at_ms": 0, "event": "robot_online", "robot": "r1"},
            {"at_ms": 1, "event": "task_requested", "task": "t"},
            {"at_ms": 2, "event": "task_assigned", "task": "t", "robot": "r1"},
            {"at_ms": 3, "event": "robot_offline", "robot": "r1"},
        ]
        report = check(events)
        self.assertEqual(report["status"], "fail")
        self.assertEqual({item["code"] for item in report["findings"]}, {"offline", "incomplete"})

    def test_trace_sink(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            sink = TraceSink(path)
            sink.emit("robot_online", robot="r1", at_ms=0)
            self.assertIn('"robot":"r1"', path.read_text())


if __name__ == "__main__":
    unittest.main()
