from enum import Enum


class GenerateEmailRequestStyle(str, Enum):
    CONCISE = "Concise"
    ELOQUENT = "Eloquent"
    ENGAGING = "Engaging"
    EVOCATIVE = "Evocative"
    FLUID = "Fluid"
    LYRICAL = "Lyrical"
    PERSUASIVE = "Persuasive"
    SOPHISTICATED = "Sophisticated"
    VIVID = "Vivid"
    WITTY = "Witty"

    def __str__(self) -> str:
        return str(self.value)
