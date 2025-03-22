# Finalysis
A python library for financial instrument payoff analysis.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://finalysis-python.streamlit.app/)

## 🚀 Quickstart

```python
from finalysis import Spot, Option, plot

current_price = 100
strategy = Spot(price=current_price) + Option(premium=5, strike=100, kind='put')

plot.payoff(strategy, current_price)
```

![Payoff Diagram](media/payoff.png)

## 📦 Features

- Core primitives: Spot, Option, Future, and structured products like DualInvestment, SmartLeverage
- Strategy composition using +, -, * operators
- Streamlit UI to build strategies interactively (https://finalysis-python.streamlit.app/)
- Plotting payoff diagrams

## 📈 Examples

| Strategy | Code | Payoff |
| --- | --- | --- |
| Butterfly | `Spot() + 2 * Option(strike=100) - Option(strike=110)` | ![Butterfly](media/payoff.png) |

## 🔧 Other Instruments

```python
from finalysis.instruments import (
  SellHighDI,
  BuyLowDI,
  SmartLeverage,
  SpotGrid,
  SpotLimit
)
```