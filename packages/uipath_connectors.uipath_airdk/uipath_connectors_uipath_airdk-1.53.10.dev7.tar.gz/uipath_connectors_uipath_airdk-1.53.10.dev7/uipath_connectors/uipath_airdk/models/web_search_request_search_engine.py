from enum import Enum


class WebSearchRequestSearchEngine(str, Enum):
    GOOGLECUSTOMSEARCH = "GoogleCustomSearch"

    def __str__(self) -> str:
        return str(self.value)
