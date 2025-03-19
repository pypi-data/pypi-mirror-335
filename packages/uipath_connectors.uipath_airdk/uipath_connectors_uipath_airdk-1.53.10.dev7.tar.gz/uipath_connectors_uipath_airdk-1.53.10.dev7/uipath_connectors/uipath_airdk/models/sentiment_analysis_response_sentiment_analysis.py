from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.sentiment_analysis_response_sentiment_analysis_sentiment_breakdown import (
    SentimentAnalysisResponseSentimentAnalysisSentimentBreakdown,
)
from ..models.sentiment_analysis_response_sentiment_analysis_overall_sentiment import (
    SentimentAnalysisResponseSentimentAnalysisOverallSentiment,
)


class SentimentAnalysisResponseSentimentAnalysis(BaseModel):
    """
    Attributes:
        analysis (Optional[str]): Detailed explanation of the sentiment analysis Example: The text contains a mix of
                positive and negative sentiments. The speaker feels lucky for not being at the office, indicating a positive
                sentiment towards their own situation. However, they also mention chaos in the office, which adds a negative
                sentiment about the office environment. The balance between these sentiments leans slightly towards the positive
                due to the speaker's personal relief..
        confidence_level (Optional[int]): The overall confidence level of the analysis Example: 80.0.
        key_phrases_str (Optional[list[str]]):  Example: {"phrase":"I am feeling lucky to have missed office
                today","sentiment":"Positive","confidence":0.9}.
        overall_sentiment (Optional[SentimentAnalysisResponseSentimentAnalysisOverallSentiment]):
        overall_sentiment_str (Optional[str]): Contains the sentiment score and label Example:
                {"score":33,"label":"Slightly Positive"}.
        sentiment_breakdown (Optional[SentimentAnalysisResponseSentimentAnalysisSentimentBreakdown]):
        sentiment_breakdown_str (Optional[str]): Counts of positive, negative, neutral, and total statements Example:
                {"positiveStatements":1,"negativeStatements":1,"neutralStatements":0,"totalStatements":2}.
        undertones_str (Optional[list[str]]):  Example: {"description":"Relief for missing a chaotic situation at
                work","impact":"The positive sentiment of relief is more dominant, contributing to an overall slightly positive
                score."}.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    analysis: Optional[str] = Field(alias="analysis", default=None)
    confidence_level: Optional[int] = Field(alias="confidenceLevel", default=None)
    key_phrases_str: Optional[list[str]] = Field(alias="keyPhrasesStr", default=None)
    overall_sentiment: Optional[
        "SentimentAnalysisResponseSentimentAnalysisOverallSentiment"
    ] = Field(alias="overallSentiment", default=None)
    overall_sentiment_str: Optional[str] = Field(
        alias="overallSentimentStr", default=None
    )
    sentiment_breakdown: Optional[
        "SentimentAnalysisResponseSentimentAnalysisSentimentBreakdown"
    ] = Field(alias="sentimentBreakdown", default=None)
    sentiment_breakdown_str: Optional[str] = Field(
        alias="sentimentBreakdownStr", default=None
    )
    undertones_str: Optional[list[str]] = Field(alias="undertonesStr", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SentimentAnalysisResponseSentimentAnalysis"],
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
