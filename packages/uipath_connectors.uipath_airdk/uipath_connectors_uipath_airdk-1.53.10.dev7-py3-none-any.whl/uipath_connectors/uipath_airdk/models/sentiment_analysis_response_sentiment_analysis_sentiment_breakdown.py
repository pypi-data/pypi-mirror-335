from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class SentimentAnalysisResponseSentimentAnalysisSentimentBreakdown(BaseModel):
    """
    Attributes:
        negative_statements (Optional[int]): The number of statements identified as negative. Example: 1.0.
        neutral_statements (Optional[int]): The number of statements classified as neutral. Example: 0.0.
        positive_statements (Optional[int]): Provides an array of statements identified as positive. Example: 1.0.
        total_statements (Optional[int]): The total count of statements evaluated for sentiment analysis. Example: 2.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    negative_statements: Optional[int] = Field(alias="negativeStatements", default=None)
    neutral_statements: Optional[int] = Field(alias="neutralStatements", default=None)
    positive_statements: Optional[int] = Field(alias="positiveStatements", default=None)
    total_statements: Optional[int] = Field(alias="totalStatements", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SentimentAnalysisResponseSentimentAnalysisSentimentBreakdown"],
        src_dict: Dict[str, Any],
    ):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
