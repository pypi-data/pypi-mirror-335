import numpy as np
from random import randint, random, sample
from typing import List

from .interfaces import IGate


class CCX(IGate):
    controll1: int
    controll2: int
    target: int

    def __init__(self, controll1: int = 0, controll2: int = 1, target: int = 2):
        self.controll1 = controll1
        self.controll2 = controll2
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 2
        ), "The CC X Gate requires at least 3 qubits to operate as intended."

        self.controll1, self.controll2, self.target = sample(range(0, qubit_num), 3)

        return self

    def __repr__(self):
        return f"CCX(control1={self.controll1}, control2={self.controll2}, target={self.target})"


class CCZ(IGate):
    controll1: int
    controll2: int
    target: int

    def __init__(self, controll1: int = 0, controll2: int = 1, target: int = 2):
        self.controll1 = controll1
        self.controll2 = controll2
        self.target = target

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 2
        ), "The CC Z Gate requires at least 3 qubits to operate as intended."

        self.controll1, self.controll2, self.target = sample(range(0, qubit_num), 3)

        return self

    def __repr__(self):
        return f"CCZ(control1={self.controll1}, control2={self.controll2}, target={self.target})"
