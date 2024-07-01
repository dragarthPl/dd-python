from typing import Any, cast

import jsonpickle


class Serializable:
    def serialize(self: Any) -> str:
        return cast(str, jsonpickle.encode(self))

    @classmethod
    def deserialize(cls, json_string: str) -> Any:
        return jsonpickle.decode(json_string)
