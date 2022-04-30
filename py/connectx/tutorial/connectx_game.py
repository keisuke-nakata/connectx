from collections.abc import Sequence, Iterable, Callable
from typing import Any, Literal, Mapping
import dataclasses
import itertools
import uuid

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from connectx.tutorial import minimax


Mark = Literal[1, 2]  # 1: player, 2: opponent


@dataclasses.dataclass
class Observation:
    board: Sequence[Literal[0, 1, 2]]  # 0: empty, 1: player, 2: opponent
    mark: Mark
    remainingOverageTime: int
    step: int


@dataclasses.dataclass
class Config:
    columns: int
    rows: int
    inarow: int


class ConnectXAction(minimax.Action):
    col: int

    def __init__(self, col: int, turn: minimax.Turn) -> None:
        self.col = col
        self._turn = turn

        self._id = str(uuid.uuid1())

    @property
    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        return f"col={self.col}"

    @property
    def turn(self) -> minimax.Turn:
        return self._turn

    @property
    def property_(self) -> Mapping[str, Any]:
        return {}

    ###
    # user-defined properties
    ###

    def __hash__(self) -> int:
        return self.col

    def __repr__(self) -> str:
        return f"ConnectXAction<col={self.col}>"


class ConnectXState(minimax.State):
    def __init__(self, grid: np.ndarray, next_player: Mark, step: int) -> None:
        self.grid = grid
        self.next_player = next_player
        self.step = step

        self._id = str(uuid.uuid1())

    @property
    def next_turn(self) -> minimax.Turn:
        if self.next_player == 1:
            return minimax.Turn.PLAYER
        else:
            return minimax.Turn.OPPONENT

    @property
    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        return "\n".join("".join(str(x) for x in row) for row in self.grid.tolist())

    @property
    def property_(self) -> Mapping[str, Any]:
        return {}


class ConnectXGame(minimax.Game[ConnectXState, ConnectXAction]):
    def __init__(self, columns: int, rows: int, inarow: int) -> None:
        self.columns = columns
        self.rows = rows
        self.inarow = inarow

    def get_terminal_score(self, state: ConnectXState) -> tuple[bool, float]:
        """
        state が最終状態 (それ以上手がない) であれば (True, terminal_score) を返す。
        そうでない場合、(False, nan) を返す。
        """
        for window in generate_windows(state.grid, self.inarow):
            if (window == 1).sum() == self.inarow:
                return (True, 1_000_000)
            elif (window == 2).sum() == self.inarow:
                return (True, -10_000)
        if len(self.get_available_actions(state)) == 0:
            return (True, 0)
        return (False, float("nan"))

    def get_available_actions(self, state: ConnectXState) -> Sequence[ConnectXAction]:
        return [ConnectXAction(c, state.next_turn) for c in range(self.columns) if state.grid[0][c] == 0]

    def step(self, state: ConnectXState, action: ConnectXAction) -> ConnectXState:
        for row in reversed(range(self.rows)):
            if state.grid[row, action.col] == 0:
                break
        else:
            raise RuntimeError("Invalid action")

        next_grid = state.grid.copy()
        next_grid[row, action.col] = state.next_player
        next_player: Literal[1, 2] = 1 if state.next_player == 2 else 2
        return ConnectXState(next_grid, next_player, state.step + 1)


def generate_horizontal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    return itertools.chain.from_iterable(sliding_window_view(row, inarow) for row in grid)


def generate_vertical_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    return itertools.chain.from_iterable(sliding_window_view(col, inarow) for col in grid.T)


def generate_positive_diagonal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    nrow, ncol = grid.shape
    diags = (grid.diagonal(diag_idx) for diag_idx in range(-nrow + 1, ncol))
    return itertools.chain.from_iterable(sliding_window_view(diag, inarow) for diag in diags if len(diag) >= inarow)


def generate_negative_diagonal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    grid_flipped = np.fliplr(grid)
    nrow, ncol = grid_flipped.shape
    diags = (grid_flipped.diagonal(diag_idx) for diag_idx in range(-nrow + 1, ncol))
    return itertools.chain.from_iterable(sliding_window_view(diag, inarow) for diag in diags if len(diag) >= inarow)


def generate_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    fns: Iterable[Callable] = (
        generate_horizontal_windows,
        generate_vertical_windows,
        generate_positive_diagonal_windows,
        generate_negative_diagonal_windows,
    )
    return itertools.chain.from_iterable(fn(grid, inarow) for fn in fns)
