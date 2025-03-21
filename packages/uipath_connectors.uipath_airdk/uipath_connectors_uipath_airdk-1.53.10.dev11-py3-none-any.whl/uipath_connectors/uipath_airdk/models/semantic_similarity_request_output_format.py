from enum import Enum


class SemanticSimilarityRequestOutputFormat(str, Enum):
    BEST_MATCH = "Best match"
    LIST_OF_SCORES = "List of scores"

    def __str__(self) -> str:
        return str(self.value)
