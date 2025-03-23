"""api工具箱"""

import abc
import sys
import logging
import importlib
import json
from pathlib import Path
from typing import Union, Dict, Any, Optional, List
from multiprocessing import Lock
from pydantic import TypeAdapter, ValidationError

try:
    from typing_extensions import TypedDict, NotRequired
except ImportError:
    from typing import TypedDict, NotRequired  # type: ignore[attr-defined, no-redef]

# from typing_extensions import TypedDict
from vxutils import VXContext


class ProviderConfig(TypedDict):
    """供应商配置"""

    mod_path: str
    params: NotRequired[Dict[str, Any]]


ProviderConfigAdapter = TypeAdapter(ProviderConfig)


def import_tools(mod_path: Union[str, Path, Any], **params: Any) -> Any:
    """导入工具"""

    if params is None:
        params = {}

    cls_or_obj = mod_path
    if isinstance(mod_path, str):
        if mod_path.find(".") > -1:
            mod_name = mod_path.split(".")[-1]
            class_path = ".".join(mod_path.split(".")[:-1])
            mod = importlib.import_module(class_path)
            cls_or_obj = getattr(mod, mod_name)
        else:
            cls_or_obj = importlib.import_module(mod_path)

    return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj


def import_by_config(config: ProviderConfig) -> Any:
    """根据配置文件初始化对象

    配置文件格式:
    config = {
        'mod_path': 'vxsched.vxEvent',
        'params': {
            "type": "helloworld",
            "data": {
                'mod_path': 'vxutils.vxtime',
            },
            "trigger": {
                "mod_path": "vxsched.triggers.vxIntervalTrigger",
                "params":{
                    "interval": 10
                }
            }
        }
    }

    """
    if not isinstance(config, dict):
        return config

    if "mod_path" not in config:
        return config

    mod_path = config["mod_path"]
    params = {}
    if "params" in config and isinstance(config["params"], dict):
        for k, v in config["params"].items():
            try:
                v = ProviderConfigAdapter.validate_python(v)
                params[k] = import_by_config(v)
            except ValidationError:
                params[k] = v

    return import_tools(mod_path, **params)


class AbstractProvider(abc.ABC):
    """接口基类"""

    @abc.abstractmethod
    def start_up(self, context: VXContext, provider_config: ProviderConfig) -> None:
        """启动接口

        Arguments:
            context {VXContext} -- 上下文
        """
        raise NotImplementedError

    def tear_down(self) -> None:
        """关闭接口"""
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class VXInitProvider(AbstractProvider):
    """初始化接口"""


class AbstractProviderCollection(abc.ABC):
    """接口集合基类

    {
        "current": {
            "mod_path": "xxx.xxx",
            "params": {
                "token": "xxxx"
            }
        }",
        "daily_bar": {
            "mod_path": "xxx.xxx",
            "params": {
                "token": "@current"
            }
        }
    }
    """

    def __init__(self, context: Optional[VXContext] = None, **kwargs: Any) -> None:
        self._init_providers: List[VXInitProvider] = []
        self._providers: Dict[str, Any] = {}
        self._is_active = False

        self._context = VXContext() if context is None else context
        self._context.lock = Lock()
        for k, v in kwargs.items():
            setattr(self._context, k, v)

    def start_up(
        self,
        *init_providers: VXInitProvider,
        **providers: AbstractProvider,
    ) -> None:
        """启动接口集合"""
        if self._is_active:
            return
        logging.info("starting interface: {%s} ...", self.__class__.__name__)

        for provider in init_providers:
            self._init_providers.append(provider)
            provider.start_up(self._context)

        for name, provider in providers.items():
            self.register_provider(name, provider)
            provider.start_up(self._context)

        self._is_active = True

    def tear_down(self) -> None:
        """关闭接口集合"""
        if not self._is_active:
            return

        for provider in self._init_proviers:
            provider.tear_down()
        self._init_proviers.clear()

        for name in self._providers.keys():
            self.unregister_provider(name)

        self._is_active = False

    @classmethod
    def from_config(
        cls, config: Union[str, Path], *, context: Optional[VXContext] = None
    ) -> "AbstractProviderCollection":
        """从配置文件初始化

        Arguments:
            config {Union[str, Path]} -- 配置文件路径
            context {Optional[VXContext]} -- 上下文
        """
        obj = cls(context=context)
        with open(config, "r", encoding="utf-8") as f:
            provider_configs = json.load(f)

        for name, provider_config in provider_configs.items():
            obj.register_provider(name, provider_config)
        return obj

    @property
    def context(self) -> Union[VXContext, Dict[str, Any]]:
        """上下文管理器"""
        return self._context

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} (id-{id(self)}) >"

    def __getattr__(self, name: str) -> Any:
        if name in self._providers:
            return self._providers[name]
        return super().__getattribute__(name)

    def register_provider(
        self, name: str, provider: Union[ProviderConfig, Any]
    ) -> None:
        """注册接口

        Arguments:
            name {str} -- 接口名称
            provider {Union[ProviderConfig,Callable[...]]} -- 接口提供者
        """
        try:
            provider_config = ProviderConfigAdapter.validate_python(provider)
            provider = import_by_config(provider_config)
        except ValidationError:
            pass
        self._providers[name] = provider
        logging.info("register interface : %s success..", name)

    def unregister_provider(self, name: str) -> None:
        """注销接口"""
        if name in self._providers:
            provider = self._providers.pop(name, None)
            if hasattr(provider, "tear_down"):
                provider.tear_down()
            logging.info("unregister interface: %s success..", name)
