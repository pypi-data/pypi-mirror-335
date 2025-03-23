"""scheduler module"""

import signal
from importlib import machinery, util
import logging
import os
import time
import uuid
import json
from pathlib import Path
from argparse import ArgumentParser, Namespace
from contextlib import suppress
from typing import Any, List, Optional, Dict, Callable, Union
import threading
from concurrent.futures import Future
from pydantic import Field
from vxutils import VXJSONEncoder, to_json
from vxutils.context import VXContext
from vxutils.logger import loggerConfig
from vxutils.executor import VXTaskItem, async_task, VXTrigger
from vxutils.datamodel.core import VXDataModel


ON_INIT_EVENT = "__init__"
ON_REPLY_EVENT = "__reply__"
ON_TASK_COMPLETE_EVENT = "__task_complete__"
ON_EXIT_EVENT = "__exit__"


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


__handlers__: Dict[str, List[Callable[[VXContext, VXEvent], Any]]] = {}


def register_handler(
    event_type: str,
) -> Callable[[Callable[[VXContext, VXEvent], Any]], Any]:
    """注册事件处理函数

    Arguments:
        event_type {str} -- 事件类型

    Returns:
        Callable[[Callable[[VXContext, VXEvent], Any]], None] -- 事件处理函数
    """
    # global __handlers__
    if event_type not in __handlers__:
        __handlers__[event_type] = []

    def wrapper(
        handler: Callable[[VXContext, VXEvent], Any],
    ) -> Callable[[VXContext, VXEvent], Any]:
        __handlers__[event_type].append(handler)
        logging.warning("Register event handler: %s -> %s", event_type, handler)
        return handler

    return wrapper


def unregister_handler(
    event_type: str, handler: Optional[Callable[[VXContext, VXEvent], Any]] = None
) -> None:
    """注销事件处理函数

    Arguments:
        event_type {str} -- 事件类型

    Keyword Arguments:
        handler {Optional[Callable[[VXContext, VXEvent], Any]]} -- 事件处理函数 (default: {None})
    """
    # global __handlers__
    if not handler:
        __handlers__.pop(event_type, [])
    elif handler in __handlers__[event_type]:
        __handlers__[event_type].remove(handler)
        # logging.warning(f"Unregister event handler: {event_type} -> {handler}")
        logging.warning("Unregister event handler: %s -> %s", event_type, handler)


__default_config__: Dict[str, Any] = {
    "daily": {"on_settle": {"timestr": "00:00:00"}},
    "every": {"on_second": {"interval": 1}},
}
__context__: VXContext = VXContext()
__context__["config"] = {}
__context__["params"] = {}

__ACTIVE__: bool = False
__ACTIVE__: threading.Event = threading.Event()


def _handle_no_reply_event(context: VXContext, event: VXEvent) -> List[Future[Any]]:
    #    global __handlers__, __ACTIVE__

    fus: List[Future[Any]] = []
    try:
        handlers = __handlers__.get(event.type, [])
        logging.debug("Event handler: %s -> %s", event.type, handlers)

        for handler in handlers:
            task = VXTaskItem(handler, context, event)
            async_task.__executor__.apply(task)
            fus.append(task.future)

    except Exception as err:
        logging.error(
            "Event handler error: %s -> %s, %s",
            event.type,
            handlers,
            err,
            exc_info=True,
        )

    return fus


class VXPublisher:
    """发布器"""

    # def __init__(self, context: VXContext) -> None:
    #    self._context = context

    def __call__(
        self,
        event: Union[str, VXEvent],
        *,
        trigger: Optional[VXTrigger] = None,
        data: Optional[Dict[str, Any]] = None,
        channel: str = "default",
        priority: int = 10,
        reply_to: str = "",
    ) -> Future[Any]:
        """发布事件"""

        if __ACTIVE__ is False:
            raise RuntimeError("Scheduler is not active.")

        if isinstance(event, str):
            event = VXEvent(
                type=event,
                data=data or {},
                channel=channel,
                priority=priority,
                reply_to=reply_to,
            )
        if reply_to == "":
            task = VXTaskItem(
                _handle_no_reply_event, context=self._context, event=event
            )
        else:
            task = VXTaskItem(_handle_reply_event, context=self._context, event=event)
        return async_task.__executor__.apply(task=task, trigger=trigger)


publish = VXPublisher()


def load_modules(mod_path: Union[str, Path]) -> Any:
    """加载策略目录"""
    if not os.path.exists(mod_path):
        logging.warning(msg=f"{mod_path} is not exists")
        return

    modules = os.listdir(mod_path)
    logging.info("loading strategy dir: %s.", mod_path)
    logging.info("=" * 80)
    for mod in modules:
        if (not mod.startswith("__")) and mod.endswith(".py"):
            try:
                loader = machinery.SourceFileLoader(mod, os.path.join(mod_path, mod))
                spec = util.spec_from_loader(loader.name, loader)
                if spec is None:
                    logging.error("Load Module: %s Failed.", mod)
                    continue

                strategy_mod = util.module_from_spec(spec)
                loader.exec_module(strategy_mod)
                logging.info("Load Module: %s Sucess.", strategy_mod)
                logging.info("+" * 80)
            except Exception as err:
                logging.error("Load Module: %s Failed. %s", mod, err, exc_info=True)
                logging.error("-" * 80)


def __quit_sched__(*args: Any) -> None:
    """退出调度器"""
    try:
        stop()
    except Exception:
        os._exit(0)


def init(args: Namespace) -> None:
    """初始化模块"""

    loggerConfig(force=True)
    target = Path(args.target).absolute()
    logging.info("初始化模块: %s", target)

    for d in [
        "mod",
        "etc",
        "data",
        "log",
    ]:
        if (target / d).exists():
            logging.warning("Target DIR is: %s", target / d)
        else:
            (target / d).mkdir(parents=True)
            logging.info("Create DIR: %s", target / d)

    if not (target / "etc/default_config.json").exists():
        with open(target / "etc/default_config.json", "w", encoding="utf-8") as f:
            json.dump(__default_config__, f, indent=4)
            logging.info(
                "Create Default Config File: %s", target / "etc/default_config.json"
            )

    if not (target / "data/params.json").exists():
        with open(target / "data/params.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
            logging.info("Create Empty Params File: %s", target / "data/params.json")


def is_active() -> bool:
    """是否激活"""
    return __ACTIVE__.is_set()


def load_context(
    config_file: Union[str, Path] = "etc/config.json",
    params_file: Union[str, Path] = "data/params.json",
) -> None:
    """加载context

    Keyword Arguments:
        config_file {Union[str, Path]} -- 配置文件 (default: {"etc/config.json"})
        params_file {Union[str, Path]} -- 参数文件 (default: {"data/params.json"})
    """
    config_file = Path(config_file)
    params_file = Path(params_file)

    __context__.clear()
    __context__.config = {}
    __context__.params = {}

    if not config_file.exists():
        logging.warning("Config file(%s) is not exists.", config_file)

    else:
        try:
            with open(config_file, "r", encoding="utf-8") as fp:
                config = json.load(fp)
            __context__["config"] = config
            logging.debug("Config file(config_file) load: %s", to_json(config))
        except Exception as e:
            logging.error("Load config file error: %s", e)

    if not params_file.exists():
        logging.warning("Params file(%s) is not exists.", params_file)
    else:
        try:
            with open(params_file, "r", encoding="utf-8") as fp:
                params = json.load(fp)
            __context__["params"] = params
            logging.debug("Params file(%s) load: %s", params_file, to_json(params))

        except json.JSONDecodeError as e:
            logging.error("Load params file error: %s", e)


def start(mod: Optional[Union[str, Path]] = None) -> None:
    """启动调度起"""

    global __context__, __handlers__, __ACTIVE__
    if __ACTIVE__.is_set():
        return

    # if __ACTIVE__ is True:
    #    return

    logging.info("========== Scheduler is started... ==========")

    if mod:
        mod_path = Path(mod)
        if not mod_path.parent.exists():
            mod_path.mkdir(parents=True, exist_ok=True)
        load_modules(mod_path=mod)

    try:
        __ACTIVE__.set()
        if ON_INIT_EVENT in __handlers__:
            logging.info("========== Scheduler starting Init Event... ==========")
            fu = publish(ON_INIT_EVENT)
            with suppress(TimeoutError):
                fu.result(timeout=5)

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, __quit_sched__)
        logging.info(
            "========== Scheduler starting success... press `Ctrl+C` to exit... =========="
        )

    except Exception as err:
        logging.error("[Scheduler] Runtime Error...%s", err, exc_info=True)
        stop()


def stop() -> None:
    """暂停调度器"""

    global __context__, __handlers__, __ACTIVE__
    if not __ACTIVE__.is_set():
        return

    # if __ACTIVE__ is False:
    #    return

    try:
        # __ACTIVE__ = False
        __ACTIVE__.clear()
        with open("data/params.json", "w", encoding="utf-8") as f:
            json.dump(__context__.params, f, indent=4, cls=VXJSONEncoder)
            logging.info("Save params to: %s", Path("data/params.json").absolute())
            logging.debug("Params : %s", to_json(__context__.params))
    except Exception as err:
        logging.error("Save params Failed: %s, %s", err, __context__.params)
    finally:
        if ON_EXIT_EVENT in __handlers__:
            publish(ON_EXIT_EVENT)
        async_task.__executor__.shutdown(wait=True)
        __context__.clear()
        logging.info("========== Scheduler is stopped... ==========")


def run(args: Optional[Namespace] = None) -> None:
    global __context__, __handlers__, __ACTIVE__

    if args is None:
        args = Namespace(
            config="etc/config.json", mod="mod", log="log/message.log", verbose=False
        )

    log_level = "DEBUG" if args.verbose else "INFO"
    log_file = args.log if args.log else ""
    if args.log:
        log_file = Path(args.log).absolute()
        if log_file.is_dir():
            log_file = log_file / "vxsched.log"

        if not log_file.parent.exists():
            log_file.parent.mkdir(parents=True)

    loggerConfig(level=log_level, filename=log_file, force=True)

    try:
        load_context(config_file=args.config)
        start(mod=args.mod)
        __ACTIVE__.wait()

    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error("[Scheduler] Runtime Error...%s", err, exc_info=True)
    finally:
        stop()


def main() -> None:
    """主函数"""

    parser = ArgumentParser(description="vxsched: a event driven scheduler")
    subparser = parser.add_subparsers(description="run subcommand")

    # 初始化模块
    init_parser = subparser.add_parser("init", help="init module")
    init_parser.add_argument("target", type=str, default=".", help="Target DIR")
    init_parser.set_defaults(func=init)

    # 运行策略模块
    run_parser = subparser.add_parser("run", help="run scheduler")
    run_parser.add_argument(
        "-c", "--config", default="etc/config.json", help="Config File"
    )
    run_parser.add_argument("-m", "--mod", type=str, default="mod", help="Module DIR")
    run_parser.add_argument(
        "-l", "--log", type=str, default="log/message.log", help="Log File"
    )
    run_parser.add_argument(
        "-v", "--verbose", default=False, help="Debug Mode", action="store_true"
    )
    run_parser.set_defaults(func=run)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
