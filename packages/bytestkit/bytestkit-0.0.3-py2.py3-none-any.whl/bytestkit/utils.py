#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import calendar
import datetime
import decimal
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Literal, Sequence, Tuple, Union

import yaml

from .exceptions import ExecuteCommandError


class CommonUtils:
    @staticmethod
    def get_host_ip() -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    @staticmethod
    def in_container() -> bool:
        """判断当前是否在docker容器中"""
        return os.path.exists("/.dockerenv")

    @staticmethod
    def execute_command(cmd: Union[str, list], json_load: bool = False, timeout: Union[float, int] = 5, **kwargs):
        """执行终端命令, 并返回控制台输出.

        Args:
            cmd (str): 终端命令, 可以传一个完整的命令行字符串, 或者传一个包含各个参数切片的列表, 详见下面的示例,
            json_load (bool, optional): 是否对控制台输出内容进行反序列化操作. Defaults to False.

        Usage
        1. 可以传一个完整的命令行字符串
        cmd = "ls -al"
        execute_command(cmd)
        2. 传一个包含各个参数的列表
        reqData = {"symbol": "BTCUSDT", "interval": 1}
        cmd = ['grpcurl', '-plaintext', '-d', reqData, '10.18.4.64:25105', 'bybit.future.quote.v5.APIService.GetFirstKline']
        execute_command(cmd)
        """
        try:
            if isinstance(cmd, str):  # 兼容旧版本
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout, **kwargs).decode("utf-8")
            else:
                _cmd = []
                for c in cmd:
                    if isinstance(c, (int, float)):
                        _cmd.append(float(c))
                    elif isinstance(c, (dict, list)):
                        _cmd.append(json.dumps(c))
                    else:
                        _cmd.append(c)
                result = subprocess.check_output(_cmd, text=True, stderr=subprocess.STDOUT, timeout=timeout, **kwargs)
        except subprocess.CalledProcessError as e:
            raise ExecuteCommandError(f"Failed to execute terminal command: {_cmd}, e: {repr(e)}") from e

        if json_load:
            result = json.loads(result)

        return result

    @staticmethod
    def load_yaml(filename: Union[str, Path]) -> dict:
        """从yaml文件中反序列化数据

        Args:
            filename (Union[str, Path]): yaml文件路径或Path对象
        """
        fp: Path = Path(filename) if isinstance(filename, str) else filename
        if not fp.exists():
            raise ValueError("yaml文件不存在: {}".format({fp.absolute()}))

        with open(fp, "r", encoding="utf-8") as f:
            data: dict = yaml.load(f.read(), Loader=yaml.FullLoader)
            return data

    @staticmethod
    def json_schema_diff(src: dict, dst: dict, key_whitelist: Sequence[str] = None) -> dict:
        """
        json结构体比对
        """
        assert all([isinstance(src, dict), isinstance(dst, dict)]), "Unsupported parameter type."

        def _recursive_diff(left, right, details, path="/"):
            if isinstance(left, type(right)):
                details.append({"replace": path, "value": right, "details": "type", "src": left})
                return

            delim = "/" if path != "/" else ""

            if key_whitelist and isinstance(left, dict) and isinstance(right, dict):
                for k in key_whitelist:
                    if k in left:
                        left.pop(k)
                    if k in right:
                        right.pop(k)

            if isinstance(left, dict):
                for k, v in left.items():
                    new_path = delim.join([path, k])
                    if k not in right:
                        details.append({"remove": new_path, "src": v})
                    else:
                        _recursive_diff(v, right[k], details, new_path)
                for k, v in right.items():
                    if k in left:
                        continue
                    details.append({"add": delim.join([path, k]), "dst": v})
            elif isinstance(left, list):
                left_lenth = len(left)
                right_lenth = len(right)
                if left_lenth > right_lenth:
                    for i, item in enumerate(left[right_lenth:], start=right_lenth):
                        details.append({"remove": delim.join([path, str(i)]), "src": item, "details": "array-item"})
                elif right_lenth > left_lenth:
                    for i, item in enumerate(right_lenth[left_lenth:], start=left_lenth):
                        details.append({"add": delim.join([path, str(i)]), "dst": item, "details": "array-item"})
                minl = min(right_lenth, right_lenth)
                if minl > 0:
                    for i, item in enumerate(left[:minl]):
                        _recursive_diff(item, right[i], details, delim.join([path, str(i)]))
            else:
                if isinstance(left, type(right)):
                    details.append({"replace": path, "dst": right, "src": left})

            details = []
            _recursive_diff(src, dst, details)

            res = {}
            res["result"] = True if len(details) == 0 else False
            res["details"] = details
            return res


_DateLike = Union[str, datetime.date]
_DateTimeLike = Union[str, datetime.datetime, datetime.date]


class DateTimeUtils:
    """
    时间/日期相关的公共方法
    """

    @staticmethod
    def today() -> datetime.date:
        """返回今天的日期"""
        return datetime.date.today()

    @staticmethod
    def get_current_timestamp(length=10) -> int:
        """
        返回当前时间戳(10位或者13位)
        """
        current_time = time.time()
        if length == 13:
            return int(current_time * 1000)
        else:
            return int(current_time)

    @staticmethod
    def is_current_time_earlier_than(target_datetime_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> bool:
        """判断当前日期时间是否早于传入的时间日期"""
        target_datetime = datetime.datetime.strptime(target_datetime_str, fmt)
        current_datetime = datetime.datetime.now()

        if current_datetime > target_datetime:
            return True
        else:
            return False

    @staticmethod
    def month_date_range(year: int, month: int, date_fmt="%Y-%m-%d") -> Tuple[str, str]:
        """计算某个月份的日期范围
        如: get_month_date_range(2022, 6) -> (2022-06-01, 2022-06-30)
        """
        start_date = datetime.date(int(year), int(month), 1)
        _, days_in_month = calendar.monthrange(year, month)
        end_date = start_date + datetime.timedelta(days=days_in_month - 1)

        return start_date.strftime(date_fmt), end_date.strftime(date_fmt)

    @staticmethod
    def datetime_to_timestamp(dt: datetime.datetime, tzinfo=datetime.timezone.utc) -> int:
        """将`datetime.datetime`对象转换为10位时间戳"""
        return int(dt.replace(tzinfo=tzinfo).timestamp())

    @staticmethod
    def timestamp_to_datetime(ts: int) -> datetime.datetime:
        """10位时间戳转换为`datetime.datetime`对象"""
        return datetime.datetime.utcfromtimestamp(ts)

    @staticmethod
    def timestamp_to_date(ts: int) -> datetime.datetime:
        """10位时间戳转换为`datetime.date`对象"""
        dt = DateTimeUtils.timestamp_to_datetime(ts)
        return datetime.date(year=dt.year, month=dt.month, day=dt.day)

    @staticmethod
    def timestamp_to_str(ts: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """时间戳转换为时间字符串格式"""
        return time.strftime(fmt, time.localtime(ts))

    @staticmethod
    def str_to_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
        """时间字符串格式转换为`datetime.datetime`对象"""
        if isinstance(dt_str, datetime.date):
            return dt_str
        return datetime.datetime.strptime(dt_str, fmt)

    @staticmethod
    def str_to_date(dt_str: str, fmt: str = "%Y-%m-%d") -> datetime.date:
        """时间字符串格式转换为`datetime.date`对象"""
        if isinstance(dt_str, datetime.date):
            return dt_str
        return datetime.datetime.strptime(dt_str.strip(), fmt).date()

    @staticmethod
    def get_specific_timestamp():
        """
        当前处于本周任意一天, 获取上周五08:00:00的时间戳
        """
        t = datetime.datetime.now()  # 获取当前时间
        t_8 = t.replace(t.year, t.month, t.day, 8, 0, 0, 0)  # 获取当天早上8点
        tl = time.localtime()
        tw = tl.tm_wday  # 本周的第几天
        timeArray = time.strptime(str(t_8), "%Y-%m-%d %H:%M:%S")  # 转换成时间数组
        timestamp = time.mktime(timeArray)  # 转换成时间戳
        endTimeE3 = (int(timestamp) - (int(tw) + 3) * 24 * 3600) * 1000

        return endTimeE3

    @staticmethod
    def timestamp_range(endTime: _DateTimeLike = None, startTime: _DateTimeLike = None, intervalDays: int = 7, digits: int = 10) -> Tuple[int, int]:
        """返回指定的日期时间范围, 计算对应的10位或13位时间戳范围

        Args:
            endTime (Union[str, datetime.datetime], optional): 结束日期时间, 不传则默认当天23:59:59, 如传入字符串, 格式为: 2024-02-01 12:00:00.
            startTime (Union[str, datetime.datetime], optional): 开始日期时间, 不传则默认根据结束时间和间隔天数往前倒推. 如传入字符串, 格式为: 2024-01-01 12:00:00.
            intervalDays (int): 起始时间间隔范围
            digits (int): 时间戳位数, 默认10位, 支持10位或13位
        """
        if endTime is None:
            endTime = datetime.datetime.now()
            endTimestamp = int(endTime.replace(hour=23, minute=59, second=59).timestamp())
        else:
            endTime = DateTimeUtils.str_to_datetime(endTime)
            endTimestamp = endTime.timestamp()

        if startTime is None:
            startTime = endTime - datetime.timedelta(days=intervalDays)
            startTimestamp = int(startTime.replace(hour=0, minute=0, second=0).timestamp())
        else:
            startTime = DateTimeUtils.str_to_datetime(startTime)
            startTimestamp = startTime.timestamp()

        if digits == 13:
            return int(startTimestamp) * 1000, int(endTimestamp) * 1000

        return int(startTimestamp), int(endTimestamp)

    @staticmethod
    def date_range(endDate: _DateTimeLike = None, intervalDays: int = 7) -> Tuple[str, str]:
        """根据结束日期和间隔时间, 倒推开始日期, 返回一个包含起始日期和结束日期的元组(字符串格式)

        Args:
            endDate (Union[str, datetime.datetime], optional): 结束日期, 不传则默认当天, 如传入字符串, 格式为: 2022-01-01.
            internal_days (int): 起始时间间隔范围
        """
        if endDate is None:
            endDate = datetime.date.today()
        endDate = DateTimeUtils.str_to_date(endDate)
        startDate = endDate - datetime.timedelta(days=intervalDays)
        return startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d")

    @staticmethod
    def get_recent_month_date_range(internal_months: int, endDate: _DateTimeLike = None) -> datetime.date:
        """根据endDate向前推指定个月, 返回日期对象

        Args:
            internal_months (int): 月数
            endDate (Union[str, datetime.date], optional): 结束日期, 不传则默认当天, 如传入字符串, 格式为: 2022-01-01.
        """
        if endDate is None:
            _endDate = datetime.date.today()
        elif isinstance(endDate, str):
            _endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        else:
            _endDate = endDate
        assert isinstance(_endDate, datetime.date), f"不支持的参数类型, endTime: `<{type(_endDate)}>`"

        month = _endDate.month - 1 - internal_months
        year = _endDate.year + month // 12
        month = month % 12 + 1
        day = min(_endDate.day, calendar.monthrange(year, month)[1])

        target_date = _endDate.replace(year, month, day)
        return target_date

    @staticmethod
    def calc_month_delta(startDate: _DateLike, endDate: _DateLike = None) -> int:
        """计算两个日期之间的月份差

        说明:
            1. 如果两个日期在同一个月份, 返回0, 如:  calc_month_delta("2023-02-01","2023-02-28") -> 0
            2. 如果两个日期很接近, 但是不在一个月份, 会返回1, 如: calc_month_delta("2023-02-28","2023-03-01") -> 1
            3. 如果传入的 end_date < start_date, 则会返回负数
        """
        _startDate = DateTimeUtils.str_to_date(startDate)
        if endDate is None:
            _endDate = datetime.date.today()
        else:
            _endDate = DateTimeUtils.str_to_date(endDate)

        year_gap = _endDate.year - _startDate.year
        if _startDate.month == _endDate.month:
            monthDelta = 0 + year_gap * 12
        else:
            if year_gap >= 0 and _endDate >= _startDate:
                delta: datetime.timedelta = _endDate - _startDate
            else:
                delta: datetime.timedelta = _startDate - _endDate
            days = delta.days
            monthDelta = (days // 30) + 1 + year_gap * 12
        return monthDelta


_NumericLike = Union[int, float, str, decimal.Decimal]


def isNumeric(n: _NumericLike, raise_exception=False) -> bool:
    """判断给定的值是否为数值类型或可以转换为数值类型的字符串。

    Args:
        n (NumericLike): 需要判断的输入值，可以是 int, float, decimal.Decimal 或者表示数字的字符串。
        raise_exception (bool, optional): 如果设置为 True 且输入不是数值类型，则抛出 ValueError。默认为 False。

    Returns:
        bool: 如果输入是数值类型或可转换为数值类型的字符串返回 True, 否则返回 False。

    Raises:
        ValueError: 当 `raise_exception` 设置为 True 并且输入值不是数值类型时抛出。
    """
    if isinstance(n, (int, float, decimal.Decimal)):
        flag = True
    elif isinstance(n, str) and n.replace(".", "").lstrip("+").lstrip("-").isdigit():  # not stirp
        flag = True
    else:
        flag = False

    if raise_exception and flag is False:
        raise ValueError(f"Unsupport value type: {n}, type: {type(n)}")

    return flag


class DecimalUtils:
    """十进制浮点运算工具类.
    同时实例方法支持链式调用, 降低python弱语言类型造成的困扰.

    使用示例:
    triggerPrice = '0.348526'
    scaledTriggerPriceStr = DecimalUtils(triggerPrice).round("0.000").scale(3).to_string()
    """

    def __init__(self, n: _NumericLike, rounding: str = None, context: decimal.Context = None):
        isNumeric(n, True)

        ctx = context if context else decimal.getcontext()
        self.n = decimal.Decimal(str(n))

        # 设置舍入模式为四舍五入, 即若最后一个有效数字小于5则朝0方向取整，否则朝0反方向取整
        self.rounding = decimal.ROUND_HALF_UP if not rounding else rounding
        ctx.rounding = self.rounding
        ctx.prec = 28

        # init
        self._cache = self.n

    def round(self, exp: str):
        """将数值四舍五入到指定精度.
        Usage:
        >>> roundPrice1 = DecimalUtils('3.14145').round('0.0000').to_string()
        >>> Assert.assert_equal(roundPrice1, '3.1415')
        >>> Assert.assert_not_equal(roundPrice1, round(3.14145, 4))
        """
        _exp = exp if isinstance(exp, str) else str(exp)
        self._cache = self._cache.quantize(decimal.Decimal(_exp), self.rounding)
        return self

    def truncate(self, exp: str):
        """将数值截取到指定精度 (不四舍五入)
        Usage:
        >>> DecimalUtils('3.1415').truncate('0.000').to_string()
        3.141
        """
        sourcePrecision = DecimalUtils(self._cache).get_precision()
        target_precision = DecimalUtils(exp).get_precision()
        if sourcePrecision > target_precision:
            t = str(self._cache).split(".")
            self._cache = decimal.Decimal(t[0] + "." + t[1][:target_precision])  # truncate

        return self

    def scale(self, e: int):
        """以10为底, 将参数进行指数级别缩放 (e可为负数)
        Usage:
        >>> DecimalUtils('0.348526').scale(3).to_string()
        348.526
        >>> DecimalUtils('348.526').scale(-3).to_string()
        0.348526
        """
        self._cache = self._cache.scaleb(e)
        return self

    def biz_round(self, size: _NumericLike, mode: Literal["floor", "ceil"] = "floor"):
        """根据根据size, 将数值进行 向下裁减 或 向上进位 处理, 返回的结果与size保持相同精度.
        Uasge:
        >>> DecimalUtils(1.66 * 1.05).bizRound("0.001", "floor").to_string()
        1.742
        >>> DecimalUtils(1.66 * 1.05).bizRound("0.001", "ceil").to_string()
        1.743
        """
        if mode == "floor":
            x: int = self.floor(size)
        elif mode == "ceil":
            x: int = self.ceil(size)
        else:
            raise ValueError(f"Unsupport mode: {mode}")

        temp = DecimalUtils(size) * x
        self._cache = temp.truncate(size).to_decimal()
        return self

    def cutdown(self, size: _NumericLike):
        """根据根据size, 将数值进行向下裁减处理, 返回的结果与size保持相同精度.
        如: 根据ticksize, 将price进行向下裁减处理, 并保存与tickesize相同的小数精度

        Uasge:
        >>> DecimalUtils("16000.6").cutdown('0.5').to_string()
        16000.5
        >>> DecimalUtils("16000.6").cutdown('0.50').to_string()
        16000.50
        """
        isNumeric(size, True)
        x: int = self.floor(size)
        temp = DecimalUtils(size) * x
        self._cache = temp.truncate(size).to_decimal()
        return self

    def is_zero(self) -> bool:
        """如果参数为0, 则返回True, 否则返回False
        Usage:
        >>> DecimalUtils('0.001').isZero()
        Flase
        >>> DecimalUtils('0.00').isZero()
        True
        """
        return self._cache.is_zero()

    def is_multiple(self, exp: _NumericLike) -> bool:
        """判断数值是否为传入参数的整数倍
        Uasge:
        >>> DecimalUtils("500000").isMultiple("0.005")
        True
        >>> DecimalUtils("500000.1").isMultiple("0.5")
        False
        """
        isNumeric(exp, True)
        precision = DecimalUtils(exp).get_precision()
        exp_scale = DecimalUtils(exp).scale(precision).to_int()
        cache_scale = DecimalUtils(self._cache).scale(precision).to_int()
        return (cache_scale % exp_scale) == 0

    def is_sigend(self) -> bool:
        """如果参数带有负号,则返回为True, 否则返回False
        特殊地, -0会返回Flase
        """
        return self._cache.is_signed()

    def delete_extra_zero(self):
        """删除小数点后面多余的0"""
        self._cache = decimal.Decimal(str(self._cache).rstrip("0").rstrip("."))
        return self

    def get_precision(self) -> int:
        """获取小数位精度"""
        _cache_str = str(self._cache).lower()
        if "." in _cache_str:
            precision = len(_cache_str.rsplit(".", maxsplit=1)[-1])
        elif "e" in _cache_str:  # 当数值较大或者较小时, 会变为科学计数法
            _, precision = _cache_str.replace("-", "").split("e")
            precision = int(precision)
        else:
            precision = 0

        return precision

    def floor(self, size: _NumericLike) -> int:
        """向下取整"""
        isNumeric(size, True)
        temp = self._cache / decimal.Decimal(size)
        return temp.to_integral_value(rounding=decimal.ROUND_FLOOR)

    def ceil(self, size: _NumericLike) -> int:
        """向上取整"""
        isNumeric(size, True)
        temp = self._cache / decimal.Decimal(size)
        return temp.to_integral_value(rounding=decimal.ROUND_CEILING)

    def to_decimal(self) -> decimal.Decimal:
        return self._cache

    def to_int(self) -> int:
        return int(self._cache.to_integral_value())

    def to_float(self) -> float:
        return float(self._cache)

    def to_string(self) -> str:
        _cache_str = str(self._cache).lower()
        if "e" in _cache_str:
            return str(int(self._cache.to_integral_value()))
        return str(self._cache)

    def _type_convert(self, other):
        if isinstance(other, DecimalUtils):
            return other
        isNumeric(other, True)
        return DecimalUtils(other)

    def __eq__(self, other) -> bool:
        return self._cache == self._type_convert(other)._cache

    def __ne__(self, other) -> bool:
        return self._cache != self._type_convert(other)._cache

    def __lt__(self, other) -> bool:
        return self._cache < self._type_convert(other)._cache

    def __le__(self, other) -> bool:
        return self._cache <= self._type_convert(other)._cache

    def __gt__(self, other) -> bool:
        return self._cache > self._type_convert(other)._cache

    def __ge__(self, other) -> bool:
        return self._cache >= self._type_convert(other)._cache

    def __add__(self, other):
        return DecimalUtils(self._cache + self._type_convert(other)._cache)

    def __sub__(self, other):
        return DecimalUtils(self._cache - self._type_convert(other)._cache)

    def __mul__(self, other):
        return DecimalUtils(self._cache * self._type_convert(other)._cache)

    def __truediv__(self, other):
        return DecimalUtils(self._cache / self._type_convert(other)._cache)

    def __floordiv__(self, other):
        return DecimalUtils(self._cache // self._type_convert(other)._cache)

    def __mod__(self, other):
        return DecimalUtils(self._cache % self._type_convert(other)._cache)

    def __pow__(self, other):
        return DecimalUtils(self._cache ** self._type_convert(other)._cache)

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __rmod__(self, other):
        return self.__mod__(other)

    def __rpow__(self, other):
        return self.__pow__(other)

    def __repr__(self) -> str:
        return f"type: {type(self)}, cache: {self._cache}, rounding: {self.rounding}"

    def __str__(self) -> str:
        return self.__repr__()
