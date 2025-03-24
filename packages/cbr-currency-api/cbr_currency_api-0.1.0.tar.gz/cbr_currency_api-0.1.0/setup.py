from setuptools import setup, find_packages

setup(
    name="cbr_currency_api",
    version="0.1.0",
    description="Библиотека для работы с курсами валют ЦБ РФ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Shellect",
    author_email="evstyunino@gmail.com",
    url="https://github.com/shellect/cbr-currency-api",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "cachetools",
        "tenacity",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)