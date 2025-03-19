from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit


class ICircuitProcessor(ABC):
    """Base class of all circuit processors, including
    simulators and fitness functions."""

    @abstractmethod
    def process(self, circuits: List[Circuit], generation: int) -> None: ...
