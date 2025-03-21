from enum import Enum


class WebReaderRequestProvider(str, Enum):
    JINA = "Jina"

    def __str__(self) -> str:
        return str(self.value)
