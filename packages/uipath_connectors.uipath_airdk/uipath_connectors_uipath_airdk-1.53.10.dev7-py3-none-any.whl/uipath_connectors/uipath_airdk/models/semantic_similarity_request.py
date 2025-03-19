from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.semantic_similarity_request_output_format import (
    SemanticSimilarityRequestOutputFormat,
)
from ..models.semantic_similarity_request_similarity_type import (
    SemanticSimilarityRequestSimilarityType,
)


class SemanticSimilarityRequest(BaseModel):
    """
    Attributes:
        first_comparison_input (str): The first string of text for calculating similarity. Example: Artificial
                intelligence is revolutionizing various industries..
        second_comparison_input (str): The second string of text for calculating similarity. Example: AI applications
                are limited to tech companies..
        similarity_type (SemanticSimilarityRequestSimilarityType): The type of similarity which can either be a string
                to string comparison or a string to a list of strings. Example: String to string.
        comparison_array (Optional[str]): Array of strings to compare first input against for matching. Example:
                ["Machine learning is transforming multiple sectors.", "Traditional methods are becoming obsolete.", "AI
                applications are limited to tech companies."].
        output_format (Optional[SemanticSimilarityRequestOutputFormat]): If  'best match’ is selected for similarity
                type, the output will be the most likely match.  If list of scores is selected, the output will assign a
                similarity score for for the whole list of outputs. Example: Best match.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    first_comparison_input: str = Field(alias="firstComparisonInput")
    second_comparison_input: str = Field(alias="secondComparisonInput")
    similarity_type: SemanticSimilarityRequestSimilarityType = Field(
        alias="similarityType"
    )
    comparison_array: Optional[str] = Field(alias="comparisonArray", default=None)
    output_format: Optional[SemanticSimilarityRequestOutputFormat] = Field(
        alias="outputFormat", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SemanticSimilarityRequest"], src_dict: Dict[str, Any]):
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
