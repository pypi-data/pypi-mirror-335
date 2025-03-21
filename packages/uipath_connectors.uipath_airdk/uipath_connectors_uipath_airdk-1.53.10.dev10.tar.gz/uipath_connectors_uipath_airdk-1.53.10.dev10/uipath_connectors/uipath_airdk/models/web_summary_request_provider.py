from enum import Enum


class WebSummaryRequestProvider(str, Enum):
    PERPLEXITY = "Perplexity"

    def __str__(self) -> str:
        return str(self.value)
