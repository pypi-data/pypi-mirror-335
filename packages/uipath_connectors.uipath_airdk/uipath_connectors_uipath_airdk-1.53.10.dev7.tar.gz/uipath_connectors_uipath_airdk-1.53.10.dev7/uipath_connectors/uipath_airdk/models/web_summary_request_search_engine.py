from enum import Enum


class WebSummaryRequestSearchEngine(str, Enum):
    PERPLEXITY = "Perplexity"

    def __str__(self) -> str:
        return str(self.value)
