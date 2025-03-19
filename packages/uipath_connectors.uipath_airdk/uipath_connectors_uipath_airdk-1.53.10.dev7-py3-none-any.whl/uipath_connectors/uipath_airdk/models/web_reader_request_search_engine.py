from enum import Enum


class WebReaderRequestSearchEngine(str, Enum):
    JINA = "Jina"

    def __str__(self) -> str:
        return str(self.value)
