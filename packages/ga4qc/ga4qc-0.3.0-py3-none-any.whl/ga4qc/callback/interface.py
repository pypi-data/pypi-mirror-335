from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit


class ICallback(ABC):
    """Base class for all GA Callbacks."""

    @abstractmethod
    def __call__(self, circuits: List[Circuit], generation: int = None) -> None: ...
