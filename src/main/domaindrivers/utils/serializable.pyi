from typing import Any

class Serializable:
    def serialize(self) -> str: ...
    @classmethod
    def deserialize(cls, json_string: str) -> Any: ...
