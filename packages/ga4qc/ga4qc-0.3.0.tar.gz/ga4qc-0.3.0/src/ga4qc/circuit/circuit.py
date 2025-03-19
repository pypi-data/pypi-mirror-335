from copy import deepcopy
from numpy import ndarray
from typing import List

from .gates import IGate, Oracle


class Circuit:
    """Class containing a list of gates as well as their
    unitaries and fitness values."""

    gates: List[IGate]
    fitness_values: List[float]
    unitaries: List[ndarray]

    qubit_num: int

    def __init__(self, gates: List[IGate], qubit_num: int):
        self.gates = gates
        self.qubit_num = qubit_num

        self.fitness_values = None
        self.unitaries = None

    def __len__(self) -> int:
        return len(self.gates)

    @property
    def case_count(self) -> int:
        for gate in self.gates:
            if type(gate) is Oracle:
                return gate.case_count

        return 1

    def reset(self) -> None:
        self.unitaries = []
        self.fitness_values = []

    @property
    def state_vectors(self) -> List[ndarray]:
        assert self.unitaries is not None, (
            "Circuit unitaries have to be set for state vectors to be available. "
            "Have you called a simulator?"
        )

        vectors = [unitary[:, 0] for unitary in self.unitaries]
        return vectors

    def copy(self) -> "Circuit":
        return deepcopy(self)

    def __repr__(self):
        return "[" + ", ".join([gate.__repr__() for gate in self.gates]) + "]"

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __eq__(self, comparison_circuit: "Circuit") -> bool:
        return self.__hash__() == comparison_circuit.__hash__()
