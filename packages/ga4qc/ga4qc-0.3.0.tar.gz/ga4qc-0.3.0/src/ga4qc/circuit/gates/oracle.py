from typing import List

from .interfaces import IGate


class Oracle(IGate):
    sub_circuits: List[List[IGate]]
    name: str

    def __init__(self, sub_circuits: List[List[IGate]], name: str = "Oracle"):
        self.sub_circuits = sub_circuits
        self.name = name

    def randomize(self, qubit_num: int) -> IGate:
        return self

    def get_gates(self, case_i: int) -> List[IGate]:
        return self.sub_circuits[case_i]

    @property
    def case_count(self) -> int:
        return len(self.sub_circuits)

    def __repr__(self):
        return f"{self.name}()"


class OracleConstructor:
    sub_circuits: List[List[IGate]]
    name: str

    def __init__(self, sub_circuits: List[List[IGate]], name: str = "Oracle"):
        self.sub_circuits = sub_circuits
        self.name = name

    def __call__(self) -> Oracle:
        return Oracle(sub_circuits=self.sub_circuits, name=self.name)
