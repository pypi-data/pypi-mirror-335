from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.context_grounding_search_response_search_result_array_array_item_ref import (
    ContextGroundingSearchResponseSearchResultArrayArrayItemRef,
)


class ContextGroundingSearchResponse(BaseModel):
    r"""
    Attributes:
        search_result (Optional[str]): The outcome of the search query. Example: [{"source":"List of Day Care Surgeries
                for Magma HDI GIC Ltd_f0834f2d174_1712824796337.pdf","content":"# List of Day Care Surgeries for Magma HDI GIC
                Ltd\n\n## CARDIOLOGY RELATED\n1 CORONARY ANGIOGRAPHY\n\n## CRITICAL CARE RELATED\n2 INSERT NON- TUNNEL CV
                CATH","page_number":"1"},{"source":"List of Day Care Surgeries for Magma HDI GIC
                Ltd_f0834f2d174_1712824796337.pdf","content":"```markdown\nList of Day Care Surgeries for Magma HDI GIC
                Ltd\n\nCARDIOLOGY RELATED\n1 CORONARY ANGIOGRAPHY","page_number":"1"}].
        search_result_array (Optional[list['ContextGroundingSearchResponseSearchResultArrayArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    search_result: Optional[str] = Field(alias="searchResult", default=None)
    search_result_array: Optional[
        list["ContextGroundingSearchResponseSearchResultArrayArrayItemRef"]
    ] = Field(alias="searchResultArray", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ContextGroundingSearchResponse"], src_dict: Dict[str, Any]
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
