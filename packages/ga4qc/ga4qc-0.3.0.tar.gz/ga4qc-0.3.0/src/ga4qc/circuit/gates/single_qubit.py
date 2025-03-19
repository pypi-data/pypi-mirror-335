import numpy as np
from random import randint, random
from typing import List

from .interfaces import IGate, IOptimizableGate


class Identity(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"Id(target={self.target})"


class X(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"X(target={self.target})"


class Y(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"Y(target={self.target})"


class Z(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"Z(target={self.target})"


class H(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"H(target={self.target})"


class S(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"S(target={self.target})"


class T(IGate):
    target: int

    def __init__(self, target: int = 0):
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        return self

    def __repr__(self):
        return f"T(target={self.target})"


class RX(IOptimizableGate):
    target: int
    theta: float

    def __init__(self, target: int = 0, theta: float = 0.0):
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        self.theta = random() * 2 * np.pi - np.pi
        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The RX gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"RX(target={self.target}, theta={round(self.theta, 3)})"


class RY(IOptimizableGate):
    target: int
    theta: float

    def __init__(self, target: int = 0, theta: float = 0.0):
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        self.theta = random() * 2 * np.pi - np.pi
        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The RY gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"RY(target={self.target}, theta={round(self.theta, 3)})"


class RZ(IOptimizableGate):
    target: int
    theta: float

    def __init__(self, target: int = 0, theta: float = 0.0):
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        self.theta = random() * 2 * np.pi - np.pi
        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The RZ gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"RZ(target={self.target}, theta={round(self.theta, 3)})"


class Phase(IOptimizableGate):
    target: int
    theta: float

    def __init__(self, target: int = 0, theta: float = 0.0):
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        self.target = randint(0, qubit_num - 1)
        self.theta = random() * 2 * np.pi - np.pi
        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The phase gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"Phase(target={self.target}, theta={round(self.theta, 3)})"
