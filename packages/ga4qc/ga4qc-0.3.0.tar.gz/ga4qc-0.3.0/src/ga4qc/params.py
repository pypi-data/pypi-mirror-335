from dataclasses import dataclass
from typing import List

from ga4qc.circuit.gates import IGate


@dataclass
class GAParams:
    population_size: int
    chromosome_length: int
    generations: int
    qubit_num: int
    gate_set: List[IGate]
    ancillary_qubit_num: int = 0
    elitism_count: int = 0
