import json
import random
from pathlib import Path
from typing import Optional
import time

import numpy as np

from connectx.gamesolver import gametree
from connectx.tutorial import connectx_game, connectx_solver


class Agent:
    _game: Optional[connectx_game.ConnectXGame]
    _scorer: Optional[connectx_solver.ConnectXScorer]
    _primitive_mcts: Optional[connectx_solver.ConnectXPrimitiveMCTS]

    def __init__(self, depth: int, outdir: Optional[Path]) -> None:
        self._depth = depth
        self._outdir = outdir

        self._game = None
        self._scorer = None
        self._primitive_mcts = None

    def _call_core(self, state: connectx_game.ConnectXState) -> connectx_game.ConnectXAction:
        start = time.time()

        assert self._primitive_mcts is not None
        root_node = self._primitive_mcts(self._depth, state)

        self._dump_gametree(root_node)

        shuf = list(range(len(root_node.children)))
        random.shuffle(shuf)
        r_children = [root_node.children[s] for s in shuf]
        scores = [node.score for node in r_children]
        actions = [node.parent_edge.action for node in r_children if node.parent_edge is not None]

        assert len(scores) == len(actions)

        end = time.time()
        print(end - start)
        return actions[np.argmax(scores)]

    def __call__(self, obs: connectx_game.Observation, config: connectx_game.Config) -> int:
        if (self._game is None) or (self._scorer is None) or (self._primitive_mcts is None):
            self._game = connectx_game.ConnectXGame(config.columns, config.rows, config.inarow)
            self._primitive_mcts = connectx_solver.ConnectXPrimitiveMCTS(self._game)

        grid = np.asarray(obs.board).reshape(config.rows, config.columns)
        state = connectx_game.ConnectXState(grid, next_player=1, step=obs.step)

        best_action = self._call_core(state)
        return best_action.col

    def _dump_gametree(
        self, root_node: gametree.Node[connectx_game.ConnectXState, connectx_game.ConnectXAction]
    ) -> None:
        if self._outdir is None:
            return
        dumpdir = self._outdir / "tree"
        dumpdir.mkdir(exist_ok=True)
        with open(dumpdir / f"{str(root_node.state.step)}.json", "w") as f:
            json.dump(root_node.to_dict(), f)
