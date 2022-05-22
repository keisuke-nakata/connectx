from __future__ import annotations

from typing import Generic, Optional

from connectx.gamesolver import game, gametree


class Minimax(Generic[game.R, game.S, game.A, gametree.SC]):
    def __init__(
        self, game: game.Game[game.R, game.S, game.A], scorer: gametree.SC, tree: gametree.Tree[game.R, game.S, game.A]
    ) -> None:
        self._game = game
        self._scorer = scorer
        self._tree = tree

    def __call__(self, depth: int, state: game.S) -> None:
        if self._game.get_result(state=state) is not None:
            raise RuntimeError("Game is already over.")
        root_node_id = self._tree.add_root_node(state=state)
        self._call_core_safe(depth=depth, node_id=root_node_id)
        # self._mark_rational(root_node)

    def _call_core_safe(self, depth: int, node_id: gametree.NodeId) -> None:
        try:
            self._call_core(depth, node_id)
        except KeyError:  # すでにノードがない
            return

    def _call_core(self, depth: int, node_id: gametree.NodeId) -> None:
        """与えられた node_id に対する score を計算する (つまり、この関数が呼ばれた時点で node はすでに tree に追加されている前提)"""
        state, result = self._tree.get_node_state_result(node_id=node_id)
        if result is not None:  # ゲーム終了
            score = self._scorer(state)
            self._tree.assign_node_property(node_id, "score", score)
            return
        if depth == 0:
            score = self._scorer(state)
            self._tree.assign_node_property(node_id, "score", score)
            return
        # ゲーム継続; 木を成長させつつ再帰呼び出し
        next_actions = self._game.get_available_actions(state)
        next_states = [self._game.step(state, action) for action in next_actions]
        next_results = [self._game.get_result(state=state) for state in next_states]
        children = []
        for next_action, next_state, next_result in zip(next_actions, next_states, next_results):
            child_node_id = self._tree.grow(
                parent_node_id=node_id, action=next_action, state=next_state, result=next_result
            )
            self._call_core_safe(depth=depth - 1, node_id=child_node_id)
            children.append(child_node_id)
        # 子ノードのスコアを集約して自分のスコアを計算
        scores: list[float] = []
        for child_node_id in children:
            try:
                score = self._tree.get_node_property(node_id=child_node_id, key="score")
                scores.append(score)
            except KeyError:  # 子ノードが存在しない場合はスキップ
                pass
        aggregator = min if state.next_turn == game.Turn.OPPONENT else max
        score = aggregator(scores)
        self._tree.assign_node_property(node_id, "score", score)


def get_rational_score(node: gametree.Node) -> float:
    score: float = node.properties.get("score", float("-Inf"))
    return score


if __name__ == "__main__":
    toy_scores = {
        7: 40,
        8: 0,
        9: -1,
        10: -20,
        11: 10,
        12: -10,
        13: -5,
        14: 30,
    }

    class ToyResult(game.Result):
        def __init__(self, winner: Optional[game.Turn]) -> None:
            self._winner = winner

        @property
        def winner(self) -> Optional[game.Turn]:
            return self._winner

    class ToyState(game.State):
        def __init__(self, i: int) -> None:
            self.i = i

        @property
        def next_turn(self) -> game.Turn:
            if self.i in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return game.Turn.OPPONENT
            else:
                return game.Turn.PLAYER

        def __str__(self) -> str:
            return f"State #{self.i}"

    class ToyAction(game.Action):
        def __init__(self, to: int) -> None:
            self.to = to

        def __str__(self) -> str:
            return f"Action #{self.to}"

        @property
        def turn(self) -> game.Turn:
            if self.to in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return game.Turn.PLAYER
            else:
                return game.Turn.OPPONENT

    class ToyGame(game.Game[ToyResult, ToyState, ToyAction]):
        def get_result(self, state: ToyState) -> Optional[ToyResult]:
            if state.i < 7:
                return None
            if toy_scores[state.i] > 0:
                return ToyResult(game.Turn.PLAYER)
            elif toy_scores[state.i] == 0:
                return ToyResult(None)
            else:
                return ToyResult(game.Turn.OPPONENT)

        def get_available_actions(self, state: ToyState) -> list[ToyAction]:
            if state.i >= 7:
                return []
            return [ToyAction(x) for x in (state.i * 2 + 1, state.i * 2 + 2)]

        def step(self, state: ToyState, action: ToyAction) -> ToyState:
            return ToyState(action.to)

    class ToyScorer(gametree.Scorer[ToyState]):
        def __call__(self, state: ToyState) -> float:
            if state.i < 7:
                return 0
            return toy_scores[state.i]

    tree = gametree.Tree[ToyResult, ToyState, ToyAction]()
    minimax = Minimax[ToyResult, ToyState, ToyAction, ToyScorer](ToyGame(), ToyScorer(), tree)
    minimax(depth=3, state=ToyState(0))

    import datetime as dt
    import json
    from pathlib import Path

    outdir = Path("./out").resolve() / dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir.mkdir(exist_ok=True, parents=True)
    d = tree.to_dict(get_rational_score)
    # def typecheck(dd):
    #     if isinstance(dd, dict):
    #         ret = {}
    #         for k, v in dd.items():
    #             ret[k] = typecheck(v)
    #         return ret
    #     if isinstance(dd, list):
    #         ret = []
    #         for x in dd:
    #             ret.append(typecheck(x))
    #         return ret
    #     return type(dd)
    # t = typecheck(d)
    with open(outdir / "tree.json", "w") as f:
        json.dump(d, f)
