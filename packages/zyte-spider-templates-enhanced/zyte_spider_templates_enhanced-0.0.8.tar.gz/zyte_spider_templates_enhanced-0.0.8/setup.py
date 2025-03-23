from setuptools import find_packages, setup

setup(
    name="zyte-spider-templates-enhanced",
    version="0.0.8",

    url="https://github.com/felipdc/zyte-spider-templates",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.1",
        "requests>=0.10.1",
        "scrapy>=2.11.0",
        "scrapy-poet>=0.24.0",
        "scrapy-spider-metadata>=0.2.0",
        "scrapy-zyte-api[provider]>=0.23.0",
        "zyte-common-items>=0.23.0",
    ]
)
