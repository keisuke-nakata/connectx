from __future__ import annotations

import abc
from typing import Any, Generic, Optional, TypeVar, Sequence

from connectx.gamesolver import game


class Edge(Generic[game.A]):
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.action.id,
            "repr": str(self.action),
            "turn": self.action.turn.name.lower(),
            "isRational": self.is_rational,
        }


class Node(Generic[game.S, game.A]):
    def __init__(
        self,
        state: game.S,
        is_terminal: bool,
        score: float,
        parent_edge: Optional[Edge],
        children: Sequence["Node[game.S, game.A]"],
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
    def parent_edge(self) -> Optional[Edge[game.A]]:
        return self._parent_edge

    @property
    def children(self) -> Sequence["Node[game.S, game.A]"]:
        return self._children

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.state.id,
            "repr": str(self.state),
            "isTerminal": self.is_terminal,
            "score": self.score,
            "isRational": self.is_rational,
            "parentEdge": None if self.parent_edge is None else self.parent_edge.to_dict(),
            "children": [node.to_dict() for node in self.children],
        }


class Scorer(abc.ABC, Generic[game.S]):
    @abc.abstractmethod
    def __call__(self, state: game.S) -> float:
        pass


SC = TypeVar("SC", bound=Scorer)
