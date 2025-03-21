from enum import Enum


class ImageAnalysisRequestImageType(str, Enum):
    FILE = "File"
    PUBLIC_URL = "Public URL"

    def __str__(self) -> str:
        return str(self.value)
