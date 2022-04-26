import abc
from collections.abc import Sequence
from typing import TypeVar, Generic
import enum


class Turn(enum.Enum):
    PLAYER = enum.auto()
    OPPONENT = enum.auto()


class State(abc.ABC):
    @abc.abstractproperty
    def next_turn(self) -> Turn:
        pass


class Action(abc.ABC):
    pass


S = TypeVar("S", bound=State)
A = TypeVar("A", bound=Action)


class Game(abc.ABC, Generic[S, A]):
    """
    ゲームのルールを記述するクラス。state は外に持ち、このクラス自体は状態を持たない
    """

    @abc.abstractmethod
    def get_terminal_score(self, state: S) -> tuple[bool, float]:
        """
        state が最終状態 (それ以上手がない) であれば (True, score) を返す。
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


class Minimax(abc.ABC, Generic[G, S, A, SC]):
    def __init__(self, game: G) -> None:
        self._game = game

    def __call__(self, depth: int, state: S, scorer: SC) -> float:
        is_terminal, score = self._game.get_terminal_score(state)
        if is_terminal:
            return score
        if depth == 0:
            return scorer(state)
        available_actions = self._game.get_available_actions(state)
        next_states = (self._game.step(state, action) for action in available_actions)
        next_scores = (self.__call__(depth - 1, next_state, scorer) for next_state in next_states)
        if state.next_turn == Turn.OPPONENT:
            return min(next_scores)
        else:
            return max(next_scores)

    def argminimax(self, depth: int, state: S, scorer: SC) -> tuple[Sequence[float], Sequence[A]]:
        if depth == 0:
            raise RuntimeError
        is_terminal, score = self._game.get_terminal_score(state)
        if is_terminal:
            raise RuntimeError
        available_actions = self._game.get_available_actions(state)
        if len(available_actions) == 0:
            raise RuntimeError
        scores = [self.__call__(depth - 1, self._game.step(state, action), scorer) for action in available_actions]
        return scores, available_actions


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

    class ToyAction(Action):
        def __init__(self, to: int) -> None:
            self.to = to

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
                14: 30
            }
            return x[state.i]

    class ToyMinimax(Minimax[ToyGame, ToyState, ToyAction, ToyScorer]):
        pass

    minimax = ToyMinimax(ToyGame())

    print(minimax(depth=3, state=ToyState(0), scorer=ToyScorer()))
    print(minimax.argminimax(depth=3, state=ToyState(0), scorer=ToyScorer()))
