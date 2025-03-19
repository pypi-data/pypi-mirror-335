from abc import ABC, abstractmethod

from ga4qc.circuit import Circuit


class IMutation(ABC):
    """Base class of all mutation operations."""

    prob: float = 1.0

    @abstractmethod
    def mutate(self, circuit: Circuit, generation: int) -> None: ...
