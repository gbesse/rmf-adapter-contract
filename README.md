# RMF Adapter Contract

## Français

Alpha locale pour vérifier une **trace d’événements d’adaptateur de flotte**. Elle contrôle l’ordre des horodatages, les transitions des tâches, la déconnexion pendant une tâche et les retards entre battements. Les scénarios synthétiques passent sans installation de ROS.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/rmf-adapter-contract fixtures/healthy.jsonl --locale=fr
.venv/bin/rmf-adapter-contract fixtures/disconnect.jsonl --locale=fr
```

Chaque ligne JSON contient `at_ms` et `event`. Les événements de robot utilisent `robot` ; ceux des tâches utilisent `task`, et les événements assignés utilisent aussi `robot`. Les noms reconnus figurent dans les exemples. Instrumenter votre adaptateur pour émettre cette trace sans modifier ses décisions. L’outil ne se connecte pas à Open-RMF, ne simule pas sa planification et ne prouve pas l’absence de collision. Le code de sortie est 0 pour une trace conforme, 1 pour une anomalie et 2 pour une entrée invalide.

`TraceSink("trace.jsonl").emit("robot_online", robot="r1")` fournit un point d’instrumentation minimal. Émettre les événements depuis les callbacks réels de l’adaptateur et conserver la trace localement.

## English

Local alpha for checking a **fleet-adapter event trace**. It checks timestamp order, task transitions, disconnects during tasks and heartbeat gaps. Synthetic scenarios run without ROS.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/rmf-adapter-contract fixtures/healthy.jsonl --locale=en
.venv/bin/rmf-adapter-contract fixtures/disconnect.jsonl --locale=en
```

Each JSON line has `at_ms` and `event`. Robot events use `robot`; task events use `task`, and assigned events also use `robot`. The examples show recognized names. Instrument your adapter to emit the trace without changing its decisions. The tool does not connect to Open-RMF, simulate its planner or prove collision freedom. Exit code 0 means compliant trace, 1 means a finding, and 2 means invalid input.

`TraceSink("trace.jsonl").emit("robot_online", robot="r1")` is a minimal instrumentation point. Emit events from real adapter callbacks and keep the trace local.

## Español

Alfa local para verificar un **registro de eventos de un adaptador de flota**. Comprueba el orden temporal, las transiciones de tareas, las desconexiones durante tareas y los intervalos entre señales. Los escenarios sintéticos se ejecutan sin ROS.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/rmf-adapter-contract fixtures/healthy.jsonl --locale=es
.venv/bin/rmf-adapter-contract fixtures/disconnect.jsonl --locale=es
```

Cada línea JSON contiene `at_ms` y `event`. Los eventos de robot usan `robot`; los de tarea usan `task`, y los eventos asignados también usan `robot`. Los ejemplos muestran los nombres admitidos. Instrumenta el adaptador para emitir este registro sin cambiar sus decisiones. La herramienta no se conecta a Open-RMF, no simula su planificador ni demuestra la ausencia de colisiones. El código de salida 0 indica conformidad, 1 una anomalía y 2 una entrada no válida.

`TraceSink("trace.jsonl").emit("robot_online", robot="r1")` ofrece un punto mínimo de instrumentación. Emite eventos desde los callbacks reales del adaptador y conserva el registro localmente.

MIT — [LICENSE](LICENSE).
