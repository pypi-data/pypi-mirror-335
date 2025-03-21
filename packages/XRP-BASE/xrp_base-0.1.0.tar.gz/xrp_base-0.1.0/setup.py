from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="XRP-BASE",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "base58",
        "requests",
        "xrpl-py",
        "cryptography",
        "ecdsa",
        "pysha3",
        "web3",
        "ccxt",
        "pycoin",
        "qrcode",
        "mnemonic",
        "pywallet",
        "asyncio",
        "pytest"
    ],
    entry_points={
        "console_scripts": [
            "xrpl-toolkit=xrpl_toolkit.xrp_toolkit:xrp_base"
        ]
    },
    description="A Python package for XRPL transactions and installations.",
    author="Your Name",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6"
)