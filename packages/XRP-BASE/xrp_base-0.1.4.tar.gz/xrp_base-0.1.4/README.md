# XRPL Toolkit

A powerful Python package for working with XRP transactions, address validation, conversions, and more. This toolkit provides functionalities like generating XRP addresses, checking balances, and processing transactions securely.

## Features

-   Generate and validate XRP addresses
-   Check XRP balance and transaction details
-   Convert XRP to USD
-   Simulate package installations for XRPL-related dependencies
-   Secure transaction processing

## Installation

To install the package, run:

```bash
pip install xrpl-toolkit
```

## Usage

### Command-Line Interface (CLI)

Once installed, you can use the toolkit via the command line:

```bash
xrpl-toolkit
```

It will present a menu with options to generate addresses, check balances, validate addresses, and more.

### Importing in Python

You can also import the package in your Python script:

```bash
from xrpl_toolkit.xrp_toolkit import xrp_toolkit

xrp_toolkit()
```

## Dependencies

The package relies on several key libraries for XRP-related functionalities:
-   xrpl-py – for interacting with the XRP Ledger
-   base58 – for encoding addresses
-   cryptography – for secure transactions
-   web3 – for blockchain integration
-   rich – for enhanced terminal output