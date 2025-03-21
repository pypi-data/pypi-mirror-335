from enum import Enum


class ContentGenerationRequestContextGrounding(str, Enum):
    EXISTING_INDEX = "Existing index"
    FILE_RESOURCE = "File resource"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
