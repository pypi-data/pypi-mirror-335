from dataclasses import dataclass, fields
from enum import Enum
from typing import ClassVar, Dict, Union

from typing_extensions import Literal

from finter.backtest.v0.builder import SimulatorBuilder
from finter.backtest.v0.config import AVAILABLE_CORE_TYPES, AVAILABLE_DIVIDEND_TYPES

AVAILABLE_MARKETS = Literal[
    "kr_stock",
    "us_stock",
    "us_etf",
    "id_stock",
    "id_bond",
    "id_fund",
    #########################################################
    "vn_stock",
    "crypto_spot_binance",
]
AVAILABLE_BASE_CURRENCY = Literal["KRW", "IDR", "USD", "VND"]
AVAILABLE_DEFAULT_BENCHMARK = Literal[
    "KOSPI200", "S&P500", "JCI", "HO_CHI_MINH_STOCK_INDEX", "US_DOLLAR_INDEX"
]


@dataclass
class MarketConfig:
    initial_cash: float
    buy_fee_tax: float
    sell_fee_tax: float
    slippage: float
    dividend_tax: float

    core_type: AVAILABLE_CORE_TYPES

    adj_dividend: bool
    base_currency: AVAILABLE_BASE_CURRENCY

    default_benchmark: AVAILABLE_DEFAULT_BENCHMARK

    drip: AVAILABLE_DIVIDEND_TYPES


class MarketType(Enum):
    KR_STOCK = "kr_stock"
    US_STOCK = "us_stock"
    US_ETF = "us_etf"
    ID_STOCK = "id_stock"
    ID_BOND = "id_bond"
    ID_FUND = "id_fund"

    VN_STOCK = "vn_stock"
    CRYPTO_SPOT_BINANCE = "crypto_spot_binance"


@dataclass
class MarketTemplates:
    # Class variable to store all market configurations
    CONFIGS: ClassVar[Dict[MarketType, MarketConfig]] = {
        MarketType.KR_STOCK: MarketConfig(
            initial_cash=100_000_000,  # 1억원
            buy_fee_tax=1.2,
            sell_fee_tax=31.2,
            slippage=10,
            dividend_tax=1540,
            core_type="basic",
            drip=None,
            #
            adj_dividend=False,
            base_currency="KRW",
            default_benchmark="KOSPI200",
        ),
        MarketType.US_STOCK: MarketConfig(
            initial_cash=100_000,
            buy_fee_tax=25,
            sell_fee_tax=25,
            slippage=10,
            dividend_tax=0,
            core_type="basic",
            drip=None,
            #
            adj_dividend=False,
            base_currency="USD",
            default_benchmark="S&P500",
        ),
        MarketType.US_ETF: MarketConfig(
            initial_cash=100_000,
            buy_fee_tax=25,
            sell_fee_tax=25,
            slippage=10,
            dividend_tax=0,
            core_type="basic",
            drip=None,
            #
            adj_dividend=False,
            base_currency="USD",
            default_benchmark="S&P500",
        ),
        MarketType.ID_STOCK: MarketConfig(
            initial_cash=1_000_000_000,
            buy_fee_tax=20,
            sell_fee_tax=30,
            slippage=10,
            dividend_tax=0,
            core_type="basic",
            drip=None,
            #
            adj_dividend=False,
            base_currency="IDR",
            default_benchmark="JCI",
        ),
        MarketType.ID_BOND: MarketConfig(
            initial_cash=1_000_000_000,
            buy_fee_tax=10,
            sell_fee_tax=10,
            slippage=50,
            dividend_tax=1000,
            core_type="basic",
            drip="coupon",
            #
            adj_dividend=True,
            base_currency="IDR",
            default_benchmark="JCI",
        ),
        MarketType.ID_FUND: MarketConfig(
            initial_cash=1_000_000_000,
            buy_fee_tax=10,
            sell_fee_tax=10,
            slippage=0,
            dividend_tax=0,
            core_type="id_fund",
            drip=None,
            #
            adj_dividend=False,
            base_currency="IDR",
            default_benchmark="JCI",
        ),
        MarketType.VN_STOCK: MarketConfig(
            initial_cash=1_000_000_000,
            buy_fee_tax=40,
            sell_fee_tax=50,
            slippage=10,
            dividend_tax=0,
            core_type="vn",
            drip=None,
            #
            adj_dividend=False,
            base_currency="VND",
            default_benchmark="HO_CHI_MINH_STOCK_INDEX",
        ),
        MarketType.CRYPTO_SPOT_BINANCE: MarketConfig(
            initial_cash=100_000,
            buy_fee_tax=10,
            sell_fee_tax=10,
            slippage=10,
            dividend_tax=0,
            core_type="basic",
            drip=None,
            #
            adj_dividend=False,
            base_currency="USD",
            default_benchmark="US_DOLLAR_INDEX",
        ),
    }

    @classmethod
    def create_simulator(
        cls,
        market_type: AVAILABLE_MARKETS,
    ) -> SimulatorBuilder:
        try:
            market_enum = MarketType(market_type)
        except ValueError:
            raise ValueError(f"Unsupported market type: {market_type}")

        if market_enum not in cls.CONFIGS:
            raise ValueError(f"Unsupported market type: {market_enum}")

        config = cls.CONFIGS[market_enum]
        return (
            SimulatorBuilder()
            .update_cost(
                buy_fee_tax=config.buy_fee_tax,
                sell_fee_tax=config.sell_fee_tax,
                slippage=config.slippage,
                dividend_tax=config.dividend_tax,
            )
            .update_trade(
                initial_cash=config.initial_cash,
            )
            .update_execution(
                core_type=config.core_type,
                drip=config.drip,
            )
        )

    @classmethod
    def get_config_value(
        cls,
        market_type: AVAILABLE_MARKETS,
        config_key: str,
    ) -> Union[float, bool, AVAILABLE_CORE_TYPES, AVAILABLE_BASE_CURRENCY]:
        valid_keys = {field.name for field in fields(MarketConfig)}
        if config_key not in valid_keys:
            raise ValueError(
                f"Invalid config key: {config_key}. "
                f"Valid keys are: {', '.join(valid_keys)}"
            )

        try:
            market_enum = MarketType(market_type)
        except ValueError:
            raise ValueError(f"Unsupported market type: {market_type}")

        if market_enum not in cls.CONFIGS:
            raise ValueError(f"Unsupported market type: {market_enum}")

        return getattr(cls.CONFIGS[market_enum], config_key)
