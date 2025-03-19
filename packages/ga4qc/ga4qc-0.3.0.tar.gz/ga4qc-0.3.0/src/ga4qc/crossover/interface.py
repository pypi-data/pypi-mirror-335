from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit


class ICrossover(ABC):
    """Base class of all crossover operators."""

    prob: float = 1.0

    @abstractmethod
    def cross(self, circuit1: Circuit, circuit2: Circuit, generation: int) -> None: ...
