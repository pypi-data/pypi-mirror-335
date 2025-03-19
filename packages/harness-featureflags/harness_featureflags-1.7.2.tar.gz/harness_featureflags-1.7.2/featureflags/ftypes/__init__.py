from .boolean import Boolean
from .integer import Integer
from .json import JSON
from .number import Number
from .string import String

TYPES: dict = {
    bool: Boolean,
    str: String,
    int: Integer,
    float: Number,
    dict: JSON
}
