# XNO API Library

XNO API is a Python package for retrieving financial data from multiple sources.

## Installation

```sh
pip install xnoapi
```

## Usage

```sh
from xnoapi import client
from xnoapi.vn.data import stock, derivatives

client(apikey="...")

stock.list_liquid_asset()
stock.get_hist("VIC", "1D")
```
