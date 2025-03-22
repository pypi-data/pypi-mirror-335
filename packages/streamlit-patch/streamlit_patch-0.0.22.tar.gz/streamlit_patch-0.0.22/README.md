# streamlit_patch

```shell
pip install streamlit_patch
```

## 用法
- 可以将markdown中的《text》标签替换为按钮，点击按钮后会弹出提示框。
- 可以将/echarts[key]替换为一个echart图表，该图标为一个line chart
- 可以使用/itable[key]替换为一个可交互的table组件

key可以用作网络请求的查询参数，用于获取图表数据。


```python
from streamlit_patch import process_markdown


def main():
    # 示例Markdown文本
    markdown_text = """# The Growing Landscape of Investment Firms: A Spotlight on Leading Fund Management Companies
As the global financial markets continue to evolve, fund management companies have become crucial players in shaping investment strategies and driving economic growth. These firms manage trillions of dollars in assets across various types of funds, including mutual funds, hedge funds, exchange-traded funds (ETFs), and private equity. Below is an overview of some of the leading fund management companies that are paving the way in the investment world.
## 1. BlackRock: The World’s Largest Asset Manager
《BlackRock Inc.》, founded in 1988, is the largest investment management firm in the world, with assets under management (AUM) exceeding $9 trillion. The company’s diverse portfolio includes a range of equity, fixed-income, and alternative investment strategies. BlackRock is renowned for its leadership in sustainable investing, having launched multiple Environmental, Social, and Governance (ESG) investment funds. With a global presence, the firm continues to innovate in risk management and passive investment solutions.
## 2. **Vanguard Group: A Pioneer of Low-Cost Investing**
《Vanguard Group》Founded in 1975 by John C./echarts[123] Bogle, Vanguard is known for its low-cost investment approach/itable[456] and has become synonymous with index investing. Vanguard’s philosophy of offering low-fee index funds has revolutionized the investing landscape, attracting millions of individual and institutional investors. Today, Vanguard manages over $7 trillion in assets, with a wide range of mutual funds, ETFs, and retirement solutions. The firm has been a key advocate for investor-friendly policies and is recognized for its focus on long-term value creation.
"""
    # 在 Streamlit 中渲染修改后的 Markdown 内容
    process_markdown(markdown_text)

    # 定义一个替换<text>标签为按钮的函数


# 运行主程序
if __name__ == "__main__":
    main()

```
