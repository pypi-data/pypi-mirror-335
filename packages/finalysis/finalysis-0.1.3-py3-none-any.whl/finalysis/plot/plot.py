import numpy as np
import plotly.graph_objects as go
from finalysis.instruments import Instrument

def payoff(
  strategy: Instrument,
  price: float,
  *,
  min_price: float | None = None,
  max_price: float | None = None,
  steps: int = 1000,
  relative: bool = False,
  show_current_price: bool = True,
) -> go.Figure:
  """
  Generate an interactive payoff plot for a strategy.

  Parameters:
  - strategy: an Instrument implementing .payoff
  - price: current price of the underlying
  - min_price, max_price: price range for the plot (optional)
  - steps: number of points in the plot
  - relative: show PnL as a percentage of current price
  - show_current_price: add a vertical line for current price

  Returns:
  - plotly.graph_objects.Figure
  """
  X = np.linspace(min_price or 0.75 * price, max_price or 1.5 * price, steps)
  Y = strategy.payoff({'final_price': X})

  if relative:
      Y = Y / price

  fig = go.Figure()

  fig.add_trace(go.Scatter(
      x=X, y=Y,
      mode='lines',
      name='PnL',
      hovertemplate='Final Price: %{x:.2f}<br>PnL: %{y:.2f}<extra></extra>'
  ))

  if show_current_price:
      fig.add_vline(
          x=price,
          line=dict(color='red', dash='dash'),
          annotation_text="Current Price",
          annotation_position="top right"
      )

  fig.update_layout(
      title="Strategy Payoff",
      xaxis_title="Final Price",
      yaxis_title="PnL" if not relative else "Relative PnL",
      hovermode="x unified",
      showlegend=True,
      template="plotly_white"
  )

  return fig
