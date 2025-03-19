from typing import List, Type

from ga4qc.circuit import Circuit, IGate, random_circuit
from .interface import ISeeder
from ga4qc.params import GAParams


class RandomSeeder(ISeeder):
    params: GAParams

    def __init__(self, params: GAParams):
        self.params = params

    def seed(self, population_size: int) -> List[Circuit]:
        population = []

        for _ in range(population_size):
            circuit = random_circuit(
                self.params.gate_set, self.params.chromosome_length, self.params.qubit_num)
            population.append(circuit)

        return population
