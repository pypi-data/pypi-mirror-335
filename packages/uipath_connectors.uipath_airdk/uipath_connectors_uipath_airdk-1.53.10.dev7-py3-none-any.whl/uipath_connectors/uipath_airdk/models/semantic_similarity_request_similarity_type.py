from enum import Enum


class SemanticSimilarityRequestSimilarityType(str, Enum):
    LIST_OF_STRINGS = "List of strings"
    STRING_TO_STRING = "String to string"

    def __str__(self) -> str:
        return str(self.value)
