import numpy as np
import pandas as pd

from finter.backtest.v0.config import SimulatorConfig
from finter.backtest.v0.simulators.vars import InputVars, SimulationVariables


class BaseBacktestor:
    def __init__(
        self,
        config: SimulatorConfig,
        input_vars: InputVars,
        results: list[str] = [],
    ):
        # 보존할 속성들을 저장
        self.results = results

        self.frame = config.frame
        self.trade = config.trade
        self.execution = config.execution
        self.optional = config.optional
        self.cost = config.cost

        self.vars = SimulationVariables(input_vars, self.frame.shape)
        self.vars.initialize(self.trade.initial_cash)

        self._results = BacktestResult(self)

    def _clear_all_variables(self):
        preserved = {}
        for attr_name in self.results:
            if hasattr(self._results, attr_name):
                preserved[attr_name] = getattr(self._results, attr_name)

        results = self.results
        for attr in list(self.__dict__.keys()):
            delattr(self, attr)

        self.results = results
        for attr_name, attr_value in preserved.items():
            setattr(self, attr_name, attr_value)

    def run(self):
        raise NotImplementedError

    @property
    def _summary(self):
        return self._results.summary

    def plot_single(self, single_asset):
        return self._results.plot_single(single_asset)


class BacktestResult:
    def __init__(self, simulator: BaseBacktestor) -> None:
        self.simulator = simulator
        self.vars = simulator.vars
        self.frame = simulator.frame

    def _create_df(
        self, data: np.ndarray, index: list[str], columns: list[str]
    ) -> pd.DataFrame:
        if data.size == 0:
            return pd.DataFrame(index=index, columns=columns)
        return pd.DataFrame(data, index=index, columns=columns)

    @property
    def aum(self) -> pd.DataFrame:
        return self._create_df(self.vars.result.aum, self.frame.common_index, ["aum"])

    @property
    def cash(self) -> pd.DataFrame:
        return self._create_df(self.vars.result.cash, self.frame.common_index, ["cash"])

    @property
    def valuation(self) -> pd.DataFrame:
        return self._create_df(
            self.vars.result.valuation,
            self.frame.common_index,
            self.frame.common_columns,
        )

    @property
    def cost(self) -> pd.DataFrame:
        cost = (
            self.vars.buy.actual_buy_volume
            * self.vars.input.buy_price
            * self.simulator.cost.buy_fee_tax
        ) + (
            self.vars.sell.actual_sell_volume
            * self.vars.input.sell_price
            * self.simulator.cost.sell_fee_tax
        )
        return self._create_df(
            np.nan_to_num(cost),
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    @property
    def slippage(self) -> pd.DataFrame:
        slippage = (
            self.vars.buy.actual_buy_volume
            * self.vars.input.buy_price
            * (self.simulator.cost.slippage / (1 + self.simulator.cost.slippage))
        ) + (
            self.vars.sell.actual_sell_volume
            * self.vars.input.sell_price
            * (self.simulator.cost.slippage / (1 - self.simulator.cost.slippage))
        )
        return self._create_df(
            np.nan_to_num(slippage),
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    @property
    def exchange_rate(self) -> pd.DataFrame:
        return self._create_df(
            self.vars.input.exchange_rate,
            self.frame.common_index,
            ["exchange_rate"],
        )

    @property
    def dividend(self) -> pd.DataFrame:
        return self._create_df(
            self.vars.result.dividend,
            self.frame.common_index,
            self.frame.common_columns,
        )

    @property
    def money_flow(self) -> pd.DataFrame:
        return self._create_df(
            self.vars.input.money_flow,
            self.frame.common_index,
            ["money_flow"],
        )

    @property
    def summary(self) -> pd.DataFrame:
        if self.simulator.execution.drip == "reinvest":
            cash = self.cash
            aum = self.aum
        elif self.simulator.execution.drip in ["cash", "coupon"]:
            cash = self.cash.add(self.dividend.sum(axis=1).cumsum(), axis=0)
            aum = self.aum.add(self.dividend.sum(axis=1).cumsum(), axis=0)
        else:
            cash = self.cash
            aum = self.aum

        result = pd.concat(
            [
                aum,
                cash,
                self.valuation.sum(axis=1).rename("valuation"),
                self.money_flow,
                self.cost.sum(axis=1).rename("cost"),
                self.slippage.sum(axis=1).rename("slippage"),
                self.exchange_rate,
                self.dividend.sum(axis=1).rename("dividend"),
            ],
            axis=1,
        )
        result["daily_return"] = (
            (result["aum"] - result["money_flow"]) / result["aum"].shift()
        ).fillna(1)
        result["nav"] = result["daily_return"].cumprod() * 1000

        result = result.reindex(
            columns=[
                "nav",
                "aum",
                "cash",
                "valuation",
                "money_flow",
                "dividend",
                "cost",
                "slippage",
                "daily_return",
                "exchange_rate",
            ]
        )

        return result

    @property
    def average_buy_price(self) -> pd.DataFrame:
        self.cummulative_buy_amount = np.full(
            self.simulator.frame.shape, np.nan, dtype=np.float64
        )
        self.__average_buy_price = np.full(
            self.simulator.frame.shape, np.nan, dtype=np.float64
        )

        self.cummulative_buy_amount[0] = 0
        self.__average_buy_price[0] = 0

        for i in range(1, self.simulator.frame.shape[0]):
            self.cummulative_buy_amount[i] = (
                self.cummulative_buy_amount[i - 1]
                + (
                    self.simulator.vars.buy.actual_buy_volume[i]
                    * np.nan_to_num(self.simulator.vars.input.buy_price[i])
                )
                - (
                    self.simulator.vars.sell.actual_sell_volume[i]
                    * self.__average_buy_price[i - 1]
                )
            )

            self.__average_buy_price[i] = np.nan_to_num(
                self.cummulative_buy_amount[i]
                / self.simulator.vars.position.actual_holding_volume[i]
            )

        return self._create_df(
            self.__average_buy_price,
            index=self.simulator.frame.common_index,
            columns=self.simulator.frame.common_columns,
        )

    @property
    def realized_pnl(self) -> pd.DataFrame:
        return self._create_df(
            (
                np.nan_to_num(self.simulator.vars.input.sell_price)
                - self.average_buy_price.shift()
            )
            * self.simulator.vars.sell.actual_sell_volume,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        ).fillna(0)

    @property
    def unrealized_pnl(self) -> pd.DataFrame:
        return self._create_df(
            (np.nan_to_num(self.simulator.vars.input.price) - self.average_buy_price)
            * self.simulator.vars.position.actual_holding_volume,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        ).fillna(0)

    @property
    def target_weight(self) -> pd.DataFrame:
        return self._create_df(
            self.simulator.vars.input.weight,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    @property
    def contribution(self) -> pd.DataFrame:
        pnl = self.realized_pnl + self.unrealized_pnl.diff() - self.cost
        return pnl.div(self.aum.shift()["aum"], axis=0) * 100

    @property
    def contribution_summary(self) -> pd.DataFrame:
        ## Todo: Dividend 추가

        realized_pnl = self.realized_pnl
        unrealized_pnl = self.unrealized_pnl.diff()
        cost = self.cost
        aum = self.aum

        pnl = realized_pnl + unrealized_pnl - cost
        contribution = pnl.div(aum.shift()["aum"], axis=0)
        prev_weight = self.valuation.shift().div(aum.shift()["aum"], axis=0)
        weight = self.valuation.div(aum["aum"], axis=0)

        # 멀티칼럼 DataFrame 생성
        result = pd.concat(
            {
                "pnl": pnl,
                "contribution": contribution * 100,
                "prev_weight": prev_weight * 100,
                "weight": weight * 100,
                "target": self.target_weight * 100,
            },
            axis=1,
        )
        result = result.swaplevel(0, 1, axis=1)
        result = result.sort_index(axis=1)
        result = result.reindex(
            columns=[
                "pnl",
                "contribution",
                "prev_weight",
                "weight",
                "target",
            ],
            level=1,
        )
        return result
