from enum import Enum


class WebSearchRequestProvider(str, Enum):
    GOOGLE_CUSTOM_SEARCH = "GoogleCustomSearch"

    def __str__(self) -> str:
        return str(self.value)
