#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from enum import Enum, unique


@unique
class ContractType(Enum):
    # SiteAPI合约类型枚举
    Unknown = "Unknown"
    InverseFutures = "Inverse Future"  # 反向交割合约
    InversePerpetual = "Inverse Perpetual"  # 反向永续合约
    LinearFutures = "Linear Future"  # 正向USDT交割
    LinearPerpetual = "Linear Perpetual"  # 正向永续合约
    UsdcFutures = "Usdc Future"  # usdc交割
    UsdcPerpetual = "Usdc Perpetual"  # usdc 合约
    UsdcSpot = "Usdc Spot"  # usdc 现货
    UsdtOption = "UsdtOption"  # USDT期权
    ZMXLinearPerpetual = "Zoomex Linear Perpetual"

    def __repr__(self):
        return "<%s.%s, %s>" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.name)


@unique
class UserType(Enum):
    """用户类型枚举类"""

    Unknown = 0
    DTA = 1
    UTA_PUBLIC = 3
    UTA_PRO = 4
    Margin = 5
    UTA_Wallet = 6

    @classmethod
    def value2member(cls, value: int):
        member = cls._value2member_map_.get(int(value), None)
        if member is None:
            raise Exception(f"Member[value: {value}] is not exits")
        return member


@unique
class ContractStatus(Enum):
    Pending = 0
    Trading = 1
    Settling = 3
    Closed = 4

    @classmethod
    def name2member(cls, name):
        return cls._member_map_[name]


@unique
class Category(Enum):
    Unknown = "unknown"
    Spot = "spot"
    Linear = "linear"
    Inverse = "inverse"
    Option = "option"

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]


@unique
class TwapCategory(Enum):
    Unknown = -1
    USDT = 1
    USDC = 2
    INVERSE = 3
    UTA_USDT = 4
    UTA_USDC = 5
    INVERSE_FUTURE = 6
    UTA_USDC_FUTURE = 7
    UTA_SPOT = 8

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]


@unique
class TwapStrategyStatus(Enum):
    UNKNOWN = 0
    INIT = 1
    RUNNING = 2
    TERMINATED = 3
    TERMINATED_WITH_ORDER_NOT_FILLED = 4
    PAUSE = 5

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]


@unique
class StrategyType(Enum):
    UNKNOWN = "unknown"
    TWAP = "twap"
    WEBHOOK = "webhook"
    CHASE = "chaseOrder"
    ARBITRAGE = "arbitrage"
    ICEBERG = "iceberg"

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]


@unique
class KlineType(Enum):
    Unknown = 0
    MarketPrice = 1
    IndexPrice = 2
    MarkPrice = 3
    PremiumIndexKline = 4

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]

    def __repr__(self):
        return "<%s.%s, %s>" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.name)


@unique
class BusinessType(Enum):
    Future = "future"
    Spot = "spot"
    Option = "option"
    Spread = "Spread"
    Unknown = "Unknown"

    @classmethod
    def value2member(cls, value):
        return cls._value2member_map_[value]

    def __repr__(self):
        return "<%s.%s, %s>" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.name)
