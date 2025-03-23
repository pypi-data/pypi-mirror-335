"""上下文管理器"""

from typing import Any, OrderedDict
from vxutils.convertors import to_json


__all__ = ["VXContext"]


class VXContext(OrderedDict[str, Any]):
    """上下文管理器"""

    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        del self[name]

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} (id-{id(self)}): {to_json(self)} >"

    def __hash__(self) -> int:  # type: ignore[override]
        json_str = to_json(self, sort_keys=True)
        return hash(json_str)
