from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Type

from ..models.translate_request_language import TranslateRequestLanguage


class TranslateRequest(BaseModel):
    """
    Attributes:
        input_text (str): Text to be translated. Example: हाल के युग में तकनीकी प्रगति का विशाल उत्साह देखने को मिल रहा
                है, और एक सुबह का सपना है कि आर्टिफिशियल इंटेलिजेंस अब हमारे दैनिक जीवन के हर क्षेत्र में गहराई से प्रवेश कर रही
                है। स्मार्टफोन से स्मार्ट होम, वर्चुअल रियलिटी से स्वयं चलने वाली गाड़ियों तक, एआई तकनीक हमारे जीवनशैली और काम
                के तरीके को बदल रही है। जबकि एआई कई सुविधाएँ और अवसर लाती है, वह कुछ चुनौतियों और समस्याओं को भी साथ में लाती
                है। हमें समाज पर एआई प्रौद्योगिकी के सकारात्मक प्रभाव को सुनिश्चित करने के लिए सतर्क रहना चाहिए।, रहना चाहिए।.
        language (TranslateRequestLanguage): Specify language to be translated to. Example: German.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    input_text: str = Field(alias="inputText")
    language: TranslateRequestLanguage = Field(alias="language")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["TranslateRequest"], src_dict: Dict[str, Any]):
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
