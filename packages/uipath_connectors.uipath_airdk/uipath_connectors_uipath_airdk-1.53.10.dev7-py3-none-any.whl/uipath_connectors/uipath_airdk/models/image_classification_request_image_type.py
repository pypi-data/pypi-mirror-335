from enum import Enum


class ImageClassificationRequestImageType(str, Enum):
    FILE = "File"
    PUBLIC_URL = "Public URL"

    def __str__(self) -> str:
        return str(self.value)
