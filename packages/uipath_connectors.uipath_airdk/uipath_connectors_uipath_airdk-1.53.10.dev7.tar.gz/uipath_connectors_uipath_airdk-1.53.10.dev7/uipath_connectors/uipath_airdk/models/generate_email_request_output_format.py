from enum import Enum


class GenerateEmailRequestOutputFormat(str, Enum):
    HTML = "HTML"
    PLAIN_TEXT = "Plain text"

    def __str__(self) -> str:
        return str(self.value)
