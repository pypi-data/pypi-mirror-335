"""SQLite ORM with VXDataModel."""

import polars as pl
from pathlib import Path
from threading import Lock
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple, Union, Literal, Type
from vxutils.datamodel.core import VXDataModel


class PolarsDataBase:
    """Polars ORM with VXDataModel."""

    def __init__(self, db_uri: Union[str, Path] = ":memory:"):
        self._db_uri = db_uri
        self._lock = Lock()
        self._mappings: Dict[str, Type[VXDataModel]] = {}

    def mapping(
        self, table_name: str, datamodel_cls: Type[VXDataModel], *primary_keys: str
    ) -> None:
        """Mapping a VXDataModel class to a SQLite table."""
        with self._lock:
            self._mappings[table_name] = (datamodel_cls, primary_keys)

    def crate_table(
        self,
        table_name: str,
        datamodel_cls: Type[VXDataModel],
        primary_keys: List[str],
        if_exists: Literal["replace", "raise", "ignore"] = "raise",
    ) -> None:
        """Create a table from a VXDataModel class."""
        with self._lock:
            if if_exists == "replace":
                self.drop_table(table_name)
            elif if_exists == "raise" and table_name in self._mappings:
                raise ValueError(f"Table {table_name} already exists.")


if __name__ == "__main__":
    pass
