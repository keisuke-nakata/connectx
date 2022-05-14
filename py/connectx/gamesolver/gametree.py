from __future__ import annotations

import abc
from typing import Any, Generic, Optional, TypeVar, Sequence, Mapping

from connectx.gamesolver import game


class Edge(abc.ABC, Generic[game.A]):
    @property
    def id(self) -> str:
        return self.action.id

    @abc.abstractproperty
    def action(self) -> game.A:
        pass

    @abc.abstractproperty
    def is_rational(self) -> bool:
        pass

    @abc.abstractproperty
    def properties(self) -> Mapping[str, Any]:
        pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "repr": str(self.action),
            "turn": self.action.turn.name.lower(),
            "isRational": self.is_rational,
            "properties": self.properties,
        }


class Node(abc.ABC, Generic[game.S, game.A]):
    @property
    def id(self) -> str:
        return self.state.id

    @abc.abstractproperty
    def state(self) -> game.S:
        pass

    @abc.abstractproperty
    def is_terminal(self) -> bool:
        pass

    @abc.abstractproperty
    def is_rational(self) -> bool:
        pass

    @abc.abstractproperty
    def properties(self) -> Mapping[str, Any]:
        pass

    @abc.abstractproperty
    def parent_edge(self) -> Optional[Edge[game.A]]:
        pass

    @abc.abstractproperty
    def children(self) -> Sequence["Node[game.S, game.A]"]:
        pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "repr": str(self.state),
            "isTerminal": self.is_terminal,
            "isRational": self.is_rational,
            "properties": self.properties,
            "parentEdge": None if self.parent_edge is None else self.parent_edge.to_dict(),
            "children": [node.to_dict() for node in self.children],
        }


class Scorer(abc.ABC, Generic[game.S]):
    @abc.abstractmethod
    def __call__(self, state: game.S) -> float:
        pass


SC = TypeVar("SC", bound=Scorer)
