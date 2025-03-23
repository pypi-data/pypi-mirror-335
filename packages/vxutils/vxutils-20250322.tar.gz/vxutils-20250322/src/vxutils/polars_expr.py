"""polars表达式增强"""

import polars as pl
from datetime import datetime, timedelta
from typing import Union, Optional

from polars import (
    all,
    any,
    count,
    first,
    last,
    max,
    median,
    min,
    n_unique,
    quantile,
    std,
    sum,
    mean,
    var,
    corr,
    cov,
    cum_sum,
    cum_fold,
)

__all__ = [
    "all",
    "any",
    "count",
    "first",
    "last",
    "max",
    "mean",
    "median",
    "min",
    "n_unique",
    "quantile",
    "std",
    "sum",
    "var",
    "corr",
    "cov",
    "cum_sum",
    "cum_fold",
    "Abs",
    "Sign",
    "Log",
    "Not",
    "Power",
    "Add",
]


def Abs(
    col: Union[str, pl.Expr],
    name: str = "",
) -> pl.Expr:
    """计算绝对值

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Returns:
        pl.Expr -- 绝对值表达式
    """
    expr = pl.col(col).abs() if isinstance(col, str) else col.abs()
    expr = expr.alias(name) if name else expr
    return expr


def Sign(
    col: Union[str, pl.Expr],
    name: str = "",
) -> pl.Expr:
    """计算符号

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Returns:
        pl.Expr -- 符号表达式
    """
    expr = pl.col(col).sign() if isinstance(col, str) else col.sign()
    expr = expr.alias(name) if name else expr
    return expr


def Log(
    col: Union[str, pl.Expr],
    name: str = "",
) -> pl.Expr:
    """计算对数

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Returns:
        pl.Expr -- 对数表达式
    """
    expr = pl.col(col).log() if isinstance(col, str) else col.log()
    expr = expr.alias(name) if name else expr
    return expr


# * def Mask(
# *     col: Union[str, pl.Expr],
# *     predicate: pl.Expr,
# *     name: str = "",
# * ) -> pl.Expr:
# *     """根据条件过滤
# *
# *     Arguments:
# *         col {Union[str, pl.Expr]} -- 列名或表达式
# *         predicate {pl.Expr} -- 条件表达式
# *
# *     Returns:
# *         pl.Expr -- 过滤后的表达式
# *     """
# *     expr = pl.col(col)
# *     expr = expr.alias(name) if name else expr
# *     return expr


def Not(
    col: Union[str, pl.Expr],
    name: str = "",
) -> pl.Expr:
    """取反

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Returns:
        pl.Expr -- 取反表达式
    """
    expr = pl.col(col).not_() if isinstance(col, str) else col.not_()
    expr = expr.alias(name) if name else expr
    return expr


def Power(
    col: Union[str, pl.Expr],
    exponent: Union[int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """计算幂

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        exponent {Union[int, float]} -- 幂指数

    Returns:
        pl.Expr -- 幂表达式
    """
    expr = pl.col(col).pow(exponent) if isinstance(col, str) else col.pow(exponent)
    expr = expr.alias(name) if name else expr
    return expr


def Add(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """计算加法

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 加法表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left + col_right
    expr = expr.alias(name) if name else expr
    return expr


def Sub(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """计算减法

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 减法表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left - col_right
    expr = expr.alias(name) if name else expr
    return expr


def Mul(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """计算乘法

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 乘法表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left * col_right
    expr = expr.alias(name) if name else expr
    return expr


def Div(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """计算除法

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 除法表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left / col_right
    expr = expr.alias(name) if name else expr
    return expr


def Greater(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """大于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 大于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left > col_right
    expr = expr.alias(name) if name else expr
    return expr


def Less(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """小于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 小于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left < col_right
    expr = expr.alias(name) if name else expr
    return expr


def Gt(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """大于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 大于等于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left > col_right
    expr = expr.alias(name) if name else expr
    return expr


def Ge(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """大于等于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 大于等于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left >= col_right
    expr = expr.alias(name) if name else expr
    return expr


def Lt(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """小于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 小于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left < col_right
    expr = expr.alias(name) if name else expr
    return expr


def Le(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """小于等于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 小于等于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left <= col_right
    expr = expr.alias(name) if name else expr
    return expr


def Eq(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """等于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 等于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left == col_right
    expr = expr.alias(name) if name else expr
    return expr


def Ne(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr, int, float],
    *,
    name: str = "",
) -> pl.Expr:
    """不等于

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr, int, float]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 不等于表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right

    expr = col_left != col_right
    expr = expr.alias(name) if name else expr
    return expr


def And(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr],
    *,
    name: str = "",
) -> pl.Expr:
    """逻辑与

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 逻辑与表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right
    expr = col_left & col_right
    expr = expr.alias(name) if name else expr
    return expr


def Or(
    col_left: Union[str, pl.Expr],
    col_right: Union[str, pl.Expr],
    *,
    name: str = "",
) -> pl.Expr:
    """逻辑或

    Arguments:
        col_left {Union[str, pl.Expr]} -- 左侧列名或表达式
        col_right {Union[str, pl.Expr]} -- 右侧列名或表达式

    Returns:
        pl.Expr -- 逻辑或表达式
    """
    col_left = pl.col(col_left) if isinstance(col_left, str) else col_left
    col_right = pl.col(col_right) if isinstance(col_right, str) else col_right
    expr = col_left | col_right
    expr = expr.alias(name) if name else expr
    return expr


def If(
    conditions: Union[str, pl.Expr],
    feature_left: Union[str, pl.Expr],
    feature_right: Union[str, pl.Expr],
    *,
    name: str = "",
) -> pl.Expr:
    """条件表达式

    Arguments:
        conditions {Union[str, pl.Expr]} -- 条件表达式
        feature_left {Union[str, pl.Expr]} -- 条件成立时的值
        feature_right {Union[str, pl.Expr]} -- 条件不成立时的值

    Returns:
        pl.Expr -- 条件表达式
    """
    conditions = pl.col(conditions) if isinstance(conditions, str) else conditions
    expr = pl.when(conditions).then(feature_left).otherwise(feature_right)
    expr = expr.alias(name) if name else expr
    return expr


def Ref(
    col: Union[str, pl.Expr],
    N: int,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """引用前N行数据

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        N {int} -- 引用前N行数据

    Returns:
        pl.Expr -- 引用前N行数据表达式
    """

    expr = pl.col(col).shift(N) if isinstance(col, str) else col.shift(N)
    if over:
        expr = expr.over(over)
    expr = expr.alias(name) if name else expr
    return expr


def Mean(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算均值

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 均值表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col

    if windows is None:
        expr = expr.mean()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_mean(window_size=windows).over(over)
            if over
            else expr.rolling_mean(window_size=windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Max(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算最大值

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 最大值表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.max()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_max(windows).over(over) if over else expr.rolling_max(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Min(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算最小值

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 最小值表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.min()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_min(windows).over(over) if over else expr.rolling_min(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Std(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算标准差

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 标准差表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.std()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_std(windows).over(over) if over else expr.rolling_std(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Median(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算中位数

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Keyword Arguments:
        windows {int} -- 窗口大小 (default: {None})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})
        name {str} -- 命名 (default: {""})

    Returns:
        pl.Expr -- 中位数表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.median()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_median(windows).over(over)
            if over
            else expr.rolling_median(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Skew(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算偏度

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {Optional[Union[int, str, timedelta]]} -- 窗口大小 (default: {None})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})
        name {str} -- 命名 (default: {""})

    Returns:
        pl.Expr -- 偏度表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.skew()

    else:
        expr = expr.rolling_skew(window_size=windows)
    expr = expr.over(over) if over else expr
    expr = expr.alias(name) if name else expr
    return expr


def Kurtosis(
    col: Union[str, pl.Expr],
    windows: Optional[Union[int, str, timedelta]] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算峰度

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {Optional[Union[int, str, timedelta]]} -- 窗口大小 (default: {None})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})
        name {str} -- 命名 (default: {""})

    Returns:
        pl.Expr -- 峰度表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.kurtosis()
    else:
        raise NotImplementedError("rolling_kurtosis not implemented")
    expr = expr.over(over) if over else expr
    expr = expr.alias(name) if name else expr
    return expr


def Var(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算方差

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 方差表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.var()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_var(windows).over(over) if over else expr.rolling_var(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Sum(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算和

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {int} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 和表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.sum()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_sum(windows).over(over) if over else expr.rolling_sum(windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Count(
    col: Union[str, pl.Expr],
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算计数

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {Union[int, str, timedelta]} -- 窗口大小 (default: {0})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})

    Returns:
        pl.Expr -- 计数表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    expr = expr.count().over(over) if over else expr.count()
    expr = expr.alias(name) if name else expr
    return expr


def Sqrt(
    col: Union[str, pl.Expr],
    name: str = "",
) -> pl.Expr:
    """计算平方根

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式

    Returns:
        pl.Expr -- 平方根表达式
    """
    expr = pl.col(col).sqrt() if isinstance(col, str) else col.sqrt()
    expr = expr.alias(name) if name else expr
    return expr


def Quantile(
    col: Union[str, pl.Expr],
    quantile: float,
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算分位数

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        quantile {float} -- 分位数

    Returns:
        pl.Expr -- 分位数表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.quantile(quantile)
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr.rolling_quantile(quantile, window_size=windows).over(over)
            if over
            else expr.rolling_quantile(quantile, window_size=windows)
        )
    expr = expr.alias(name) if name else expr
    return expr


def Mad(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算绝对中位差

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        windows {Optional[int]} -- 窗口大小 (default: {None})
        over {Union[str, pl.Expr]} -- 分组列 (default: {""})
        name {str} -- 命名 (default: {""})

    Returns:
        pl.Expr -- 绝对中位差表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = (expr - expr.median()).abs().mean()
        expr = expr.over(over) if over else expr
    else:
        expr = (
            expr - expr.rolling_median(windows).over(over)
            if over
            else expr.rolling_median(windows)
        ).abs() / windows

    expr = expr.alias(name) if name else expr
    return expr


def IdxMin(
    col: Union[str, pl.Expr],
    windows: Optional[int] = None,
    *,
    over: Union[str, pl.Expr] = "",
    name: str = "",
) -> pl.Expr:
    """计算最小值索引

    Arguments:
        col {Union[str, pl.Expr]} -- 列名或表达式
        N {int} -- 窗口大小

    Returns:
        pl.Expr -- 最小值索引表达式
    """
    expr = pl.col(col) if isinstance(col, str) else col
    if windows is None:
        expr = expr.arg_min()
    else:
        expr = expr.rolling()

    expr = expr.alias(name) if name else expr
    return expr


if __name__ == "__main__":
    data = pl.DataFrame(
        [
            {"type": 1, "a": 1, "b": 2},
            {"type": 1, "a": 2, "b": 3},
            {"type": 1, "a": 2, "b": 3},
            {"a": 3, "b": 4, "type": 2},
            {"a": 4, "b": 5, "type": 2},
        ]
    )
    print(data)
    print(Mean("a"))
    print(data.select([Mean("a", over="type"), Count("b", over="type", name="test")]))
    print(data.filter(Mean("a") < 3))
    print(
        data.with_columns(
            [Mean("a", over="type"), Count("b", over="type", name="test")]
        )
    )
