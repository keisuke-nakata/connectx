import random

import numpy as np

from connectx.tutorial.connectx_game import Observation, Config, ConnectXState, ConnectXGame
from connectx.tutorial.connectx_minimax import ConnectXMinimax, ConnectXScorer


def agent(obs: Observation, config: Config) -> int:
    game = ConnectXGame(config)
    minimax = ConnectXMinimax(game)
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    state = ConnectXState(grid, next_player=1)
    scores, actions = minimax.argminimax(3, state, ConnectXScorer(config.inarow))
    print(scores, actions)
    shuf = list(range(len(scores)))
    random.shuffle(shuf)
    scores = [scores[s] for s in shuf]
    actions = [actions[s] for s in shuf]
    return actions[np.argmax(scores)].col
