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
| Butterfly | `Option(strike=98, premium=4, kind='call') -2*Option(strike=100, premium=2.5, kind='call') + Option(strike=102, premium=1.5, kind='call')` | ![Butterfly](media/butterfly.png) |
| Bull Call | `Option(strike=95, premium=6, kind='call') - Option(strike=105, premium=2, kind='call')` | ![Bull Call](media/bull_call.png) |
| Protective Put | `Spot(price=100) + Option(strike=95, premium=3, kind='put')` | ![Protective Put](media/protective_put.png) |
| Iron Condor | `Option(strike=96, premium=1) - Option(strike=98, premium=2) - Option(strike=102, premium=104) + Option(strike=110, premium=1)` | ![Iron Condor](media/iron_condor.png) |

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