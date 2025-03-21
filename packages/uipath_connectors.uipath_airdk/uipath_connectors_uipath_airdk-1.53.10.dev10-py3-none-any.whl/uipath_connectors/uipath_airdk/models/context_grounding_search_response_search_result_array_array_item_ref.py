from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ContextGroundingSearchResponseSearchResultArrayArrayItemRef(BaseModel):
    """
    Attributes:
        content (Optional[str]): The content of each item in the search results. Example: # List of Day Care Surgeries
                for Magma HDI GIC Ltd

                ## CARDIOLOGY RELATED
                1 CORONARY ANGIOGRAPHY

                ## CRITICAL CARE RELATED
                2 INSERT NON- TUNNEL CV CATH.
        page_number (Optional[str]): The page number where the search result is found. Example: 1.
        source (Optional[str]): Indicates the origin of the search result. Example: List of Day Care Surgeries for Magma
                HDI GIC Ltd_f0834f2d174_1712824796337.pdf.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)
    page_number: Optional[str] = Field(alias="page_number", default=None)
    source: Optional[str] = Field(alias="source", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ContextGroundingSearchResponseSearchResultArrayArrayItemRef"],
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
