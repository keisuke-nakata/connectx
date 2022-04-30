import abc
import enum
from collections.abc import Mapping, Sequence
from typing import Any, Generic, Optional, TypeVar


class Turn(enum.Enum):
    PLAYER = enum.auto()
    OPPONENT = enum.auto()


class State(abc.ABC):
    @abc.abstractproperty
    def next_turn(self) -> Turn:
        pass

    @abc.abstractproperty
    def id(self) -> str:
        pass

    # for node's `repr`
    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractproperty
    def property_(self) -> Mapping[str, Any]:
        pass


class Action(abc.ABC):
    @abc.abstractproperty
    def id(self) -> str:
        pass

    # for edge's `repr`
    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractproperty
    def turn(self) -> Turn:
        pass

    @abc.abstractproperty
    def property_(self) -> Mapping[str, Any]:
        pass


S = TypeVar("S", bound=State)
A = TypeVar("A", bound=Action)


class Edge(Generic[A]):
    def __init__(self, action: A) -> None:
        self._action = action

    @property
    def action(self) -> A:
        return self._action

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "id": self.action.id,
            "repr": str(self.action),
            "turn": self.action.turn.name.lower(),
            "property": self.action.property_,
        }


class Node(Generic[S, A]):
    def __init__(
        self, state: S, is_terminal: bool, score: float, parent_edge: Optional[Edge], children: Sequence["Node[S, A]"]
    ) -> None:
        self._state = state
        self._is_terminal = is_terminal
        self._score = score
        self._parent_edge = parent_edge
        self._children = children

    @property
    def state(self) -> S:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def score(self) -> float:
        return self._score

    @property
    def parent_edge(self) -> Optional[Edge[A]]:
        return self._parent_edge

    @property
    def children(self) -> Sequence["Node[S, A]"]:
        return self._children

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "id": self.state.id,
            "repr": str(self.state),
            "isTerminal": self.is_terminal,
            "score": self.score,
            "property": self.state.property_,
            "parentEdge": None if self.parent_edge is None else self.parent_edge.to_dict(),
            "children": [node.to_dict() for node in self.children],
        }


class Game(abc.ABC, Generic[S, A]):
    """
    ゲームのルールを記述するクラス。state は外に持ち、このクラス自体は状態を持たない
    """

    @abc.abstractmethod
    def get_terminal_score(self, state: S) -> tuple[bool, float]:
        """
        state が最終状態 (それ以上手がない) であれば (True, terminal_score) を返す。
        そうでない場合、(False, nan) を返す。
        """
        pass

    @abc.abstractmethod
    def get_available_actions(self, state: S) -> Sequence[A]:
        pass

    @abc.abstractmethod
    def step(self, state: S, action: A) -> S:
        pass


class Scorer(abc.ABC, Generic[S]):
    @abc.abstractmethod
    def __call__(self, state: S) -> float:
        pass


G = TypeVar("G", bound=Game)
SC = TypeVar("SC", bound=Scorer)


# TODO: abc.ABC を削除
class Minimax(abc.ABC, Generic[G, S, A, SC]):
    def __init__(self, game: G, scorer: SC) -> None:
        self._game = game
        self._scorer = scorer

    def __call__(self, depth: int, state: S, parent_edge: Optional[Edge[A]] = None) -> Node[S, A]:
        is_terminal, terminal_score = self._game.get_terminal_score(state)
        if is_terminal:
            return Node[S, A](state=state, is_terminal=True, score=terminal_score, parent_edge=parent_edge, children=[])
        if depth == 0:
            score = self._scorer(state)
            return Node[S, A](state=state, is_terminal=False, score=score, parent_edge=parent_edge, children=[])
        available_actions = self._game.get_available_actions(state)
        next_states = ((self._game.step(state, action), Edge[A](action)) for action in available_actions)
        next_nodes = [self.__call__(depth - 1, next_state, edge) for next_state, edge in next_states]
        aggregater = min if state.next_turn == Turn.OPPONENT else max
        score = aggregater(node.score for node in next_nodes)
        return Node[S, A](state=state, is_terminal=False, score=score, parent_edge=parent_edge, children=next_nodes)


if __name__ == "__main__":

    class ToyState(State):
        def __init__(self, i: int) -> None:
            self.i = i

        @property
        def next_turn(self) -> Turn:
            if self.i in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return Turn.OPPONENT
            else:
                return Turn.PLAYER

        @property
        def id(self) -> str:
            return str(self.i)

        def __str__(self) -> str:
            return f"Node #{self.i}"

        @property
        def property_(self) -> Mapping[str, Any]:
            return {}

    class ToyAction(Action):
        def __init__(self, to: int) -> None:
            self.to = to

        @property
        def id(self) -> str:
            return str(self.to)

        def __str__(self) -> str:
            return f"Edge #{self.to}"

        @property
        def turn(self) -> Turn:
            if self.to in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14):
                return Turn.PLAYER
            else:
                return Turn.OPPONENT

        @property
        def property_(self) -> Mapping[str, Any]:
            return {}

    class ToyGame(Game[ToyState, ToyAction]):
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

        def get_available_actions(self, state: ToyState) -> Sequence[ToyAction]:
            if state.i >= 7:
                return []
            return [ToyAction(x) for x in (state.i * 2 + 1, state.i * 2 + 2)]

        def step(self, state: ToyState, action: ToyAction) -> ToyState:
            return ToyState(action.to)

    class ToyScorer(Scorer[ToyState]):
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

    class ToyMinimax(Minimax[ToyGame, ToyState, ToyAction, ToyScorer]):
        pass

    minimax = ToyMinimax(ToyGame(), ToyScorer())
    root_node = minimax(depth=3, state=ToyState(0))

    from pathlib import Path
    import json
    outdir = Path("./out").resolve()
    outdir.mkdir(exist_ok=True)

    with open(outdir / "tree.json", "w") as f:
        json.dump(root_node.to_dict(), f)
