from __future__ import annotations

import abc
import enum
from typing import Generic, Optional, TypeVar


class Turn(enum.Enum):
    PLAYER = enum.auto()
    OPPONENT = enum.auto()


class Result(abc.ABC):
    @abc.abstractproperty
    def winner(self) -> Optional[Turn]:  # None は draw
        pass


class State(abc.ABC):
    @abc.abstractproperty
    def next_turn(self) -> Turn:
        pass

    # for node's `repr`
    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class Action(abc.ABC):
    # for edge's `repr`
    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractproperty
    def turn(self) -> Turn:
        pass


R = TypeVar("R", bound=Result)
S = TypeVar("S", bound=State)
A = TypeVar("A", bound=Action)


class Game(abc.ABC, Generic[R, S, A]):
    """
    ゲームのルールを記述するクラス。state は外に持ち、このクラス自体は状態を持たない
    """

    @abc.abstractmethod
    def get_result(self, state: S) -> Optional[R]:
        """
        state が最終状態 (それ以上手がない) であれば Result を返す。
        そうでない場合、None を返す。
        """
        pass

    @abc.abstractmethod
    def get_available_actions(self, state: S) -> list[A]:
        pass

    @abc.abstractmethod
    def step(self, state: S, action: A) -> S:
        pass
