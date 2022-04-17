from dataclasses import dataclass
from typing import Literal, Sequence

Mark = Literal[1, 2]
Action = int


@dataclass
class Observation:
    board: Sequence[Literal[0, 1, 2]]  # 0: empty, 1: you, 2: opponent
    mark: Mark
    remainingOverageTime: int
    step: int


@dataclass
class Config:
    columns: int
    rows: int
    inarow: int
