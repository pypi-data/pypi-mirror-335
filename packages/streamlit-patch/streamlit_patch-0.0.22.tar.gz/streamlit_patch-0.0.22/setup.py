from setuptools import setup, find_packages

setup(
    name="streamlit_patch",  # 这里是pip项目发布的名称
    version="0.0.22",  # 版本号，数值大的会优先被pip
    keywords=("pip", "streamlit_patch"),
    description="A streamlit patch for markdown render",
    long_description="A streamlit patch for markdown render",
    license="MIT Licence",
    url="https://github.com/qixiaojian310/streamlit_patch",  # 项目相关文件地址，一般是github
    author="qixiaojian310",
    author_email="qixiaojian00310@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "streamlit==1.40.1",  # 指定streamlit版本
        "streamlit-echarts==0.4.0",  # 指定streamlit-echarts版本
        "streamlit-float==0.3.5",  # 指定streamlit-float版本
        "streamlit_js_eval==0.1.7",
        "pandas<=2.0.3",
        "numpy<=1.24.4",
    ],  # 这个项目需要的第三方库
)
