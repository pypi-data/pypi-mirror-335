from dataclasses import dataclass
import numpy as np
from .instrument import Instrument

@dataclass
class SellHighDI(Instrument):
  """Sell High Dual Investment"""
  rate: float
  """interest rate (e.g 0.05)"""
  strike: float
  price: float
  def payoff(self, data):
    rel = np.minimum(data['final_price'], self.strike)*(1+self.rate) - self.price
    return rel * self.quantity
  
@dataclass
class BuyLowDI(Instrument):
  """Buy Low Dual Investment"""
  rate: float
  """interest rate (e.g 0.05)"""
  strike: float
  price: float

  def payoff(self, data):
    rel = np.where(
      data['final_price'] < self.strike,
      data['final_price']*(1+self.rate) - self.strike,
      self.rate*self.price
    )
    return rel * self.quantity
  
@dataclass
class SmartLeverage(Instrument):
  """https://www.bybit.com/en/earn/smart-leverage"""
  leverage: float
  breakeven: float

  def payoff(self, data):
    gain = self.leverage * (data['final_price'] - self.breakeven) / self.breakeven
    return np.maximum(gain, -self.quantity)