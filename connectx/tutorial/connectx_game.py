from collections.abc import Sequence, Iterable, Callable
from typing import Literal
from dataclasses import dataclass
import itertools

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from connectx.tutorial.minimax import Action, State, Game


Mark = Literal[1, 2]  # 1: player, 2: opponent


@dataclass
class Observation:
    board: Sequence[Literal[0, 1, 2]]  # 0: empty, 1: player, 2: opponent
    mark: Mark
    remainingOverageTime: int
    step: int


@dataclass
class Config:
    columns: int
    rows: int
    inarow: int


class ConnectXAction(Action):
    col: int

    def __init__(self, col: int) -> None:
        self.col = col

    def __hash__(self) -> int:
        return self.col

    def __str__(self) -> str:
        return f"ConnectXAction<col={self.col}>"

    def __repr__(self) -> str:
        return str(self)


class ConnectXState(State):
    def __init__(self, grid: np.ndarray, next_player: Mark) -> None:
        self.grid = grid
        self.next_player = next_player

    @property
    def is_opponent_turn(self) -> bool:
        return self.next_player == 2


class ConnectXGame(Game[ConnectXState, ConnectXAction]):
    def __init__(self, config: Config) -> None:
        self.config = config

    def get_terminal_score(self, state: ConnectXState) -> tuple[bool, float]:
        """
        state が最終状態 (それ以上手がない) であれば (True, score) を返す。
        そうでない場合、(False, nan) を返す。
        """
        for window in generate_windows(state.grid, self.config.inarow):
            if (window == 1).sum() == self.config.inarow:
                return (True, 1_000_000)
            elif (window == 2).sum() == self.config.inarow:
                return (True, -10_000)
        if len(self.get_available_actions(state)) == 0:
            return (True, 0)
        return (False, float("nan"))

    def get_available_actions(self, state: ConnectXState) -> Sequence[ConnectXAction]:
        return [ConnectXAction(c) for c in range(self.config.columns) if state.grid[0][c] == 0]

    def step(self, state: ConnectXState, action: ConnectXAction) -> ConnectXState:
        for rev_row in range(self.config.rows):
            if state.grid[self.config.rows - rev_row - 1, action.col] == 0:
                break
        else:
            raise RuntimeError("Invalid action")

        next_grid = state.grid.copy()
        next_grid[self.config.rows - rev_row - 1, action.col] = state.next_player
        next_player: Literal[1, 2] = 1 if state.next_player == 2 else 2
        return ConnectXState(next_grid, next_player)


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
