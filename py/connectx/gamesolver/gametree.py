from __future__ import annotations

import abc
import uuid
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, NewType, Optional, TypeVar

import numpy as np

from connectx.gamesolver import game

EdgeId = NewType("EdgeId", str)


class Edge(Generic[game.A]):
    def __init__(self, action: game.A) -> None:
        self._id = EdgeId(str(uuid.uuid4()))
        self._action = action
        self._properties: dict[str, Any] = {}

    @property
    def id(self) -> EdgeId:
        return self._id

    @property
    def action(self) -> game.A:
        return self._action

    @property
    def properties(self) -> Mapping[str, Any]:
        return self._properties


NodeId = NewType("NodeId", str)


class Node(Generic[game.R, game.S, game.A]):
    def __init__(self, state: game.S, result: Optional[game.R], parent_edge: Optional[Edge[game.A]]) -> None:
        self._id = NodeId(str(uuid.uuid4()))
        self._state = state
        self._result = result
        self._parent_edge = parent_edge
        self._properties: dict[str, Any] = {}
        self._children: list[NodeId] = []

    @property
    def id(self) -> NodeId:
        return self._id

    @property
    def state(self) -> game.S:
        return self._state

    @property
    def result(self) -> Optional[game.R]:  # None: ゲーム継続
        return self._result

    # @property
    # def is_rational(self) -> bool:
    #     return self._is_rational

    @property
    def properties(self) -> Mapping[str, Any]:
        return self._properties

    def set_property(self, key: str, value: Any) -> None:
        self._properties[key] = value

    @property
    def parent_edge(self) -> Optional[Edge[game.A]]:
        return self._parent_edge

    @property
    def children(self) -> Sequence[NodeId]:
        return self._children

    def add_child(self, node_id: NodeId) -> None:
        self._children.append(node_id)


class Scorer(abc.ABC, Generic[game.S]):
    @abc.abstractmethod
    def __call__(self, state: game.S) -> float:
        pass


SC = TypeVar("SC", bound=Scorer)


class Tree(Generic[game.R, game.S, game.A]):
    def __init__(self) -> None:
        self._nodes: dict[str, Node[game.R, game.S, game.A]] = {}
        self._root_node_id: Optional[NodeId] = None

    def add_root_node(self, state: game.S) -> NodeId:
        node = Node[game.R, game.S, game.A](state=state, result=None, parent_edge=None)
        self._nodes[node.id] = node
        self._root_node_id = node.id
        return node.id

    def grow(self, parent_node_id: NodeId, action: game.A, state: game.S, result: Optional[game.R]) -> NodeId:
        """Raises KeyError if node does not exist."""
        edge = Edge[game.A](action=action)
        node = Node[game.R, game.S, game.A](state=state, result=result, parent_edge=edge)
        parent_node = self._nodes[parent_node_id]  # maybe raises KeyError
        parent_node.add_child(node.id)
        self._nodes[node.id] = node
        return node.id

    def get_node_property(self, node_id: NodeId, key: str) -> Any:
        """Raises KeyError if node does not exist."""
        node = self._nodes[node_id]  # maybe raises KeyError
        return node.properties[key]

    def assign_node_property(self, node_id: NodeId, key: str, value: Any) -> None:
        """Raises KeyError if node does not exist."""
        node = self._nodes[node_id]  # maybe raises KeyError
        node.set_property(key=key, value=value)

    def get_node_state_result(self, node_id: NodeId) -> tuple[game.S, Optional[game.R]]:
        """Raises KeyError if node does not exist."""
        node = self._nodes[node_id]  # maybe raises KeyError
        return (node.state, node.result)

    def to_dict(self, get_rational_score: Callable[[Node[game.R, game.S, game.A]], float]) -> dict[str, Any]:
        def node_to_dict(node: Node[game.R, game.S, game.A], is_rational: bool) -> dict[str, Any]:
            rational_scores = []
            existing_children = []
            for child_node_id in node.children:
                try:
                    child_node = self._nodes[child_node_id]
                except KeyError:
                    continue
                rational_score = get_rational_score(child_node)
                rational_scores.append(rational_score)
                existing_children.append(child_node)
            aggregator = np.argmin if node.state.next_turn == game.Turn.OPPONENT else np.argmax
            rational_idx = aggregator(rational_scores) if len(rational_scores) > 0 else None
            return {
                "id": node.id,
                "repr": str(node.state),
                "isTerminal": node.result is not None,
                "isRational": is_rational,
                "properties": node.properties,
                "parentEdge": (
                    None if node.parent_edge is None else edge_to_dict(edge=node.parent_edge, is_rational=is_rational)
                ),
                "children": [
                    node_to_dict(node=child_node, is_rational=bool(idx == rational_idx) and is_rational)
                    for idx, child_node, in enumerate(existing_children)
                ],
            }

        def edge_to_dict(edge: Edge[game.A], is_rational: bool) -> dict[str, Any]:
            return {
                "id": edge.id,
                "repr": str(edge.action),
                "turn": edge.action.turn.name.lower(),
                "isRational": is_rational,
                "properties": edge.properties,
            }

        if self._root_node_id is None:
            raise RuntimeError
        try:
            root_node = self._nodes[self._root_node_id]
        except KeyError:
            raise RuntimeError

        return node_to_dict(node=root_node, is_rational=True)
