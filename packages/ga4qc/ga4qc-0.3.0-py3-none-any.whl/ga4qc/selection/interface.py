from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit


class ISelection(ABC):
    """Base class for all selection operators."""

    @abstractmethod
    def select(self, circuits: List[Circuit], k: int, generation: int) -> List[Circuit]: ...
