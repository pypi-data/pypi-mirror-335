"""事件基类"""

import logging
import uuid
from typing import Any, Dict, Optional, Callable, List
from collections import defaultdict
from pydantic import Field
from vxutils import VXDataModel, VXContext


class VXEvent(VXDataModel):
    """事件类"""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    type: str = ""
    data: Dict[str, Any] = Field(default_factory=dict, frozen=True)
    priority: int = 10
    channel: str = "default"
    reply_to: str = ""

    def __lt__(self, other: "VXEvent") -> bool:
        return (-self.priority, hash(id)) < (-other.priority, hash(other.id))


class VXEventHandlers:
    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[VXContext, VXEvent], Any]] = defaultdict(
            list
        )

    def __getitem__(self, event_type: str) -> List[Callable[[VXContext, VXEvent], Any]]:
        return self._handlers[event_type]

    def __contains__(self, event_type: str) -> bool:
        return event_type in self._handlers

    def register_handler(
        self,
        event_type: str,
    ) -> Callable[[Callable[[VXContext, VXEvent], Any]], Any]:
        def wrapper(
            handler: Callable[[VXContext, VXEvent], Any],
        ) -> Callable[[VXContext, VXEvent], Any]:
            self._handlers[event_type].append(handler)
            logging.warning("Register event handler: %s -> %s", event_type, handler)
            return handler

        return wrapper

    def unregister_handler(
        self,
        event_type: str,
        handler: Optional[Callable[[VXContext, VXEvent], Any]] = None,
    ) -> None:
        """注销事件处理函数

        Arguments:
            event_type {str} -- 事件类型

        Keyword Arguments:
            handler {Optional[Callable[[VXContext, VXEvent], Any]]} -- 事件处理函数 (default: {None})
        """
        if not handler:
            self._handlers.pop(event_type, [])
        elif handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logging.warning("Unregister event handler: %s -> %s", event_type, handler)


if __name__ == "__main__":
    handlers = VXEventHandlers()

    @handlers.register_handler("test")
    def test(ctx: VXContext, event: VXEvent):
        print(event)

    print(test)

    print(handlers._handlers)
