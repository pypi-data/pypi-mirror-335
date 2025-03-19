from abc import ABC, abstractmethod
from types import TracebackType


class UnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Enter the Unit of Work, and return its value."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Handle termination of the Unit of Work."""
