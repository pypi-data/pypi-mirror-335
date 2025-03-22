# import pandas as pd


# def plot_single(self, single_asset):
#     import plotly.graph_objs as go
#     from plotly.subplots import make_subplots

#     assert single_asset in self.simulator.position.columns, (
#         f"{single_asset} should be in position"
#     )
#     assert self.simulator.valuation.size != 0, "Valuation can not empty"

#     non_zero_position = self.simulator.position.loc[
#         :, self.simulator.position.sum() != 0
#     ]
#     if self.simulator.position.shape == self.simulator.valuation.shape:
#         valuation_df = pd.DataFrame(
#             self.simulator.valuation,
#             index=self.simulator.position.index,
#             columns=self.simulator.position.columns,
#         )
#     elif non_zero_position.shape == self.simulator.valuation.shape:
#         valuation_df = pd.DataFrame(
#             self.simulator.valuation,
#             index=non_zero_position.index,
#             columns=non_zero_position.columns,
#         )
#     else:
#         try:
#             non_zero_position = non_zero_position.loc[self.simulator.summary.index,]
#             non_zero_valuation = self.simulator.valuation[
#                 :, np.nansum(self.simulator.valuation, axis=0) != 0
#             ]

#             valuation_df = pd.DataFrame(
#                 non_zero_valuation,
#                 index=non_zero_position.index,
#                 columns=non_zero_position.columns,
#             )
#         except Exception as e:
#             print(e)
#             assert False, (
#                 f"position and valuation shape is different.\nposition {self.simulator.position.shape}; valuation {self.simulator.valuation.shape}"
#             )

#     valuation_single = valuation_df[single_asset]

#     position_single = non_zero_position[single_asset].fillna(0)
#     position_previous = position_single.shift(1)
#     position_next = position_single.shift(-1)

#     # valuation_percent 계산
#     # valuation의 차이로 계산해서 기말에 사고, 기초에 파는 효과로 나옴
#     # 조건 정의 (각각 별도의 Series 사용)
#     position_end = position_single != position_next
#     entry = (position_previous <= 0) & (position_single > 0)
#     short = (position_previous >= 0) & (position_single < 0)
#     add = (
#         (position_single > position_previous)
#         & (position_single != 0)
#         & ~entry
#         & ~short
#         & ~position_end
#     )
#     reduce = (
#         (position_single < position_previous)
#         & (position_single != 0)
#         & ~entry
#         & ~short
#         & ~position_end
#     )

#     signal = np.where(
#         entry,
#         2,
#         np.where(
#             add,
#             1,
#             np.where(reduce, -1, np.where(short, -2, np.where(position_end, 3, 0))),
#         ),
#     )

#     pnl_df = pd.DataFrame(valuation_single)
#     pnl_df["signal_start"] = signal
#     pnl_df["pnl_percent_start"] = (
#         pnl_df[signal != 0][single_asset].pct_change() * 100
#     ).shift(-1)
#     pnl_df["pnl_start"] = pnl_df[(signal != 0)][single_asset].diff().shift(-1)

#     pnl_df["signal_end"] = signal
#     pnl_df["signal_end"] = pnl_df[signal != 0]["signal_end"].shift(1)
#     pnl_df["pnl_percent_end"] = pnl_df[(signal != 0)][single_asset].pct_change() * 100

#     pnl_df["pnl_start"] = np.where(
#         pnl_df["pnl_percent_start"].abs() == 100, 0, pnl_df["pnl_start"]
#     )
#     pnl_df["pnl_start"] = np.where(
#         pnl_df[single_asset] < 0, -pnl_df["pnl_start"], pnl_df["pnl_start"]
#     )
#     pnl_df["pnl_start"] = np.where(
#         (pnl_df["signal_start"] == 3), np.nan, pnl_df["pnl_start"]
#     )
#     pnl_df["pnl_percent_start"] = np.where(
#         pnl_df["pnl_percent_start"].abs() == 100, 0, pnl_df["pnl_percent_start"]
#     )
#     pnl_df["pnl_percent_end"] = np.where(
#         pnl_df["pnl_percent_end"].abs() == 100, 0, pnl_df["pnl_percent_end"]
#     )

#     pnl_df["ffill_signal"] = pnl_df.signal_start.replace(0, np.nan).fillna(
#         method="ffill"
#     )
#     pnl_df["ffill_pnl_percent"] = pnl_df.pnl_percent_start.fillna(method="ffill")

#     fig = make_subplots(
#         rows=3,
#         cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.1,
#         subplot_titles=("Position", "Valuation(Trading)", "Profit And Loss"),
#     )

#     # 선 그래프
#     valuation_line = go.Scatter(
#         x=valuation_single.index,
#         y=valuation_single.values,
#         mode="lines",
#         name="Valuation",
#     )

#     pnl_line = go.Scatter(
#         x=pnl_df["pnl_start"].index,
#         y=pnl_df["pnl_start"].fillna(method="ffill"),
#         mode="lines",
#         name="PNL",
#     )
#     pnl_cumsum_line = go.Scatter(
#         x=pnl_df["pnl_start"].index,
#         y=pnl_df["pnl_start"].fillna(0).cumsum(),
#         mode="lines",
#         name="PNL_cumsum",
#     )

#     # 진입 포인트 (빨간색 세모)
#     trace_entry = go.Scatter(
#         x=pnl_df[pnl_df.signal_start == 2].index,
#         y=pnl_df[pnl_df.signal_start == 2]["pnl_percent_start"],
#         mode="markers",
#         marker=dict(symbol="triangle-up", color="red", size=10),
#         name="Long",
#     )

#     trace_entry2 = go.Scatter(
#         x=pnl_df[pnl_df.signal_end == 2].index,
#         y=pnl_df[pnl_df.signal_end == 2]["pnl_percent_end"],
#         mode="markers",
#         marker=dict(symbol="triangle-up", color="red", size=10),
#         name="Long",
#     )

#     line_entry = go.Scatter(
#         x=pnl_df.index,
#         y=np.where(pnl_df["ffill_signal"] == 2, pnl_df["ffill_pnl_percent"], np.nan),
#         mode="lines",
#         name="Long",
#         line=dict(color="red"),
#     )

#     # 추매 포인트 (빨간색 세모)
#     trace_add = go.Scatter(
#         x=pnl_df[pnl_df.signal_start == 1].index,
#         y=pnl_df[pnl_df.signal_start == 1]["pnl_percent_start"],
#         mode="markers",
#         marker=dict(symbol="triangle-up", color="red", size=5),
#         name="Add",
#     )

#     trace_add2 = go.Scatter(
#         x=pnl_df[pnl_df.signal_end == 1].index,
#         y=pnl_df[pnl_df.signal_end == 1]["pnl_percent_end"],
#         mode="markers",
#         marker=dict(symbol="triangle-up", color="red", size=5),
#         name="Add",
#     )

#     line_add = go.Scatter(
#         x=pnl_df.index,
#         y=np.where(pnl_df["ffill_signal"] == 1, pnl_df["ffill_pnl_percent"], np.nan),
#         mode="lines",
#         name="Add",
#         line=dict(color="rgba(255, 0, 0, 0.2)"),
#     )

#     # 매도 포인트 (파란색 세모)
#     trace_short = go.Scatter(
#         x=pnl_df[pnl_df.signal_start == -2].index,
#         y=pnl_df[pnl_df.signal_start == -2]["pnl_percent_start"],
#         mode="markers",
#         marker=dict(symbol="triangle-down", color="blue", size=10),
#         name="Short",
#     )

#     trace_short2 = go.Scatter(
#         x=pnl_df[pnl_df.signal_end == -2].index,
#         y=pnl_df[pnl_df.signal_end == -2]["pnl_percent_end"],
#         mode="markers",
#         marker=dict(symbol="triangle-down", color="blue", size=10),
#         name="Short",
#     )

#     line_short = go.Scatter(
#         x=pnl_df.index,
#         y=np.where(pnl_df["ffill_signal"] == -2, pnl_df["ffill_pnl_percent"], np.nan),
#         mode="lines",
#         name="Short",
#         line=dict(color="blue"),
#     )

#     # 매도 포인트 (파란색 세모)
#     trace_down = go.Scatter(
#         x=pnl_df[pnl_df.signal_start == -1].index,
#         y=pnl_df[pnl_df.signal_start == -1]["pnl_percent_start"],
#         mode="markers",
#         marker=dict(symbol="triangle-down", color="blue", size=5),
#         name="Reduce",
#     )

#     trace_down2 = go.Scatter(
#         x=pnl_df[pnl_df.signal_end == -1].index,
#         y=pnl_df[pnl_df.signal_end == -1]["pnl_percent_end"],
#         mode="markers",
#         marker=dict(symbol="triangle-down", color="blue", size=5),
#         name="Reduce",
#     )

#     line_down = go.Scatter(
#         x=pnl_df.index,
#         y=np.where(pnl_df["ffill_signal"] == -1, pnl_df["ffill_pnl_percent"], np.nan),
#         mode="lines",
#         name="Reduce",
#         line=dict(color="rgba(0, 0, 255, 0.2)"),
#     )

#     fig.add_trace(trace_entry, row=1, col=1)
#     fig.add_trace(trace_entry2, row=1, col=1)
#     fig.add_trace(trace_add, row=1, col=1)
#     fig.add_trace(trace_add2, row=1, col=1)
#     fig.add_trace(trace_down, row=1, col=1)
#     fig.add_trace(trace_down2, row=1, col=1)
#     fig.add_trace(trace_short, row=1, col=1)
#     fig.add_trace(trace_short2, row=1, col=1)

#     fig.add_trace(line_entry, row=1, col=1)
#     fig.add_trace(line_add, row=1, col=1)
#     fig.add_trace(line_down, row=1, col=1)
#     fig.add_trace(line_short, row=1, col=1)

#     fig.add_trace(valuation_line, row=2, col=1)

#     fig.add_trace(pnl_line, row=3, col=1)
#     fig.add_trace(pnl_cumsum_line, row=3, col=1)

#     # 레이아웃 설정
#     fig.update_layout(height=600, hovermode="x unified")

#     # 그래프 그리기
#     fig.show()
