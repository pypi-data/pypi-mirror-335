from typing import List, Tuple, Union, Set

from ga4qc.circuit import Circuit
from .interface import ICircuitProcessor
from ga4qc.seeder import ISeeder


class RemoveDuplicates(ICircuitProcessor):
    seeder: ISeeder

    def __init__(self, seeder: ISeeder):
        self.seeder = seeder

    def process(self, circuits: List[Circuit], generation: int) -> None:
        encountered_circuits: Set = set()

        for i, circuit in enumerate(circuits):

            if circuit in encountered_circuits:
                circuits[i] = self.seeder.seed(population_size=1)
            else:
                encountered_circuits.add(circuit)