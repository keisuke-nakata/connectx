from __future__ import annotations

from typing import Generic, Optional, Sequence

import numpy as np

from connectx.gamesolver import game, gametree


class MinimaxEdge(gametree.Edge[game.A]):
    def __init__(self, action: game.A) -> None:
        self._action = action

        self.is_rational = False

    @property
    def action(self) -> game.A:
        return self._action

    @property
    def is_rational(self) -> bool:
        return self._is_rational

    @is_rational.setter
    def is_rational(self, is_rational: bool) -> None:
        self._is_rational = is_rational


class MinimaxNode(gametree.Node[game.S, game.A]):
    def __init__(
        self,
        state: game.S,
        is_terminal: bool,
        score: float,
        parent_edge: Optional[MinimaxEdge],
        children: Sequence["MinimaxNode[game.S, game.A]"],
    ) -> None:
        self._state = state
        self._is_terminal = is_terminal
        self._score = score
        self._parent_edge = parent_edge
        self._children = children

        self.is_rational = False

    @property
    def state(self) -> game.S:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def score(self) -> float:
        return self._score

    @property
    def is_rational(self) -> bool:
        return self._is_rational

    @is_rational.setter
    def is_rational(self, is_rational: bool) -> None:
        self._is_rational = is_rational

    @property
    def parent_edge(self) -> Optional[MinimaxEdge[game.A]]:
        return self._parent_edge

    @property
    def children(self) -> Sequence["MinimaxNode[game.S, game.A]"]:
        return self._children


class Minimax(Generic[game.G, game.S, game.A, gametree.SC]):
    def __init__(self, game: game.G, scorer: gametree.SC) -> None:
        self._game = game
        self._scorer = scorer

    def __call__(
        self, depth: int, state: game.S, parent_edge: Optional[MinimaxEdge[game.A]] = None
    ) -> MinimaxNode[game.S, game.A]:
        root_node = self._call_core(depth, state, parent_edge)
        self._mark_rational(root_node)
        return root_node

    def _call_core(
        self, depth: int, state: game.S, parent_edge: Optional[MinimaxEdge[game.A]] = None
    ) -> MinimaxNode[game.S, game.A]:
        is_terminal, terminal_score = self._game.get_terminal_score(state)
        if is_terminal:
            return MinimaxNode[game.S, game.A](
                state=state, is_terminal=True, score=terminal_score, parent_edge=parent_edge, children=[]
            )
        if depth == 0:
            score = self._scorer(state)
            return MinimaxNode[game.S, game.A](
                state=state, is_terminal=False, score=score, parent_edge=parent_edge, children=[]
            )
        available_actions = self._game.get_available_actions(state)
        next_states = ((self._game.step(state, action), MinimaxEdge[game.A](action)) for action in available_actions)
        next_nodes = [self._call_core(depth - 1, next_state, edge) for next_state, edge in next_states]
        aggregator = min if state.next_turn == game.Turn.OPPONENT else max
        score = aggregator(node.score for node in next_nodes)
        return MinimaxNode[game.S, game.A](
            state=state, is_terminal=False, score=score, parent_edge=parent_edge, children=next_nodes
        )

    def _mark_rational(self, node: MinimaxNode[game.S, game.A]) -> None:
        node.is_rational = True
        if node.parent_edge is not None:
            node.parent_edge.is_rational = True

        if node.is_terminal or len(node.children) == 0:
            return

        next_scores = [child.score for child in node.children]
        aggregator = np.argmin if node.state.next_turn == game.Turn.OPPONENT else np.argmax
        rational_node = node.children[int(aggregator(next_scores))]
        self._mark_rational(rational_node)


if __name__ == "__main__":

    class ToyState(game.State):
        def __init__(self, i: int) -> None:
            self.i = i

        @property
        def next_turn(self) -> game.Turn:
            if self.i in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return game.Turn.OPPONENT
            else:
                return game.Turn.PLAYER

        @property
        def id(self) -> str:
            return str(self.i)

        def __str__(self) -> str:
            return f"Node #{self.i}"

    class ToyAction(game.Action):
        def __init__(self, to: int) -> None:
            self.to = to

        @property
        def id(self) -> str:
            return str(self.to)

        def __str__(self) -> str:
            return f"Edge #{self.to}"

        @property
        def turn(self) -> game.Turn:
            if self.to in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return game.Turn.PLAYER
            else:
                return game.Turn.OPPONENT

    class ToyGame(game.Game[ToyState, ToyAction]):
        def get_terminal_score(self, state: ToyState) -> tuple[bool, float]:
            x = (
                (False, float("nan")),
                (False, float("nan")),
                (False, float("nan")),
                (False, float("nan")),
                (False, float("nan")),
                (False, float("nan")),
                (False, float("nan")),
                (True, 40),
                (True, 0),
                (True, -1),
                (True, -20),
                (True, 10),
                (True, -10),
                (True, -5),
                (True, 30),
            )
            return x[state.i]

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
            x = {
                7: 40,
                8: 0,
                9: -1,
                10: -20,
                11: 10,
                12: -10,
                13: -5,
                14: 30,
            }
            return x[state.i]

    minimax = Minimax[ToyGame, ToyState, ToyAction, ToyScorer](ToyGame(), ToyScorer())
    root_node = minimax(depth=3, state=ToyState(0))

    import json
    from pathlib import Path

    outdir = Path("./out").resolve()
    outdir.mkdir(exist_ok=True)

    with open(outdir / "tree.json", "w") as f:
        json.dump(root_node.to_dict(), f)
