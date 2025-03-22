import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid


class EchartCalculator:
    def __init__(self, calc_name, chart_data, slider_key, render_time, max_capacity):
        key = str(uuid.uuid4())
        with st.expander(f"{calc_name} Calculator", expanded=False):
            self.col1, self.col2 = st.columns([1, 3])
            with self.col1:
                st.write("📝 Calculator")
                invest_year = st.slider(
                    "Invest Year",
                    1,
                    30,
                    1,
                    key=f"invest_year_{slider_key}_{render_time}",
                )
                capital = st.slider(
                    "Capital",
                    1,
                    max_capacity,
                    1,
                    key=f"capital_{slider_key}_{render_time}",
                )
                flat = st.slider(
                    "Flat Rate", -5, 5, 0, key=f"flat_{slider_key}_{render_time}"
                )

            with self.col2:
                st.write("📝 Calculator")
                """
                        计算未来 t 年后财富的变化，带有置信区间。

                        参数:
                        - n: 本金 (元)
                        - t: 投资期限 (年)
                        - i: 通货膨胀/紧缩率（百分比，如 2% 输入 2）
                        - daily_returns: 过去一年的每日收益率列表 (小数形式)

                        返回:
                        - 未来 t 年的财富曲线 (包含置信区间)
                    """
                # 计算过去一年的平均日收益率
                chart_data = chart_data.tail(365)
                avg_daily_return = np.mean(chart_data.daily_return)

                # 计算过去一年的日度收益波动率（标准差）
                daily_fluc = np.std(chart_data.daily_return)

                # 计算未来每一天的财富变化
                days = np.arange(1, invest_year * 365 + 1)
                # 生成格式化日期版本
                last_index = chart_data.index[-1]
                start_date = datetime.strptime(
                    chart_data.loc[last_index, "date"], "%Y-%m-%d"
                )
                formatted_dates = [
                    start_date + timedelta(days=int(day)) for day in days
                ]

                # 将格式化日期转换为字符串（可选）
                formatted_dates_str = [
                    date.strftime("%Y-%m-%d") for date in formatted_dates
                ]
                wealth = (
                    capital
                    * (1 + avg_daily_return) ** days
                    * (1 - flat / 100) ** (days / 365)
                )
                confidence_interval = 1.96 * daily_fluc * np.sqrt(days / 365)
                upper_bound = wealth * np.exp(confidence_interval)
                lower_bound = wealth * np.exp(-confidence_interval)
                chart_data = pd.DataFrame(
                    {
                        "days": formatted_dates_str,
                        "wealth": wealth,
                        "upper": upper_bound,
                        "lower": lower_bound,
                    }
                )
                st.line_chart(chart_data, x="days", y=["upper", "wealth", "lower"])
