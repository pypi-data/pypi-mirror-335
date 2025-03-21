from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ContextGroundingSearchRequestQuery(BaseModel):
    """
    Attributes:
        query (str): Text used to query the index or file and return similar context Example: List of Day Care Surgeries
                for Magma HDI GIC Ltd.
        number_of_results (Optional[int]): The total number of results returned by the query Default: 3. Example: 3.0.
        threshold (Optional[float]): The minimum relevance score for search results Default: 0.75. Example: 0.85.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    query: str = Field(alias="query")
    number_of_results: Optional[int] = Field(alias="numberOfResults", default=3)
    threshold: Optional[float] = Field(alias="threshold", default=0.75)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ContextGroundingSearchRequestQuery"], src_dict: Dict[str, Any]
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
