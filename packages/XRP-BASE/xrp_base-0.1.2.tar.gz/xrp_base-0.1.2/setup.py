from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="XRP-BASE",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        'requests',
        'base58'
        'pandas',
        'numpy',
        'tqdm',
        'matplotlib',
        'scikit-learn',
        'flask',
        'beautifulsoup4',
        'pytest',
        'pydantic',
        'asyncio'
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