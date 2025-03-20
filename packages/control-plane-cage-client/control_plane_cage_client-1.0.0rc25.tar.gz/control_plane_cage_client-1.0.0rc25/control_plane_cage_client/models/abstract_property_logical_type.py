from enum import Enum


class AbstractPropertyLogicalType(str, Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    DATE = "date"
    INTEGER = "integer"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
