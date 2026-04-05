# CLAUDE.md

## Project Overview

This repository contains a **Pygame-based particle physics simulation** (`物理模拟.py`) that renders fluid-like particle dynamics inside a rotating flask container.

> **Note:** The README.md describes an unimplemented "Codex" LLM inference service. That project does not exist in the codebase — only the physics simulation is implemented.

## Repository Structure

```
first-day/
├── README.md          # (Describes unimplemented Codex project)
├── 物理模拟.py         # Physics simulation — the actual project
└── CLAUDE.md          # This file
```

## The Physics Simulation

`物理模拟.py` is a single-file (~189 lines) Pygame application with three classes:

- **`Particle`** — Individual particle with position, velocity, acceleration. Handles gravity, inter-particle repulsion, Euler integration, and bounding-box collision.
- **`Flask`** — A rotating rectangular container that slowly tilts to a target angle (135 degrees).
- **`Simulation`** — Orchestrator that manages ~150 particles and the flask, running the game loop at 60 FPS.

## Dependencies

- **Python 3.10+**
- **pygame** — sole external dependency

## Running

```bash
pip install pygame
python 物理模拟.py
```

## Code Conventions

- Python with type hints (`typing.List`, `typing.Tuple`, `pygame.math.Vector2`)
- Docstrings on all public methods
- Physics uses simple Euler integration with damping
- No test suite, no linter/formatter configuration, no CI/CD
- Single-file architecture — no packages or modules

## Key Constants (in `Simulation.__init__`)

| Parameter              | Value  | Purpose                        |
|------------------------|--------|--------------------------------|
| `gravity`              | 0.5    | Downward acceleration per tick |
| `damping`              | 0.99   | Velocity decay factor          |
| `restitution`          | 0.7    | Bounciness on wall collision   |
| `repulsion_strength`   | 0.05   | Inter-particle push force      |
| `repulsion_threshold`  | 1.2    | Distance multiplier for repulsion |
| `floor_y`              | 580    | Screen-space floor boundary    |

## Guidelines for AI Assistants

- The filename uses Chinese characters (`物理模拟` = "Physics Simulation"). Handle encoding carefully.
- There is no build system, test framework, or linting configured. If adding these, use standard Python tooling (`pytest`, `ruff` or `flake8`, `pyproject.toml`).
- The README does not reflect the actual codebase. Do not assume any code from the README exists.
- When modifying physics parameters, test visually — there are no automated tests.
