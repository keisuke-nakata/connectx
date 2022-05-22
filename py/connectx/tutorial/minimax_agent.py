import json
from pathlib import Path
from typing import Optional

import numpy as np

from connectx.gamesolver import gametree, minimax
from connectx.tutorial import connectx_game, connectx_solver


class Agent:
    _game: Optional[connectx_game.ConnectXGame]
    _scorer: Optional[connectx_solver.ConnectXScorer]
    _minimax: Optional[connectx_solver.ConnectXMinimax]

    def __init__(self, depth: int, outdir: Optional[Path]) -> None:
        self._depth = depth
        self._outdir = outdir

        self._game = None
        self._scorer = None
        self._minimax = None

    def __call__(self, obs: connectx_game.Observation, config: connectx_game.Config) -> int:
        grid = np.asarray(obs.board).reshape(config.rows, config.columns)
        state = connectx_game.ConnectXState(grid, next_player=1, step=obs.step)
        tree = gametree.Tree[connectx_game.ConnectXState, connectx_game.ConnectXResult, connectx_game.ConnectXAction]()

        if (self._game is None) or (self._scorer is None):
            self._game = connectx_game.ConnectXGame(config.columns, config.rows, config.inarow)
            self._scorer = connectx_solver.ConnectXScorer(config.inarow)

        connectx_minimax = connectx_solver.ConnectXMinimax(self._game, self._scorer, tree)
        connectx_minimax(depth=self._depth, state=state)

        best_action = tree.get_rational_action(get_rational_score=minimax.get_rational_score)
        self._dump_gametree(tree)
        return best_action.col

    def _dump_gametree(
        self,
        tree: gametree.Tree[connectx_game.ConnectXState, connectx_game.ConnectXResult, connectx_game.ConnectXAction],
    ) -> None:
        if self._outdir is None:
            return
        dumpdir = self._outdir / "tree"
        dumpdir.mkdir(exist_ok=True)
        state, _ = tree.get_node_state_result(tree.root_node_id)
        d = tree.to_dict(get_rational_score=minimax.get_rational_score)
        with open(dumpdir / f"{str(state.step)}.json", "w") as f:
            json.dump(d, f)
