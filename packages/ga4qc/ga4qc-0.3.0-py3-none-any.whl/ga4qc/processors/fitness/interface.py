from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit
from ga4qc.processors.interface import ICircuitProcessor


class IFitness(ICircuitProcessor):
    """Base class of all fitness functions."""

    @abstractmethod
    def process(self, circuits: List[Circuit], generation: int) -> None: ...
