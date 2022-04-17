from typing import Literal
import random

import numpy as np

from connectx.tutorial.connectx_game import Observation, Config, ConnectXAction, ConnectXState, ConnectXGame, generate_windows, Mark
from connectx.tutorial.minimax import argminimax, Scorer


class ConnectXScorer(Scorer[ConnectXState]):
    def __init__(self, inarow: int) -> None:
        self.inarow = inarow

    def __call__(self, state: ConnectXState) -> float:
        def _score_window(window: np.ndarray, mark: Mark, inarow: int) -> float:
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

        def score_grid(grid: np.ndarray, mark: Mark, inarow: int) -> float:
            score = 0.0
            for window in generate_windows(grid, inarow):
                score += _score_window(window, mark, inarow)
            return score

        mark: Literal[1, 2] = 2 if state.is_opponent_turn else 1
        return score_grid(state.grid, mark, self.inarow)


def agent(obs: Observation, config: Config) -> int:
    game = ConnectXGame(config)
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    state = ConnectXState(grid, next_player=1)
    scores, actions = argminimax(game, 3, state, ConnectXScorer(config.inarow))
    print(scores, actions)
    shuf = list(range(len(scores)))
    random.shuffle(shuf)
    scores = [scores[s] for s in shuf]
    actions = [actions[s] for s in shuf]
    return actions[np.argmax(scores)].col
