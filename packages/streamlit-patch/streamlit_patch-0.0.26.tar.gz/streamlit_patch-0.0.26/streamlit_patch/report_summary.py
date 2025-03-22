from datetime import datetime, timedelta
import uuid
import numpy as np
import pandas as pd
import sqlite3
import streamlit as st

from .db_connector import search_by_product_name


@st.fragment
def dynamic_inputs(products, max_capital, key):
    input_vals = []
    for idx, product in enumerate(products):
        if idx == len(products) - 1:
            product_value = st.number_input(
                product,
                0,
                max_capital - sum(input_vals),
                value=max_capital - sum(input_vals),
                key=f"input_{product}_{key}",
            )
        else:
            product_value = st.number_input(
                product,
                0,
                max_capital - sum(input_vals),
                key=f"input_{product}_{key}",
            )

        input_vals.append(product_value)
    # 输出当前结果
    slider_dict = dict(zip(products, input_vals))
    total = sum(slider_dict.values())
    # 验证
    if total <= max_capital:
        st.success(f"🔢 总和：{total}")
    else:
        st.error(f"⚠️ 总和异常：{total}")
    return slider_dict


class EchartReportCalculator:
    def __init__(
        self, ccb_db_path, fund_db_path, slider_key, products=[], max_capital=100000
    ):
        key = str(uuid.uuid4())
        with st.container():
            self.col1, self.col2, self.col3 = st.columns([3, 5, 8])
            with self.col1:
                st.write("📝 Calculator")
                invest_year = st.slider(
                    "Invest Year", 1, 30, 1, key=f"invest_year_{slider_key}"
                )
                capital = st.slider(
                    "Capital", len(products), max_capital, key=f"capital_{slider_key}"
                )
                flat = st.slider("Flat Rate", -5, 5, 0, key=f"flat_{slider_key}")
            with self.col2:
                with st.container(height=330, border=False):
                    if len(products) > 0:
                        input_dict = dynamic_inputs(
                            products, max_capital=capital, key=slider_key
                        )
                        st.button("Update", key=slider_key)
            with self.col3:
                st.write("📝 Calculator")
                wealth = np.zeros(invest_year * 365 - 1)
                for key in input_dict:
                    # key 查询数据库
                    # input_dict[key] capital
                    chart_data = search_by_product_name(ccb_db_path, fund_db_path, key)
                    chart_data = chart_data.tail(365)
                    avg_daily_return = np.mean(chart_data.daily_return)
                    # 计算未来每一天的财富变化
                    days = np.arange(1, invest_year * 365)
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

                    wealth += (
                        input_dict[key]
                        * (1 + avg_daily_return) ** days
                        * (1 - flat / 100) ** (days / 365)
                    )
                chart_data = pd.DataFrame(
                    {
                        "days": formatted_dates_str,
                        "wealth": wealth,
                    }
                )
                st.line_chart(chart_data, x="days", y=["wealth"])
                # if sum(input_dict.values()) <= capital:
