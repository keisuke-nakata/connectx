import abc
import json
from logging import root
from pathlib import Path
import random
from typing import Generic, Optional
from connectx.tutorial.minimax import Node

import numpy as np

from connectx.tutorial import connectx_game
from connectx.tutorial import connectx_minimax


# class Agent(abc.ABC, Generic[S

class Agent:
    _game: Optional[connectx_game.ConnectXGame]
    _scorer: Optional[connectx_minimax.ConnectXScorer]
    _minimax: Optional[connectx_minimax.ConnectXMinimax]

    def __init__(self, outdir: Path) -> None:
        self._outdir = outdir

        self._game = None
        self._scorer = None
        self._minimax = None

    def _call_core(self, state: connectx_game.ConnectXState) -> connectx_game.ConnectXAction:
        assert self._minimax is not None
        root_node = self._minimax(3, state)

        self._dump_gametree(root_node)

        shuf = list(range(len(root_node.children)))
        random.shuffle(shuf)
        r_children = [root_node.children[s] for s in shuf]
        scores = [node.score for node in r_children]
        actions = [node.parent_edge.action for node in r_children if node.parent_edge is not None]

        assert len(scores) == len(actions)
        return actions[np.argmax(scores)]

    def __call__(self, obs: connectx_game.Observation, config: connectx_game.Config) -> int:
        if (self._game is None) or (self._scorer is None) or (self._minimax is None):
            self._game = connectx_game.ConnectXGame(config.columns, config.rows, config.inarow)
            self._scorer = connectx_minimax.ConnectXScorer(config.inarow)
            self._minimax = connectx_minimax.ConnectXMinimax(self._game, self._scorer)

        grid = np.asarray(obs.board).reshape(config.rows, config.columns)
        state = connectx_game.ConnectXState(grid, next_player=1, step=obs.step)

        best_action = self._call_core(state)
        return best_action.col

    def _dump_gametree(self, root_node: Node[connectx_game.ConnectXState, connectx_game.ConnectXAction]) -> None:
        dumpdir = self._outdir / "tree"
        dumpdir.mkdir(exist_ok=True)
        with open(dumpdir / f"{str(root_node.state.step)}.json", "w") as f:
            json.dump(root_node.to_dict(), f)


# def agent(obs: connectx_game.Observation, config: connectx_game.Config) -> int:
#     game = connectx_game.ConnectXGame(config.columns, config.rows, config.inarow)
#     scorer = connectx_minimax.ConnectXScorer(config.inarow)
#     minimax = connectx_minimax.ConnectXMinimax(game, scorer)

#     grid = np.asarray(obs.board).reshape(config.rows, config.columns)
#     state = connectx_game.ConnectXState(grid, next_player=1)
#     root_node = minimax(3, state)

#     shuf = list(range(len(root_node.children)))
#     random.shuffle(shuf)
#     r_children = [root_node.children[s] for s in shuf]
#     scores = [node.score for node in r_children]
#     actions = [node.parent_edge.action for node in r_children if node.parent_edge is not None]
#     assert len(scores) == len(actions)
#     return actions[np.argmax(scores)].col
