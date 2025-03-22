from typing import Sequence, TypedDict
from dataclasses import dataclass
import numpy as np
from .instrument import Instrument, Data

class RangeData(Data):
  min_price: float

@dataclass
class SpotLimit(Instrument[RangeData]):
  price: float
  
  def payoff(self, data):
    if data['min_price'] <= self.price:
      return (data['final_price'] - self.price) * self.quantity
    else:
      return np.array(0.)
    
class Candle(TypedDict):
  open: float
  high: float
  low: float
  close: float

class GridData(Data):
  candles: Sequence[Candle]
    
@dataclass
class SpotGrid(Instrument[GridData]):
  buy_price: float
  sell_price: float
  fee: float = 0
  debug: bool = False

  def payoff(self, data: GridData):
    import numpy as np
    payoff = np.zeros_like(data['final_price'])
    bought = False

    def step(price: float) -> bool:
      nonlocal payoff, bought
      if not bought and price <= self.buy_price:
        payoff -= self.buy_price*(1+self.fee)
        if self.debug:
          print('Buying at:', price, 'payoff:', payoff)
        bought = True
        stepped = True
      
      elif bought and price >= self.sell_price:
        payoff += self.sell_price*(1-self.fee)
        if self.debug:
          print('Selling at:', price, 'payoff:', payoff)
        bought = False
        stepped = True

      else:
        stepped = False
      
      return stepped


    for c in data['candles']:
      step(c['open'])
      step(c['high']) or step(c['low']) # type: ignore
      step(c['close'])
      
    if bought:
      payoff += data['final_price']
      if self.debug:
        print(f"Final value: {data['final_price']}, payoff:", payoff)

    return payoff * self.quantity