import numpy as np

from connectx.tutorial import connectx_game, minimax


class ConnectXScorer(minimax.Scorer[connectx_game.ConnectXState]):
    def __init__(self, inarow: int) -> None:
        self.inarow = inarow

    def __call__(self, state: connectx_game.ConnectXState) -> float:
        def _score_window(window: np.ndarray, mark: connectx_game.Mark, inarow: int) -> float:
            score = 0.0
            if (window == mark).sum() == inarow:
                score += 1_000_000
            opponent = 1 if mark == 2 else 2
            if (window == opponent).sum() == inarow:
                score += -10_000
            elif (window == 0).sum() == 1:
                for color in (1, 2):
                    if (window == color).sum() == inarow - 1:
                        if color == mark:
                            score += 1
                        else:
                            score += -100
            return score

        def score_grid(grid: np.ndarray, mark: connectx_game.Mark, inarow: int) -> float:
            score = 0.0
            for window in connectx_game.generate_windows(grid, inarow):
                score += _score_window(window, mark, inarow)
            return score

        return score_grid(state.grid, state.next_player, self.inarow)


class ConnectXMinimax(
    minimax.Minimax[
        connectx_game.ConnectXGame,
        connectx_game.ConnectXState,
        connectx_game.ConnectXAction,
        ConnectXScorer,
    ]
):
    pass
