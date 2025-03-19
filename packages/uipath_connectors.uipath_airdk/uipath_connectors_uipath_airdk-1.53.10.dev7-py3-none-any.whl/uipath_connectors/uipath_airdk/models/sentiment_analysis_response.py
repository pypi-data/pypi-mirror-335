from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.sentiment_analysis_response_sentiment_analysis import (
    SentimentAnalysisResponseSentimentAnalysis,
)
from ..models.sentiment_analysis_response_usage import SentimentAnalysisResponseUsage


class SentimentAnalysisResponse(BaseModel):
    """
    Attributes:
        completion_tokens (Optional[int]): Indicates the count of tokens utilized to complete the analysis. Example:
                301.0.
        created (Optional[int]): The date and time when the analysis was performed. Example: 1.725272496E9.
        id (Optional[str]): A unique identifier for the sentiment analysis request. Example:
                chatcmpl-A2yTgC2UHbkfRAH5wKtYUCK4uQ0bM.
        method (Optional[str]): Specifies the HTTP method employed for the API call. Example: POST.
        model (Optional[str]): The model used for performing sentiment analysis. Example: gpt-4o-2024-05-13.
        object_ (Optional[str]): The text content that is being analyzed for sentiment. Example: chat.completion.
        prompt_tokens (Optional[int]): Tokens generated from the prompt used in sentiment analysis. Example: 577.0.
        sentiment_analysis (Optional[SentimentAnalysisResponseSentimentAnalysis]):
        total_tokens (Optional[int]): The total count of processed tokens in the text. Example: 878.0.
        usage (Optional[SentimentAnalysisResponseUsage]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    completion_tokens: Optional[int] = Field(alias="completionTokens", default=None)
    created: Optional[int] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    method: Optional[str] = Field(alias="method", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    object_: Optional[str] = Field(alias="object", default=None)
    prompt_tokens: Optional[int] = Field(alias="promptTokens", default=None)
    sentiment_analysis: Optional["SentimentAnalysisResponseSentimentAnalysis"] = Field(
        alias="sentimentAnalysis", default=None
    )
    total_tokens: Optional[int] = Field(alias="totalTokens", default=None)
    usage: Optional["SentimentAnalysisResponseUsage"] = Field(
        alias="usage", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SentimentAnalysisResponse"], src_dict: Dict[str, Any]):
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
