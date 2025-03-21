from enum import Enum


class GenerateEmailRequestSalutationString(str, Enum):
    DEAR = "Dear"
    GREETINGS = "Greetings"
    HELLO = "Hello"

    def __str__(self) -> str:
        return str(self.value)
