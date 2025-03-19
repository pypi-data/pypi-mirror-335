from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class SemanticSimilarityResponseSemanticSimilarity(BaseModel):
    """
    Attributes:
        list_of_scores (Optional[str]): A list containing similarity scores for multiple comparisons (only for list of
                score). Example: [{"string":"Machine learning is transforming multiple
                sectors.","similarityScore":0.85,"similarityExplanation":"High similarity due to shared context and intent. Both
                sentences discuss the impact of advanced technologies (AI and machine learning) on various industries or
                sectors. The key concepts of technological transformation and industry impact are present in both. The
                vocabulary differs slightly but conveys a similar theme."},{"string":"Traditional methods are becoming
                obsolete.","similarityScore":0.4,"similarityExplanation":"Moderate similarity. While the primary string
                discusses the positive impact of AI on industries, this comparison string implies a negative consequence
                (obsolescence of traditional methods) which can be indirectly related to the rise of AI. The context of
                technological change is present, but the intent and sentiment differ."},{"string":"AI applications are limited
                to tech companies.","similarityScore":0.6,"similarityExplanation":"Moderate to high similarity. Both sentences
                discuss AI, but the primary string emphasizes its broad impact across various industries, while the comparison
                string suggests a limitation to tech companies. The key concept of AI is shared, but the scope and sentiment
                differ, with the comparison string presenting a more restricted view."}].
        similarity_explanation (Optional[str]): Provides an explanation of the semantic similarity result (only for
                string to string or best match).
        similarity_score (Optional[float]): The calculated score representing the semantic similarity (only for string
                to string or best match). Example: 0.3.
        string (Optional[str]): Best match string out of the provided comparison array (only for best match).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    list_of_scores: Optional[str] = Field(alias="listOfScores", default=None)
    similarity_explanation: Optional[str] = Field(
        alias="similarityExplanation", default=None
    )
    similarity_score: Optional[float] = Field(alias="similarityScore", default=None)
    string: Optional[str] = Field(alias="string", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SemanticSimilarityResponseSemanticSimilarity"],
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
