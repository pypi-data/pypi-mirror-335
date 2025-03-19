from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class RewriteResponse(BaseModel):
    """
    Attributes:
        rewritten_content (Optional[str]): The final rewritten version of the original content. Example: प्रोटोकॉल
                बफर्स, जिसे प्रोटोबफ भी कहा जाता है, एक ऐसी तकनीक है जो डेटा को संरचित और संक्षिप्त रूप में सहेजती है। गूगल
                द्वारा विकसित, यह उनकी आंतरिक सेवाओं में संचार और डेटा संग्रहण के लिए खूब इस्तेमाल होती है। यह भाषा और मंच की
                सीमाओं से परे है और इसे विस्तारित किया जा सकता है। इसकी मुख्य विशेषताएं हैं: भाषा स्वतंत्रता, दक्षता,
                विस्तारशीलता और क्रॉस-प्लेटफॉर्म समर्थन। यह आपको विभिन्न प्रोग्रामिंग भाषाओं में डेटा को आसानी से संग्रहित और
                पुनर्प्राप्त करने की सुविधा देता है।.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    rewritten_content: Optional[str] = Field(alias="rewrittenContent", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["RewriteResponse"], src_dict: Dict[str, Any]):
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
