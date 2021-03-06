import numpy as np

from connectx.gamesolver import minimax, gametree
from connectx.tutorial import connectx_game


def mark_playable_grid(grid: np.ndarray) -> np.ndarray:
    """-1: empty (playable), 0: empty (un-playable), 1: player, 2: opponent"""
    playable_grid = grid.copy()
    for col in range(playable_grid.shape[1]):
        try:
            row = connectx_game.get_playable_row(playable_grid[:, col])
        except RuntimeError:
            continue
        playable_grid[row, col] = -1
    return playable_grid


class ConnectXScorer(gametree.Scorer[connectx_game.ConnectXState]):
    def __init__(self, inarow: int) -> None:
        self.inarow = inarow

    def __call__(self, state: connectx_game.ConnectXState) -> float:
        def _score_window(window: np.ndarray, inarow: int) -> float:
            if (window == 1).sum() == inarow:
                return 1_000_000
            if (window == 2).sum() == inarow:
                return -10_000

            score = 0.0
            if (window == -1).sum() == 1 and (window == 0).sum() == 0:  # 4列の中にこのターンで石を置ける場所が残り1つ
                for color in (1, 2):
                    if (window == color).sum() == inarow - 1:
                        if color == 1:
                            score += 1
                        else:
                            score += -100
            return score

        def score_grid(grid: np.ndarray, inarow: int) -> float:
            score = 0.0
            playable_grid = mark_playable_grid(grid)
            for window in connectx_game.generate_windows(playable_grid, inarow):
                score += _score_window(window, inarow)
            return score

        return score_grid(state.grid, self.inarow)


class ConnectXMinimax(
    minimax.Minimax[
        connectx_game.ConnectXState,
        connectx_game.ConnectXResult,
        connectx_game.ConnectXAction,
        ConnectXScorer,
    ]
):
    pass


# class ConnectXMCTS(mcts.MCTS[connectx_game.ConnectXState, connectx_game.ConnectXAction]):
#     pass
