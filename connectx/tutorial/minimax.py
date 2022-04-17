import abc
from typing import Sequence, TypeVar, Generic, Tuple


class State(abc.ABC):
    @abc.abstractproperty
    def is_opponent_turn(self) -> bool:
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
    def get_terminal_score(self, state: S) -> Tuple[bool, float]:
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


def minimax(game: Game, depth: int, state: State, scorer: Scorer) -> float:
    is_terminal, score = game.get_terminal_score(state)
    if is_terminal:
        # print(f"{state.i}: {score}")
        return score
    if depth == 0:
        # print(f"{state.i}: {user_score_fn(state)}")
        return scorer(state)
    available_actions = game.get_available_actions(state)
    next_states = (game.step(state, action) for action in available_actions)
    next_scores = (minimax(game, depth - 1, next_state, scorer) for next_state in next_states)
    if state.is_opponent_turn:
        next_score = min(next_scores)
    else:
        next_score = max(next_scores)
    # print(f"{state.i}: {next_score}")
    return next_score


def argminimax(game: Game, depth: int, state: State, scorer: Scorer) -> Tuple[Sequence[float], Sequence[Action]]:
    is_terminal, score = game.get_terminal_score(state)
    if is_terminal:
        raise RuntimeError
    if depth == 0:
        raise RuntimeError
    available_actions = game.get_available_actions(state)
    if len(available_actions) == 0:
        raise RuntimeError
    scores = [minimax(game, depth - 1, game.step(state, action), scorer) for action in available_actions]
    return scores, available_actions


if __name__ == "__main__":
    class ToyState(State):
        def __init__(self, i: int) -> None:
            self.i = i

        @property
        def is_opponent_turn(self) -> bool:
            return self.i in (1, 2, 7, 8, 9, 10, 11, 12, 13, 14)

    class ToyAction(Action):
        def __init__(self, to: int) -> None:
            self.to = to

    class ToyGame(Game[ToyState, ToyAction]):
        def get_terminal_score(self, state: ToyState) -> Tuple[bool, float]:
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

    print(minimax(ToyGame(), depth=3, state=ToyState(0), scorer=ToyScorer()))
    print(argminimax(ToyGame(), depth=3, state=ToyState(0), scorer=ToyScorer()))
