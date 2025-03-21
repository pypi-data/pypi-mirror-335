from enum import Enum
from json import JSONEncoder
from pathlib import Path
from typing import Any
from uuid import UUID


class CustomJSONEncoder(JSONEncoder):
    """
    A custom JSON encoder that extends the JSONEncoder class to handle additional
    data types, making them JSON-compatible.

    Features:
    - Handles custom objects with `to_json()` methods.
    - Serializes datetime objects to ISO 8601 format.
    - Converts `Path` objects to POSIX-style paths.
    - Serializes `bytes` and `bytearray` to hexadecimal strings.
    - Serializes `Enum` members using their values.
    - Allows passing a context for additional customization during encoding.

    Args:
        skipkeys (bool): Skip keys that are not of a basic type (str, int, float, bool, None).
        ensure_ascii (bool): Escape all non-ASCII characters.
        check_circular (bool): Check for circular references.
        allow_nan (bool): Allow NaN, Infinity, and -Infinity values.
        sort_keys (bool): Sort the output keys alphabetically.
        indent (int or None): Specify the number of spaces for indentation.
        separators (tuple or None): Custom separators for JSON encoding.
        default (callable or None): A function to handle unsupported types.
        context (dict or None): Optional context to provide additional parameters or information.

    Methods:
        default(data: Any) -> Any:
            Override the default serialization method to handle custom data types.
    """

    def __init__(self, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None, context=None):
        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
        )
        self.context = context  # Store the optional context for use during encoding

    def default(self, data) -> Any:
        """
        Override the default method to handle additional data types.

        Args:
            data (Any): The object to serialize.

        Returns:
            Any: A JSON-compatible representation of the object.

        Custom Behavior:
        - Objects with a `to_json()` method are serialized using that method.
        - Datetime objects are serialized to ISO 8601 strings.
        - Path objects are converted to their POSIX-style string representation.
        - Bytes and bytearrays are serialized as hexadecimal strings.
        - Enum members are serialized using their values.
        - Unsupported types fall back to the superclass implementation.
        """
        if hasattr(data, "to_json"):  # Support objects with a to_json() method
            return data.to_json()
        elif hasattr(data, "isoformat"):  # Serialize datetime objects to ISO 8601
            return data.isoformat()
        elif isinstance(data, Path):  # Convert Path objects to POSIX-style paths
            return data.as_posix()
        elif isinstance(data, (bytes, bytearray)):  # Serialize bytes to hexadecimal
            return data.hex()
        elif isinstance(data, Enum):  # Serialize Enum members by their values
            return data.value
        elif isinstance(data, UUID): # Support UUID type
            return data.hex
        else:  # Fallback to the superclass implementation
            return super().default(data)