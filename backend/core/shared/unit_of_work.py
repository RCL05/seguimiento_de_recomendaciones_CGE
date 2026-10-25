from contextlib import AbstractContextManager
from typing import Protocol, TypeVar


T = TypeVar("T")


class UnitOfWork(Protocol):
    """Port used by application services to group changes atomically."""

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc_value, traceback) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class InMemoryUnitOfWork(AbstractContextManager):
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
