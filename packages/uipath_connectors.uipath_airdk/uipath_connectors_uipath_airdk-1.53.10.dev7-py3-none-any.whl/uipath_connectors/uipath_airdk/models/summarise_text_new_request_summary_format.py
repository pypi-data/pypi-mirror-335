from enum import Enum


class SummariseTextNewRequestSummaryFormat(str, Enum):
    BULLETED_LIST = "Bulleted list"
    CHRONOLOGICAL = "Chronological"
    NUMBERED_LIST = "Numbered list"
    OUTLINE = "Outline"
    PARAGRAPH = "Paragraph"
    TABULAR = "Tabular"

    def __str__(self) -> str:
        return str(self.value)
