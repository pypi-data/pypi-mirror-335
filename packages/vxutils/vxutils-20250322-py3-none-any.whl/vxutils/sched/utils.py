"""各类工具"""

import logging
import os
import json
from importlib import machinery, util
from pathlib import Path
from typing import Union, Any, Optional
from vxutils import VXContext


def load_modules(mod_path: Union[str, Path]) -> Any:
    """加载模块

    Arguments:
        mod_path -- 模块路径

    """
    mod_path = Path(mod_path)
    if not mod_path.exists():
        logging.warning(msg=f"{mod_path} is not exists")
        return

    logging.info("loading strategy dir: %s.", mod_path)
    logging.info("=" * 80)
    modules = os.listdir(mod_path)
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


def load_context(
    config_file: Union[str, Path],
    params_file: Union[str, Path],
    /,
    context: Optional[VXContext] = None,
) -> VXContext:
    """初始化context"""
    if context is None:
        context = VXContext()
    else:
        context.clear()

    context["config"] = {}
    context["params"] = {}

    with open(config_file, "r", encoding="utf-8") as fp:
        context["config"] = json.load(fp)
        logging.debug(
            "Load config file(%s) susscess... %s", config_file, context["config"]
        )

    with open(params_file, "r", encoding="utf-8") as fp:
        context["params"] = json.load(fp)
        logging.debug(
            "Load params file(%s) susscess... %s", params_file, context["params"]
        )
    return context
