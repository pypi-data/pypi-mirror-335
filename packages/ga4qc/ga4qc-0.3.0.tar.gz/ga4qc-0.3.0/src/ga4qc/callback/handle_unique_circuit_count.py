from abc import ABC, abstractmethod

from statistics import mean, stdev
from typing import List, Callable


from ga4qc.circuit import Circuit
from .interface import ICallback


class UniqueCircuitCountCallback(ICallback, ABC):
    def __call__(self, circuits: List[Circuit], generation: int) -> None:
        unique_circuit_count = len(set(circuits))
        circuit_count = len(circuits)

        self.handle(unique_circuit_count, circuit_count, generation)

    @abstractmethod
    def handle(
        self,
        unique_circuit_count: int,
        circuit_count: int,
        generation: int = None,
    ) -> None: ...
