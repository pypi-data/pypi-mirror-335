"""调度器服务器"""

import os
import logging
import json
import signal
import threading
from pathlib import Path
from argparse import ArgumentParser, Namespace
from contextlib import suppress
from vxutils.sched.constant import (
    CONTEXT,
    HANDLERS,
    STOPEVENT,
    EXECUTOR,
    ON_INIT_EVENT,
    ON_EXIT_EVENT,
    publish,
)
from vxutils.sched.utils import load_context, load_modules
from vxutils import VXJSONEncoder, loggerConfig, VXContext, to_json


def init(args: Namespace) -> None:
    """初始化模块

    Arguments:
        args {Namespace} -- 命令行
    """
    target = Path(args.target)
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)

    for sub_dir in ["etc", "log", "mod", "data"]:
        sub_path = target / sub_dir
        if not sub_path.exists():
            sub_path.mkdir(parents=True, exist_ok=True)
            logging.error("Create %s success...", sub_path.absolute())
        else:
            logging.warning("%s already exists...", sub_path.absolute())

    with open(target / "etc/config.json", "w", encoding="utf-8") as fp:
        json.dump({}, fp, cls=VXJSONEncoder, indent=4)
        logging.error("Create %s success...", (target / "etc/config.json").absolute())


def run(args: Namespace) -> None:
    """运行服务器

    Arguments:
        args {Namespace} -- 命令行
    """

    if args is None:
        args = Namespace(config="etc/config.json", mod="mod", log="log/message.log")

    loglevel = logging.DEBUG if args.verbose else logging.INFO
    loggerConfig(level=loglevel, filename=args.log)
    load_context(args.config, args.params, context=CONTEXT)
    STOPEVENT.clear()
    if args.mod:
        load_modules(args.mod)

    # 提交初始
    try:
        start(CONTEXT)
        STOPEVENT.wait()
    except KeyboardInterrupt:
        stop()
        logging.info("Stop scheduler success...")


def stop(*args) -> None:
    """停止服务器"""
    if STOPEVENT.is_set():
        return
    try:
        publish(ON_EXIT_EVENT)
        STOPEVENT.set()
        EXECUTOR.shutdown(wait=True)
        with open("data/params.json", "w", encoding="utf-8") as f:
            json.dump(CONTEXT.params, cls=VXJSONEncoder, indent=4, fp=f)
            logging.info("Save params to: %s", Path("data/params.json").absolute())
            logging.debug("Params : %s", to_json(CONTEXT.params))
    except Exception as err:
        logging.error("Save params Failed: %s, %s", err, CONTEXT.params)
    finally:
        logging.info("========== Scheduler is stopped... ==========")
        os._exit(0)


def start(context: VXContext) -> None:
    """启动服务器
    Arguments:
        context {VXContext} -- 上下文
    """
    # 重置停止事件
    STOPEVENT.clear()
    logging.info("========== Scheduler is started... ==========")
    # 提交初始化任务
    try:
        if ON_INIT_EVENT in HANDLERS:
            logging.info("========== Scheduler starting Init Event... ==========")
            fu = publish(ON_INIT_EVENT)
            with suppress(TimeoutError):
                fu.result(timeout=5)

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, stop)
        logging.info(
            "========== Scheduler starting success... press `Ctrl+C` to exit... =========="
        )

    except Exception as err:
        logging.error("[Scheduler] Runtime Error...%s", err, exc_info=True)


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
        "-p", "--params", type=str, default="data/params.json", help="Params File"
    )
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
