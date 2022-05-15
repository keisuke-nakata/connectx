"""https://horomary.hatenablog.com/entry/2021/06/21/000500#1-%E5%8E%9F%E5%A7%8B%E3%83%A2%E3%83%B3%E3%83%86%E3%82%AB%E3%83%AB%E3%83%AD%E6%9C%A8%E6%8E%A2%E7%B4%A2
深さを固定し、そこからランダムプレイアウトするだけの単純な MCTS
"""

from __future__ import annotations

from typing import Generic, Optional, Sequence, Any, Mapping
import random

import numpy as np

from connectx.gamesolver import game, gametree


class MCTSEdge(gametree.Edge[game.A]):
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

    @property
    def properties(self) -> Mapping[str, Any]:
        return {}


class MCTSNode(gametree.Node[game.S, game.A]):
    def __init__(
        self,
        state: game.S,
        is_terminal: bool,
        parent_edge: Optional[MCTSEdge],
        parent_node: Optional["MCTSNode[game.S, game.A]"],
    ) -> None:
        self._state = state
        self._is_terminal = is_terminal
        self._parent_edge = parent_edge
        self._parent_node = parent_node

        self._children: Sequence["MCTSNode[game.S, game.A]"] = []
        self.is_rational = False
        self._win_rate = (0.0, 0)  # (n_player_win, n_play)

    @property
    def state(self) -> game.S:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def is_rational(self) -> bool:
        return self._is_rational

    @is_rational.setter
    def is_rational(self, is_rational: bool) -> None:
        self._is_rational = is_rational

    @property
    def properties(self) -> Mapping[str, Any]:
        return {
            "score": self.score,
            "winRate": f"{self.win_rate[0]}/{self.win_rate[1]}",
        }

    @property
    def parent_edge(self) -> Optional[MCTSEdge[game.A]]:
        return self._parent_edge

    @property
    def children(self) -> Sequence["MCTSNode[game.S, game.A]"]:
        return self._children

    @children.setter
    def children(self, children: Sequence["MCTSNode[game.S, game.A]"]) -> None:
        self._children = children

    # custom functions

    @property
    def parent_node(self) -> Optional["MCTSNode[game.S, game.A]"]:
        return self._parent_node

    @property
    def win_rate(self) -> tuple[float, int]:
        return self._win_rate

    def update_win_rate(self, score: float) -> None:
        self._win_rate = (self._win_rate[0] + score, self._win_rate[1] + 1)

    @property
    def score(self) -> float:
        return self._win_rate[0] / self._win_rate[1]


class MCTS(Generic[game.S, game.A]):
    def __init__(self, game: game.Game[game.S, game.A]) -> None:
        self._game = game

    def __call__(self, depth: int, state: game.S) -> MCTSNode[game.S, game.A]:
        if depth == 0:
            raise RuntimeError
        is_terminal, _ = self._game.get_terminal_score(state)
        if is_terminal:
            raise RuntimeError

        root_node = MCTSNode[game.S, game.A](
            state=state, is_terminal=is_terminal, parent_edge=None, parent_node=None
        )
        playout_nodes = self._expand_tree(root_node, depth)

        for node in playout_nodes:
            for _ in range(30):
                score = self._playout(node)
                self._backprop(node, score)

        self._mark_rational(root_node)

        return root_node

    def _expand_tree(self, node: MCTSNode[game.S, game.A], depth: int) -> list[MCTSNode[game.S, game.A]]:
        prev_level_nodes = [node]
        for _ in range(depth):
            current_level_nodes: list[MCTSNode[game.S, game.A]] = []
            for node in prev_level_nodes:
                current_level_nodes.extend(self._expand_node(node))
            prev_level_nodes = current_level_nodes
        return current_level_nodes

    def _expand_node(self, node: MCTSNode[game.S, game.A]) -> list[MCTSNode[game.S, game.A]]:
        if node.is_terminal:
            return [node]
        available_actions = self._game.get_available_actions(node.state)
        next_states = [
            (self._game.step(node.state, action), MCTSEdge[game.A](action)) for action in available_actions
        ]
        next_is_terminals = [self._game.get_terminal_score(state[0])[0] for state in next_states]

        next_nodes = [
            MCTSNode[game.S, game.A](state=state, is_terminal=is_terminal, parent_edge=edge, parent_node=node)
            for (state, edge), is_terminal in zip(next_states, next_is_terminals)
        ]
        node.children = next_nodes
        return next_nodes

    def _playout(self, node: MCTSNode[game.S, game.A]) -> float:
        state = node.state
        while True:
            is_terminal, score = self._game.get_terminal_score(state)
            if is_terminal:
                if score > 0:
                    return 1.0
                elif score == 0:
                    return 0.5
                else:
                    return 0.0
            available_actions = self._game.get_available_actions(state)
            action = random.choice(available_actions)
            state = self._game.step(state, action)

    def _backprop(self, node: MCTSNode[game.S, game.A], score: float) -> None:
        current_node: Optional[MCTSNode[game.S, game.A]] = node
        while current_node is not None:
            current_node.update_win_rate(score)
            current_node = current_node.parent_node

    def _mark_rational(self, node: MCTSNode[game.S, game.A]) -> None:
        node.is_rational = True
        if node.parent_edge is not None:
            node.parent_edge.is_rational = True

        if node.is_terminal or len(node.children) == 0:
            return

        next_scores = [child.score for child in node.children]
        aggregator = np.argmin if node.state.next_turn == game.Turn.OPPONENT else np.argmax
        rational_node = node.children[int(aggregator(next_scores))]
        self._mark_rational(rational_node)
