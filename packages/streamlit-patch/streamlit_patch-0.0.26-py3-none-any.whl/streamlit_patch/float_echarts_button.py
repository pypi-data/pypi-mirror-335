import streamlit as st
from streamlit_float import *
from streamlit_echarts import st_echarts
import streamlit as st


# 定义一个函数封装组件的逻辑
def display_echarts_with_toggle(options, button_name="Click me", button_key=""):
    options["title"]["text"] = button_name
    # 初始化float功能
    float_init()

    # 使用 session_state 来保存容器显示状态
    if button_key not in st.session_state:
        st.session_state[button_key] = False  # 默认不显示容器

    # 按钮点击时改变变量的值
    if st.button(button_name):
        st.session_state[button_key] = not st.session_state[button_key]

    # 根据变量显示或隐藏容器
    if st.session_state[button_key]:
        container = st.container()
        with container:
            st_echarts(options=options)
        container.float(
            f"background-color: white; transform: translate(calc({len(button_name) + 2} * 10px), -60px); box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 10px;padding: 10px; position: absolute;"
        )
