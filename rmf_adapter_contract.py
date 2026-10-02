"""Offline contract checks for fleet-adapter event traces."""

import argparse
import json
from pathlib import Path
import sys


MESSAGES = {
    "fr": {
        "order": "Horodatages non ordonnés à la ligne {line}",
        "transition": "Transition {event} invalide pour la tâche {task}",
        "offline": "Tâche {task} active quand le robot {robot} se déconnecte",
        "incomplete": "Tâche {task} sans état final",
        "heartbeat": "Plus de {limit} ms sans battement pour {robot}",
        "input": "Trace invalide : {detail}",
        "summary": "{count} anomalie(s) dans {events} événement(s)",
    },
    "en": {
        "order": "Timestamps are out of order at line {line}",
        "transition": "Invalid {event} transition for task {task}",
        "offline": "Task {task} was active when robot {robot} disconnected",
        "incomplete": "Task {task} has no terminal state",
        "heartbeat": "More than {limit} ms without a heartbeat from {robot}",
        "input": "Invalid trace: {detail}",
        "summary": "{count} finding(s) in {events} event(s)",
    },
    "es": {
        "order": "Marcas de tiempo desordenadas en la línea {line}",
        "transition": "Transición {event} no válida para la tarea {task}",
        "offline": "La tarea {task} seguía activa al desconectarse el robot {robot}",
        "incomplete": "La tarea {task} no tiene estado final",
        "heartbeat": "Más de {limit} ms sin señal del robot {robot}",
        "input": "Registro no válido: {detail}",
        "summary": "{count} anomalía(s) en {events} evento(s)",
    },
}

TRANSITIONS = {
    None: {"task_requested": "requested"},
    "requested": {"task_assigned": "assigned", "task_cancelled": "cancelled"},
    "assigned": {"task_started": "started", "task_cancelled": "cancelled"},
    "started": {"task_completed": "completed", "task_cancelled": "cancelled"},
    "completed": {},
    "cancelled": {},
}
ROBOT_EVENTS = {"robot_online", "robot_offline", "heartbeat"}


def check(events, max_heartbeat_gap_ms=5000, locale="en"):
    if locale not in MESSAGES or max_heartbeat_gap_ms <= 0:
        raise ValueError("unsupported locale or heartbeat limit")
    findings = []
    tasks = {}
    robots = {}

    def add(code, **details):
        findings.append({"code": code, "details": details, "message": MESSAGES[locale][code].format(**details)})

    previous = None
    for line, event in enumerate(events, 1):
        if not isinstance(event, dict) or not isinstance(event.get("at_ms"), int) or isinstance(event.get("at_ms"), bool):
            raise ValueError(f"line {line}: at_ms must be an integer")
        kind = event.get("event")
        if kind not in ROBOT_EVENTS and kind not in {"task_requested", "task_assigned", "task_started", "task_completed", "task_cancelled"}:
            raise ValueError(f"line {line}: unknown event")
        stamp = event["at_ms"]
        if previous is not None and stamp < previous:
            add("order", line=line)
        previous = stamp
        if kind in ROBOT_EVENTS:
            robot = event.get("robot")
            if not isinstance(robot, str) or not robot:
                raise ValueError(f"line {line}: robot is required")
            state = robots.setdefault(robot, {"online": False, "last_heartbeat": None})
            if kind == "robot_online":
                state.update(online=True, last_heartbeat=stamp)
            elif kind == "heartbeat":
                if not state["online"]:
                    add("heartbeat", robot=robot, limit=max_heartbeat_gap_ms)
                elif stamp - state["last_heartbeat"] > max_heartbeat_gap_ms:
                    add("heartbeat", robot=robot, limit=max_heartbeat_gap_ms)
                state["last_heartbeat"] = stamp
            else:
                for task, value in tasks.items():
                    if value["robot"] == robot and value["state"] in {"assigned", "started"}:
                        add("offline", robot=robot, task=task)
                state["online"] = False
            continue
        task = event.get("task")
        if not isinstance(task, str) or not task:
            raise ValueError(f"line {line}: task is required")
        state = tasks.setdefault(task, {"state": None, "robot": None})
        next_state = TRANSITIONS[state["state"]].get(kind)
        if next_state is None:
            add("transition", task=task, event=kind)
            continue
        if kind == "task_assigned":
            robot = event.get("robot")
            if not isinstance(robot, str) or not robot:
                raise ValueError(f"line {line}: assigned robot is required")
            if not robots.get(robot, {}).get("online"):
                add("offline", robot=robot, task=task)
            state["robot"] = robot
        elif kind in {"task_started", "task_completed"} and event.get("robot") != state["robot"]:
            add("transition", task=task, event=kind)
            continue
        state["state"] = next_state
    for task, value in tasks.items():
        if value["state"] not in {"completed", "cancelled"}:
            add("incomplete", task=task)
    return {
        "format": "rmf-adapter-contract/v1",
        "locale": locale,
        "status": "pass" if not findings else "fail",
        "summary": MESSAGES[locale]["summary"].format(count=len(findings), events=len(events)),
        "tasks": tasks,
        "findings": findings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a fleet-adapter event trace / Vérifier une trace de flotte / Verificar un registro de flota")
    parser.add_argument("trace")
    parser.add_argument("--locale", choices=MESSAGES, default="en")
    parser.add_argument("--max-heartbeat-gap-ms", type=int, default=5000)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        events = [json.loads(line) for line in Path(args.trace).read_text(encoding="utf-8").splitlines() if line.strip()]
        report = check(events, args.max_heartbeat_gap_ms, args.locale)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(MESSAGES[args.locale]["input"].format(detail=exc), file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
