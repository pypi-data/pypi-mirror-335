import numpy as np

from finter.backtest.v0.config import DataConfig, SimulatorConfig
from finter.modeling.utils import daily2period, get_rebalancing_mask

POSITION_SCALAR = 1e8
BASIS_POINT_SCALAR = 10000


class DataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def preprocess_position(config: SimulatorConfig, data: DataConfig):
        if config.execution.resample_period:
            position = daily2period(
                data.position,
                config.execution.resample_period,
                keep_index=True,
            )
        else:
            position = data.position

        return (
            np.nan_to_num((position / POSITION_SCALAR).to_numpy()),
            data.price.to_numpy(),
        )

    @staticmethod
    def preprocess_volume_capacity(config: SimulatorConfig, data: DataConfig):
        if config.trade.volume_capacity_ratio == 0:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                np.inf,
            )
        else:
            volume = data.volume.reindex(
                config.frame.common_index,
                columns=config.frame.common_columns,
            )
            return volume.fillna(0).to_numpy() * config.trade.volume_capacity_ratio

    @staticmethod
    def preprocess_rebalancing_mask(config: SimulatorConfig, data: DataConfig):
        period = config.execution.rebalancing_method
        if period in ["W", "M", "Q"]:
            return np.array(
                [
                    d in get_rebalancing_mask(data.position, period)  # type: ignore
                    for d in config.frame.common_index
                ],
                dtype=int,
            )
        else:
            return np.array([])

    @staticmethod
    def preprocess_dividend_ratio(config: SimulatorConfig, data: DataConfig):
        if data.dividend_ratio.empty:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                0,
            )
        else:
            return data.dividend_ratio.to_numpy()

    @staticmethod
    def preprocess_exchange_rate(config: SimulatorConfig, data: DataConfig):
        if data.exchange_rate.empty:
            return np.full(
                (len(config.frame.common_index), 1),
                1,
            )
        else:
            return data.exchange_rate.to_numpy()

    @staticmethod
    def preprocess_money_flow(config: SimulatorConfig, data: DataConfig):
        if data.money_flow.empty:
            return np.full(
                (len(config.frame.common_index), 1),
                0,
            )
        else:
            return np.nan_to_num(data.money_flow.to_numpy())

    @staticmethod
    def preprocess_target_volume_limit(config: SimulatorConfig, data: DataConfig):
        if config.trade.target_volume_limit_args is None:
            return np.array([])
        if config.trade.target_volume_limit_args["type"] == "trading_volume":
            return np.nan_to_num(
                (
                    data.volume.fillna(0)
                    .rolling(
                        config.trade.target_volume_limit_args["rolling_window"],
                        min_periods=1,
                    )
                    .mean()
                    * config.trade.target_volume_limit_args["limit_ratio"]
                ).to_numpy()
            )
        return np.array([])
