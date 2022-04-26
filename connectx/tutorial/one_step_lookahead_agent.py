import random

import numpy as np

from connectx.tutorial import connectx_game
from connectx.tutorial import connectx_minimax


def agent(obs: connectx_game.Observation, config: connectx_game.Config) -> int:
    game = connectx_game.ConnectXGame(config.columns, config.rows, config.inarow)
    minimax = connectx_minimax.ConnectXMinimax(game)
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    state = connectx_game.ConnectXState(grid, next_player=1)
    scores, actions = minimax.argminimax(1, state, connectx_minimax.ConnectXScorer(config.inarow))
    shuf = list(range(len(scores)))
    random.shuffle(shuf)
    scores = [scores[s] for s in shuf]
    actions = [actions[s] for s in shuf]
    return actions[np.argmax(scores)].col
