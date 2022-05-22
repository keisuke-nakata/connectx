from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Callable, Optional

import dataclasses
import itertools

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from typing_extensions import Literal

from connectx.gamesolver import game

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


class ConnectXState(game.State):
    def __init__(self, grid: np.ndarray, next_player: Mark, step: int) -> None:
        self.grid = grid
        self.next_player = next_player
        self.step = step

    @property
    def next_turn(self) -> game.Turn:
        if self.next_player == 1:
            return game.Turn.PLAYER
        else:
            return game.Turn.OPPONENT

    def __str__(self) -> str:
        return "\n".join("".join(str(x) for x in row) for row in self.grid.tolist())


class ConnectXResult(game.Result):
    def __init__(self, winner: Optional[game.Turn]) -> None:
        self._winner = winner

    @property
    def winner(self) -> Optional[game.Turn]:
        return self._winner


class ConnectXAction(game.Action):
    col: int

    def __init__(self, col: int, turn: game.Turn) -> None:
        self.col = col
        self._turn = turn

    def __str__(self) -> str:
        return f"col={self.col}"

    @property
    def turn(self) -> game.Turn:
        return self._turn

    ###
    # user-defined properties
    ###

    def __hash__(self) -> int:
        return self.col

    def __repr__(self) -> str:
        return f"ConnectXAction<col={self.col}>"


class ConnectXGame(game.Game[ConnectXState, ConnectXResult, ConnectXAction]):
    def __init__(self, columns: int, rows: int, inarow: int) -> None:
        self.columns = columns
        self.rows = rows
        self.inarow = inarow

    def get_result(self, state: ConnectXState) -> Optional[ConnectXResult]:
        """
        state が最終状態 (それ以上手がない) であれば Result を返す。
        そうでない場合、None を返す。
        """
        for window in generate_windows(state.grid, self.inarow):
            if (window == 1).sum() == self.inarow:
                return ConnectXResult(winner=game.Turn.PLAYER)
            elif (window == 2).sum() == self.inarow:
                return ConnectXResult(winner=game.Turn.OPPONENT)
        if len(self.get_available_actions(state)) == 0:  # draw
            return ConnectXResult(winner=None)
        return None

    def get_available_actions(self, state: ConnectXState) -> list[ConnectXAction]:
        return [ConnectXAction(c, state.next_turn) for c in range(self.columns) if state.grid[0][c] == 0]

    def step(self, state: ConnectXState, action: ConnectXAction) -> ConnectXState:
        row = get_playable_row(state.grid[:, action.col])

        next_grid = state.grid.copy()
        next_grid[row, action.col] = state.next_player
        next_player: Literal[1, 2] = 1 if state.next_player == 2 else 2
        return ConnectXState(next_grid, next_player, state.step + 1)


def get_playable_row(col: np.ndarray) -> int:
    for row in reversed(range(len(col))):
        if col[row] == 0:
            break
    else:
        raise RuntimeError("Not playable")
    return row


def generate_horizontal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    return itertools.chain.from_iterable(sliding_window_view(row, inarow) for row in grid)  # type: ignore


def generate_vertical_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    return itertools.chain.from_iterable(sliding_window_view(col, inarow) for col in grid.T)  # type: ignore


def generate_positive_diagonal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    nrow, ncol = grid.shape
    diags = (grid.diagonal(diag_idx) for diag_idx in range(-nrow + 1, ncol))
    return itertools.chain.from_iterable(
        sliding_window_view(diag, inarow) for diag in diags if len(diag) >= inarow  # type: ignore
    )


def generate_negative_diagonal_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    grid_flipped = np.fliplr(grid)  # type: ignore
    nrow, ncol = grid_flipped.shape
    diags = (grid_flipped.diagonal(diag_idx) for diag_idx in range(-nrow + 1, ncol))
    return itertools.chain.from_iterable(
        sliding_window_view(diag, inarow) for diag in diags if len(diag) >= inarow  # type: ignore
    )


def generate_windows(grid: np.ndarray, inarow: int) -> Iterable[np.ndarray]:
    fns: Iterable[Callable] = (
        generate_horizontal_windows,
        generate_vertical_windows,
        generate_positive_diagonal_windows,
        generate_negative_diagonal_windows,
    )
    return itertools.chain.from_iterable(fn(grid, inarow) for fn in fns)
