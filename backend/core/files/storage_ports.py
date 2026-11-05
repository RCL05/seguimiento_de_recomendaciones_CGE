from typing import Protocol


class FileStorage(Protocol):
    def save(self, filename: str, content: bytes) -> str:
        ...

    def read(self, location: str) -> bytes:
        ...
