import streamlit as st
from streamlit_echarts import st_echarts


def display_echarts(data: list):
    options = {
        "title": {"left": "center", "text": "Large Ara Chart"},
        "toolbox": {
            "feature": {
                "dataZoom": {"yAxisIndex": "none"},
                "restore": {},
                "saveAsImage": {},
            }
        },
        "xAxis": {"type": "time", "boundaryGap": False},
        "yAxis": {"type": "value", "boundaryGap": [0, "100%"]},
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 20},
            {"start": 0, "end": 20},
        ],
        "series": [
            {
                "name": "Fake Data",
                "type": "line",
                "smooth": True,
                "symbol": "none",
                "areaStyle": {},
                "data": data,
            }
        ],
    }
    container = st.container()
    with container:
        st_echarts(options=options)
