import setuptools

with open("/www/files/Stock/Utils/StockClockUtils/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StockClockUtils",
    version="0.0.3",
    author="Qi Yueran",
    author_email="1206585163@qq.com",
    description="Utils for Stock-Clock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['StockClockUtils'],
    install_requires=['requests','polars','pymysql','sqlalchemy','numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
