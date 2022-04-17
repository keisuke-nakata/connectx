import random

import numpy as np

from connectx.tutorial.connectx_game import Observation, Config, Mark, generate_windows


def drop_piece(grid: np.ndarray, col: int, mark: Mark, rows: int) -> np.ndarray:
    """
    gird に対して col の手 (必ず valid なものが渡される) を打った時の盤面を返す
    """
    for rev_row in range(rows):
        if grid[rows - rev_row - 1, col] == 0:
            break
    next_grid = grid.copy()
    next_grid[rows - rev_row - 1, col] = mark
    return next_grid


def _score_window(window: np.ndarray, mark: Mark, inarow: int) -> float:
    score = 0.0
    if (window == mark).sum() == inarow:
        score += 1_000_000
    elif (window == 0).sum() == 1:
        for color in (1, 2):
            if (window == color).sum() == inarow - 1:
                if color == mark:
                    score += 1
                else:
                    score += -100
    return score


def score_grid(grid: np.ndarray, mark: Mark, inarow: int) -> float:
    score = 0.0
    for window in generate_windows(grid, inarow):
        score += _score_window(window, mark, inarow)
    return score


def score_move(grid: np.ndarray, col: int, mark: Mark, config: Config) -> float:
    """
    gird に対して col の手 (必ず valid なものが渡される) を打った時の得点
    - 自分の勝利1列で 1_000_000 点
    - 自分のリーチ1列で 1 点
    - 相手のリーチ1列で -100 点
    """
    next_grid = drop_piece(grid, col, mark, config.rows)
    return score_grid(next_grid, mark, config.inarow)


def agent(obs: Observation, config: Config) -> int:
    # Get list of valid moves
    valid_moves = [c for c in range(config.columns) if obs.board[c] == 0]
    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Use the heuristic to assign a score to each possible board in the next turn
    scores = dict(zip(valid_moves, [score_move(grid, col, obs.mark, config) for col in valid_moves]))
    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    # Select at random from the maximizing columns
    return random.choice(max_cols)
