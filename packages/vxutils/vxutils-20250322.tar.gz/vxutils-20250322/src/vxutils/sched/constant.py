"""基础模块"""

import logging
import threading
from concurrent.futures import Future
from typing import Dict, Any, Optional, Union

from vxutils.sched.event import VXEvent, VXEventHandlers
from vxutils import VXContext, VXThreadPoolExecutor, VXTrigger, VXTaskItem

# 定义全局变量
CONTEXT: VXContext = VXContext()
STOPEVENT: threading.Event = threading.Event()
HANDLERS: VXEventHandlers = VXEventHandlers()
EXECUTOR: VXThreadPoolExecutor = VXThreadPoolExecutor()

# 定义特殊方法
register_handler = HANDLERS.register_handler
unregister_handler = HANDLERS.unregister_handler

# 定义特殊事件
# 初始化事件
ON_INIT_EVENT = "__init__"
ON_EXIT_EVENT = "__exit__"


def _handle_no_reply_event(ctx: VXContext, event: VXEvent) -> Any:
    """处理无回复事件"""
    handlers = HANDLERS[event.type]
    if not handlers:
        return

    for handler in handlers[1:]:
        task = VXTaskItem(handler, ctx, event)
        EXECUTOR.submit(task)

    handler = handlers[0]
    return handler(ctx, event)


def publish(
    event: Union[str, VXEvent],
    *,
    trigger: Optional[VXTrigger] = None,
    data: Optional[Dict[str, Any]] = None,
    channel: str = "default",
    priority: int = 10,
    reply_to: str = "",
) -> Future[Any]:
    """发布事件
    Args:
        event (Union[str, VXEvent]): 事件
        trigger (Optional[VXTrigger], optional): 触发器. Defaults to None.
        data (Optional[Dict[str, Any]], optional): 数据. Defaults to None.
        channel (str, optional): 频道. Defaults to "default".
        priority (int, optional): 优先级. Defaults to 10.
        reply_to (str, optional): 回复地址. Defaults to "".

    Returns:
        Future[Any]: 事件处理结果
    """
    if isinstance(event, str):
        event = VXEvent(
            type=event,
            data=data or dict(),
            priority=priority,
            channel=channel,
            reply_to=reply_to,
        )

    task = VXTaskItem(_handle_no_reply_event, CONTEXT, event)
    EXECUTOR.crontab(task, trigger=trigger)
    return task.future


def is_active() -> bool:
    """_summary_

    Returns:
        _description_
    """
    return not STOPEVENT.is_set()
