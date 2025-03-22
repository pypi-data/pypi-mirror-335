from typing_extensions import TypeVar, Generic, TypedDict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
import numpy as np

class Data(TypedDict):
  final_price: np.ndarray | float

D = TypeVar('D', bound=Data, default=Data, contravariant=True)
D2 = TypeVar('D2', bound=Data, default=Data, contravariant=True)

@dataclass
class Instrument(ABC, Generic[D]):
  quantity: float = field(default=1, kw_only=True)
  @abstractmethod
  def payoff(self, data: D, /) -> np.ndarray:
    ...

  def __add__(self, other: 'Instrument[D2]') -> 'Sum[D2]':
    return Sum([self, other])
  
  def __mul__(self, quantity: float) -> 'Instrument[D]':
    return replace(self, quantity=quantity*self.quantity)
  
  __rmul__ = __mul__

  def __neg__(self) -> 'Instrument[D]':
    return self * -1
  
  def __sub__(self, other: 'Instrument[D2]') -> 'Sum[D2]':
    return self + -other
  
  def __rsub__(self, other: 'Instrument[D2]') -> 'Sum[D2]':
    return -self + other
  
@dataclass
class Sum(Instrument[D]):
  instruments: list[Instrument[D]]
  def payoff(self, data: D) -> np.ndarray:
    return np.sum([instrument.payoff(data) for instrument in self.instruments], axis=0)
  
  def __add__(self, other: 'Instrument[D2]') -> 'Sum[D2]':
    return replace(self, instruments=self.instruments + [other])
  
  def __mul__(self, quantity: float) -> 'Sum[D]':
    return replace(self, instruments=[instrument * quantity for instrument in self.instruments])
  