from finter.backtest.core import (
    calculate_buy_sell_volumes,
    execute_transactions,
    update_aum,
    update_target_volume,
    update_valuation_and_cash,
)
from finter.backtest.v0.simulators.base import BaseBacktestor


class IDFundBacktestor(BaseBacktestor):
    settlement_days = 4

    def run(self):
        for i in range(1, self.frame.shape[0]):
            self.vars.position.target_volume[i] = update_target_volume(
                self.vars.input.weight[i],
                self.vars.result.aum[i - 1, 0],
                self.vars.input.price[i - 1],
                self.vars.input.weight[i - 1],
                self.vars.position.target_volume[i - 1],
                i == 1,
                self.execution.rebalancing_method,
                self.vars.input.rebalancing_mask[i]
                if self.execution.rebalancing_method in ["W", "M", "Q"]
                else 0,
            )

            (
                self.vars.buy.target_buy_volume[i],
                self.vars.sell.target_sell_volume[i],
                self.vars.sell.actual_sell_volume[i],
            ) = calculate_buy_sell_volumes(
                self.vars.position.target_volume[i],
                self.vars.position.actual_holding_volume[i - 1],
                self.vars.input.weight[i],
                volume_capacity=self.vars.input.volume_capacity[i],
            )

            (
                self.vars.sell.actual_sell_amount[i],
                self.vars.buy.available_buy_amount[i, 0],
                self.vars.buy.actual_buy_volume[i],
                self.vars.buy.actual_buy_amount[i],
            ) = execute_transactions(
                self.vars.sell.actual_sell_volume[i],
                self.vars.input.buy_price[i],
                self.cost.buy_fee_tax,
                self.vars.input.sell_price[i],
                self.cost.sell_fee_tax,
                self.vars.result.cash[i - 1, 0],
                self.vars.buy.target_buy_volume[i],
                actual_sell_amount=self.vars.sell.actual_sell_amount,
                settlement_days=self.settlement_days,
                current_index=i,
            )

            (
                self.vars.position.actual_holding_volume[i],
                self.vars.result.valuation[i],
                self.vars.result.cash[i, 0],
                self.vars.result.dividend[i],
            ) = update_valuation_and_cash(
                self.vars.position.actual_holding_volume[i - 1],
                self.vars.result.valuation[i - 1],
                self.vars.buy.actual_buy_volume[i],
                self.vars.sell.actual_sell_volume[i],
                self.vars.input.price[i],
                self.vars.buy.available_buy_amount[i, 0],
                self.vars.buy.actual_buy_amount[i],
                self.vars.input.dividend_ratio[i],
                self.execution.drip,
                self.cost.dividend_tax,
            )

            (
                self.vars.result.cash[i, 0],
                self.vars.result.aum[i, 0],
            ) = update_aum(
                self.vars.result.cash[i, 0],
                self.vars.result.valuation[i],
                self.vars.input.money_flow[i],
            )

        summary = self._summary
        if not self.optional.debug:
            self._clear_all_variables()
        return summary
