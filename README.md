# Tsuro AI

A Python implementation of the board game [Tsuro](https://en.wikipedia.org/wiki/Tsuro) with support for human and AI players.

## Requirements

- Python 3.10+
- pygame

## Installation

1. Clone or download the repository.
2. Install the required dependency:

```bash
pip install pygame
```

## Running the Game

```bash
python main.py
```

## How to Play (Human Player)

When it is your turn, your hand of tiles is shown at the bottom of the screen.

Rotate a tile by right-clicking on it. Place it with a left-click.

## Changing Players

Open [main.py](main.py) and edit the `players` list. There are three player types available:

| Player type | Description |
|---|---|
| `UIPlayer(ui)` | Human player — uses the graphical interface |
| `MCTSPlayer(t)` | AI using Monte Carlo Tree Search, where `t` is the time limit in seconds |
| `RandomPlayer()` | AI that picks moves at random |

**Example: two humans**
```python
players = [
    UIPlayer(ui),
    UIPlayer(ui),
]
```

**Example: human vs stronger AI**
```python
players = [
    UIPlayer(ui),
    MCTSPlayer(3),  # 3 seconds to think per move
]
```

**Example: AI vs AI**
```python
players = [
    MCTSPlayer(1),
    RandomPlayer(),
]
```

The game supports 2–8 players. Simply add or remove entries from the list.
