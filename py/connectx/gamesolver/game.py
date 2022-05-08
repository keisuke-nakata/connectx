from __future__ import annotations

import abc
import enum
from typing import Generic, TypeVar


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


S = TypeVar("S", bound=State)
A = TypeVar("A", bound=Action)


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
    def get_available_actions(self, state: S) -> list[A]:
        pass

    @abc.abstractmethod
    def step(self, state: S, action: A) -> S:
        pass


G = TypeVar("G", bound=Game)
