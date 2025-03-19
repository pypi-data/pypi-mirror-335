import numpy as np
from random import randint, random, sample
from typing import List

from .interfaces import IGate, IOptimizableGate


class CX(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled X Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CX(control={self.controll}, target={self.target})"


class CY(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled Y Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CY(control={self.controll}, target={self.target})"


class CZ(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled Z Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CZ(control={self.controll}, target={self.target})"


class CH(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled H Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CH(control={self.controll}, target={self.target})"


class CS(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled S Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CS(control={self.controll}, target={self.target})"


class CT(IGate):
    controll: int
    target: int

    def __init__(self, controll: int = 0, target: int = 1):
        self.controll = controll
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Controlled T Gate requires at least 2 qubits to operate as intended."

        self.target, self.controll = sample(range(0, qubit_num), 2)

        return self

    def __repr__(self):
        return f"CT(control={self.controll}, target={self.target})"


class CRX(IOptimizableGate):
    controll: int
    target: int
    theta: float

    def __init__(self, controll: int = 0, target: int = 1, theta: float = 0.0):
        self.controll = controll
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The CRX Gate requires at least 2 qubits to operate as intended."

        self.target, self.control = sample(range(0, qubit_num), 2)

        # Choose theta randomly, since theta = 0 is often a stationary
        # point and fails numerical optimizers to progress.
        self.theta = random() * 2 * np.pi - np.pi

        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The CRX gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"CRX(control={self.controll}, target={self.target}, theta={round(self.theta, 3)})"


class CRY(IOptimizableGate):
    controll: int
    target: int
    theta: float

    def __init__(self, controll: int = 0, target: int = 1, theta: float = 0.0):
        self.controll = controll
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The CRY Gate requires at least 2 qubits to operate as intended."

        self.target, self.control = sample(range(0, qubit_num), 2)

        # Choose theta randomly, since theta = 0 is often a stationary
        # point and fails numerical optimizers to progress.
        self.theta = random() * 2 * np.pi - np.pi

        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The CRY gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"CRY(control={self.controll}, target={self.target}, theta={round(self.theta, 3)})"


class CRZ(IOptimizableGate):
    controll: int
    target: int
    theta: float

    def __init__(self, controll: int = 0, target: int = 1, theta: float = 0.0):
        self.controll = controll
        self.target = target
        self.theta = theta

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The CRZ Gate requires at least 2 qubits to operate as intended."

        self.target, self.control = sample(range(0, qubit_num), 2)

        # Choose theta randomly, since theta = 0 is often a stationary
        # point and fails numerical optimizers to progress.
        self.theta = random() * 2 * np.pi - np.pi

        return self

    @property
    def params(self) -> List[float]:
        return [self.theta]

    def set_params(self, params: List[float]) -> None:
        assert len(params) == 1, "The CRZ gate requires exactly one parameter!"

        self.theta = params[0]

    def __repr__(self):
        return f"CRZ(control={self.controll}, target={self.target}, theta={round(self.theta, 3)})"
