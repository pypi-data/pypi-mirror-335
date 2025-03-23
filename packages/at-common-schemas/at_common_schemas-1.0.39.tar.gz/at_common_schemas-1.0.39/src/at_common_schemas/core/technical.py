from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

# Technical Indicators
class StockTechnicalIndicators(BaseSchema):
    date: datetime = Field(..., description="Date of the data")
    sma5: float = Field(..., description="Simple Moving Average over 5 days")
    sma10: float = Field(..., description="Simple Moving Average over 10 days")
    sma20: float = Field(..., description="Simple Moving Average over 20 days")
    ema5: float = Field(..., description="Exponential Moving Average over 5 days")
    ema10: float = Field(..., description="Exponential Moving Average over 10 days")
    ema20: float = Field(..., description="Exponential Moving Average over 20 days")
    rsi: float = Field(..., description="Relative Strength Index")
    macd: float = Field(..., description="Moving Average Convergence Divergence")
    macd_signal: float = Field(..., description="Signal line for MACD")
    macd_hist: float = Field(..., description="MACD histogram")
    slowk: float = Field(..., description="Stochastic %K")
    slowd: float = Field(..., description="Stochastic %D")
    upper_band: float = Field(..., description="Upper Bollinger Band")
    middle_band: float = Field(..., description="Middle Bollinger Band")
    lower_band: float = Field(..., description="Lower Bollinger Band")
    obv: int = Field(..., description="On-Balance Volume")
    roc: float = Field(..., description="Rate of Change")
    willr: float = Field(..., description="Williams %R")
    atr: float = Field(..., description="Average True Range")

# Technical Patterns
class StockTechnicalPatterns(BaseSchema):
    date: datetime = Field(..., description="Date of the data")
    ma_cross_5_10: int = Field(..., description="Signal for 5-day MA crossing 10-day MA: 1 (5-day crosses above), -1 (5-day crosses below), 0 (no cross)")
    ma_cross_10_20: int = Field(..., description="Signal for 10-20 MA crossover, 1 for cross above, -1 for cross below, 0 for no crossover")
    rsi_overbought: int = Field(..., description="Signal for RSI overbought condition: 1 (RSI > 70), -1 (RSI < 30), 0 (neither)")
    rsi_oversold: int = Field(..., description="Signal for RSI oversold condition, 1 for overbought, -1 for oversold, 0 for no signal")
    macd_crossover: int = Field(..., description="Signal for MACD line crossing signal line: 1 (bullish cross), -1 (bearish cross), 0 (no cross)")
    stoch_crossover: int = Field(..., description="Signal for Stochastic crossover, 1 for crossover, -1 for no crossover, 0 for no signal")
    bb_breakout_up: int = Field(..., description="Signal for Bollinger Band breakout upwards, 1 for breakout, -1 for no breakout, 0 for no signal")
    bb_breakout_down: int = Field(..., description="Signal for Bollinger Band breakout downwards, 1 for breakout, -1 for no breakout, 0 for no signal")
    volume_spike: int = Field(..., description="Signal for volume spike, 1 for spike, -1 for no spike, 0 for no signal")
    higher_high: int = Field(..., description="Signal for higher high, 1 for higher high, -1 for no higher high, 0 for no signal")
    lower_low: int = Field(..., description="Signal for lower low, 1 for lower low, -1 for no lower low, 0 for no signal")