from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class TranslateResponse(BaseModel):
    """
    Attributes:
        translated_text (Optional[str]): The translated text. Where supported, the output will be transliterated into
                the appropriate script or alphabet. Example: In der jüngsten Zeit wird eine immense Begeisterung für
                technologischen Fortschritt beobachtet, und es ist wie ein Morgentraum, dass künstliche Intelligenz nun tief in
                jeden Bereich unseres täglichen Lebens eindringt. Von Smartphones bis zu Smart Homes, von virtueller Realität
                bis zu selbstfahrenden Autos, die AI-Technologie verändert unsere Lebensweise und Art zu arbeiten. Während AI
                viele Annehmlichkeiten und Möglichkeiten mit sich bringt, bringt sie auch einige Herausforderungen und Probleme
                mit sich. Wir müssen wachsam bleiben, um den positiven Einfluss der AI-Technologie auf die Gesellschaft zu
                gewährleisten..
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    translated_text: Optional[str] = Field(alias="translatedText", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["TranslateResponse"], src_dict: Dict[str, Any]):
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
