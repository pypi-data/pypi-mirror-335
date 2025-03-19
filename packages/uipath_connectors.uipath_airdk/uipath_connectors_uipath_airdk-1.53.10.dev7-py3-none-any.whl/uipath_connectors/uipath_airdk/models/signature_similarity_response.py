from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.signature_similarity_response_usage import (
    SignatureSimilarityResponseUsage,
)


class SignatureSimilarityResponse(BaseModel):
    """
    Attributes:
        completion_tokens (Optional[int]): The number of tokens used to complete the analysis. Example: 150.0.
        created (Optional[int]): The date and time when the analysis was performed. Example: 1.72542702E9.
        id (Optional[str]): The unique identifier of the API request. Example: chatcmpl-A3cg08k2zVTkMu7v68WWLaxmq9qLu.
        model (Optional[str]): The unique identifier of the AI model used. Example: gpt-4o-2024-05-13.
        object_ (Optional[str]): The detailed information of the object analyzed for similarity. Example:
                chat.completion.
        prompt_tokens (Optional[int]): The number of tokens used in the input prompt. Example: 1798.0.
        reasoning (Optional[str]): The explanation of how the conclusion was reached Example: Both images contain
                signatures. The overall appearance of the two signatures, including size, slant, and spacing, matches closely.
                Specific characteristics such as line quality appear consistent, with smooth and slightly variable pressure. The
                speed seems to be fast and steady in both signatures. The formation and proportion of letters, especially in 'P'
                and 'esch' parts, are similar, with minor variations in beginning and ending strokes, which are normal. The
                connections between letters and the unique identifiers align well in both signatures..
        score (Optional[str]): A score between 0 and 100 indicating the similarity of the signatures Example: 85.
        total_tokens (Optional[int]): The total number of tokens processed in the request. Example: 1948.0.
        usage (Optional[SignatureSimilarityResponseUsage]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    completion_tokens: Optional[int] = Field(alias="completionTokens", default=None)
    created: Optional[int] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    object_: Optional[str] = Field(alias="object", default=None)
    prompt_tokens: Optional[int] = Field(alias="promptTokens", default=None)
    reasoning: Optional[str] = Field(alias="reasoning", default=None)
    score: Optional[str] = Field(alias="score", default=None)
    total_tokens: Optional[int] = Field(alias="totalTokens", default=None)
    usage: Optional["SignatureSimilarityResponseUsage"] = Field(
        alias="usage", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SignatureSimilarityResponse"], src_dict: Dict[str, Any]):
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
