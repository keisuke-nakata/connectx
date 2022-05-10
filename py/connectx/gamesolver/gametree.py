from __future__ import annotations

import abc
from typing import Any, Generic, Optional, TypeVar, Sequence

from connectx.gamesolver import game


class Edge(abc.ABC, Generic[game.A]):
    @abc.abstractproperty
    def action(self) -> game.A:
        pass

    @abc.abstractproperty
    def is_rational(self) -> bool:
        pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.action.id,
            "repr": str(self.action),
            "turn": self.action.turn.name.lower(),
            "isRational": self.is_rational,
        }


class Node(abc.ABC, Generic[game.S, game.A]):
    @abc.abstractproperty
    def state(self) -> game.S:
        pass

    @abc.abstractproperty
    def is_terminal(self) -> bool:
        pass

    @abc.abstractproperty
    def score(self) -> float:
        pass

    @abc.abstractproperty
    def is_rational(self) -> bool:
        pass

    @abc.abstractproperty
    def parent_edge(self) -> Optional[Edge[game.A]]:
        pass

    @abc.abstractproperty
    def children(self) -> Sequence["Node[game.S, game.A]"]:
        pass

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
