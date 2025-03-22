from typing_extensions import Literal
from dataclasses import dataclass
import numpy as np
from .instrument import Instrument

@dataclass
class Spot(Instrument):
  price: float
  def payoff(self, data):
    return (data['final_price'] - self.price) * self.quantity

@dataclass
class Option(Instrument):
  strike: float
  premium: float
  kind: Literal['call', 'put']

  def payoff(self, data):
    if self.kind == 'put':
      diff = self.strike - data['final_price']
    else:
      diff = data['final_price'] - self.strike
    rel = np.maximum(diff, 0) - self.premium
    return rel * self.quantity
  
@dataclass
class Future(Instrument):
  price: float
  kind: Literal['long', 'short']
  
  def payoff(self, data):
    sign = 1 if self.kind == 'long' else -1
    return (data['final_price'] - self.price) * self.quantity * sign
  