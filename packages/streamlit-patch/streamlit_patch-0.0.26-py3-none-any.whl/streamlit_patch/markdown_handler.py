import re

import streamlit as st
import uuid
from .calculator import EchartCalculator
from .db_connector import search_by_product_name

# 定义一个函数封装组件的逻辑


class EchartsHandlerContainer:
    def __init__(self):
        self.is_last = False
        self.text_container = st.empty()

    db_path = ""
    CCB_path = ""
    sidebar_container = None
    all_button = []

    @staticmethod
    def init(db_path, CCB_path):
        EchartsHandlerContainer.CCB_path = CCB_path
        EchartsHandlerContainer.db_path = db_path
        with st.sidebar:
            EchartsHandlerContainer.sidebar_container = st.empty()

    def display_echarts_with_toggle(
        self,
        slider_key,
        render_time,
        max_capital,
        button_name="Click me",
    ):
        chart_data = search_by_product_name(
            EchartsHandlerContainer.CCB_path,
            EchartsHandlerContainer.db_path,
            button_name,
        )

        # 按钮点击时改变变量的值
        with st.popover(button_name, use_container_width=True).container(height=280):
            # 根据变量显示或隐藏容器
            container = st.container(key=uuid.uuid4())
            with container:
                # logger.info(f"chart_data: {chart_data}")
                if chart_data.empty:
                    st.warning("未找到基金数据")
                else:
                    self.calculator = EchartCalculator(
                        button_name, chart_data, slider_key, render_time, max_capital
                    )
                    st.line_chart(
                        chart_data,
                        y=["unit_net_worth", "acc_net_worth"],
                        x="date",
                        x_label=button_name,
                        y_label="盈利趋势",
                        height=260,
                        width=400,
                        use_container_width=False,
                    )

    def cus_write(self, text):
        # 使用正则表达式按 <link> 分割文本
        parts = re.split(
            r"(《.*?》|/echarts\[[^\]]+\]|/itable\[[^\]]+\])",
            text,
            flags=re.MULTILINE,
        )  # 现在匹配标签和指令
        button_name = ""
        compute_content = ""
        for part in parts:
            if part.startswith("《") and part.endswith("》"):  # 判断是否为《text》标签
                button_name = part[1:-1]
                compute_content = compute_content + button_name
                # 如果 button_name 已经存在，则先删除它再添加到末尾
                if button_name in EchartsHandlerContainer.all_button:
                    EchartsHandlerContainer.all_button.remove(button_name)

                # 重新添加到列表末尾
                EchartsHandlerContainer.all_button.append(button_name)
            else:
                compute_content = compute_content + part
                # 显示图表
        with self.text_container:
            st.write(compute_content, unsafe_allow_html=True)

    def write(self, text, render_time, is_last=False):
        self.is_last = is_last
        self.cus_write(text)
        # print("render_time", render_time)

    def show_sidebar_widget(self, render_time, max_capital=100000):
        with EchartsHandlerContainer.sidebar_container:
            once_container = st.container()
            with once_container:
                st.write(
                    "识别到您对以下产品可能有投资需要，您可以进一步点击产品查看产品的收益率变化，净值走势等详细信息。"
                )
                # print(EchartsHandlerContainer.all_button)
                for button_name in EchartsHandlerContainer.all_button:
                    self.display_echarts_with_toggle(
                        button_name, render_time, max_capital, button_name
                    )

    def error(self, text):
        st.error(text)
