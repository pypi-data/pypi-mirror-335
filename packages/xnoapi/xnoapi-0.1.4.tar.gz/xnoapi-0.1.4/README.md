# XNO API Library

XNO API is a Python package for retrieving financial data from multiple sources.

## Installation

```sh
pip install xnoapi
```

## Usage

```sh
from xnoapi import client
from xnoapi.vn.data import stocks, derivatives

client(apikey="...")

stocks.list_liquid_asset()
stocks.get_hist("VIC", "1D")
```
