from abc import ABC, abstractmethod
from typing import List


class IGate(ABC):

    @abstractmethod
    def randomize(self, qubit_num: int) -> "IGate": ...

    @abstractmethod
    def __repr__(self) -> str: ...


class IOptimizableGate(IGate, ABC):

    @property
    @abstractmethod
    def params(self) -> List[float]: ...

    @abstractmethod
    def set_params(self, params: List[float]) -> None: ...
