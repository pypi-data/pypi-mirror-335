from random import sample

from .interfaces import IGate


class Swap(IGate):

    target1: int
    target2: int

    def __init__(self, target1: int = 0, target2: int = 2):
        self.target1 = target1
        self.target2 = target2

    def randomize(self, qubit_num: int) -> IGate:
        assert (
            qubit_num > 1
        ), "The Swap Gate requires at least 2 qubits to operate as intended."

        self.target1, self.target2 = sample(range(0, qubit_num), 2)
        return self

    def __repr__(self):
        return f"Swap(target1={self.target1}, target2={self.target2}"
