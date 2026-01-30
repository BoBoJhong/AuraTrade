"""
Technical Indicators Service
Calculate technical indicators for stock analysis using pure pandas/numpy
追溯: US-03, FR-04
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """Service for calculating technical indicators"""
    
    @staticmethod
    def calculate_ma(data: List[Dict[str, Any]], periods: List[int] = [5, 10, 20, 60]) -> Dict[str, List[Optional[float]]]:
        """
        Calculate Moving Averages
        
        Args:
            data: List of historical data with 'close' prices
            periods: List of MA periods (default: 5, 10, 20, 60)
        
        Returns:
            Dictionary with MA values for each period
        """
        if not data:
            return {f"ma{p}": [] for p in periods}
        
        df = pd.DataFrame(data)
        if 'close' not in df.columns:
            return {f"ma{p}": [] for p in periods}
        
        result = {}
        for period in periods:
            ma = df['close'].rolling(window=period).mean()
            result[f"ma{period}"] = [None if pd.isna(x) else float(x) for x in ma]
        
        return result
    
    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(data: List[Dict[str, Any]], 
                      fast: int = 12, 
                      slow: int = 26, 
                      signal: int = 9) -> Dict[str, List[Optional[float]]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: List of historical data with 'close' prices
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
        
        Returns:
            Dictionary with MACD, signal, and histogram values
        """
        if not data:
            return {"macd": [], "signal": [], "histogram": []}
        
        df = pd.DataFrame(data)
        if 'close' not in df.columns:
            return {"macd": [], "signal": [], "histogram": []}
        
        # Calculate EMAs
        ema_fast = TechnicalIndicatorService.calculate_ema(df['close'], fast)
        ema_slow = TechnicalIndicatorService.calculate_ema(df['close'], slow)
        
        # MACD Line
        macd_line = ema_fast - ema_slow
        
        # Signal Line
        signal_line = TechnicalIndicatorService.calculate_ema(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            "macd": [None if pd.isna(x) else float(x) for x in macd_line],
            "signal": [None if pd.isna(x) else float(x) for x in signal_line],
            "histogram": [None if pd.isna(x) else float(x) for x in histogram]
        }
    
    @staticmethod
    def calculate_rsi(data: List[Dict[str, Any]], period: int = 14) -> List[Optional[float]]:
        """
        Calculate RSI (Relative Strength Index)
        
        Args:
            data: List of historical data with 'close' prices
            period: RSI period (default: 14)
        
        Returns:
            List of RSI values
        """
        if not data:
            return []
        
        df = pd.DataFrame(data)
        if 'close' not in df.columns:
            return []
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return [None if pd.isna(x) else float(x) for x in rsi]
    
    @staticmethod
    def calculate_kdj(data: List[Dict[str, Any]], 
                     k_period: int = 9, 
                     d_period: int = 3) -> Dict[str, List[Optional[float]]]:
        """
        Calculate KDJ (Stochastic Oscillator)
        
        Args:
            data: List of historical data with 'high', 'low', 'close' prices
            k_period: K line period (default: 9)
            d_period: D line period (default: 3)
        
        Returns:
            Dictionary with K, D, J values
        """
        if not data:
            return {"k": [], "d": [], "j": []}
        
        df = pd.DataFrame(data)
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            return {"k": [], "d": [], "j": []}
        
        # Calculate RSV (Raw Stochastic Value)
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        rsv = 100 * (df['close'] - low_min) / (high_max - low_min)
        
        # Calculate K, D, J
        k = rsv.ewm(com=2).mean()  # K = SMA(RSV, 3)
        d = k.ewm(com=2).mean()     # D = SMA(K, 3)
        j = 3 * k - 2 * d           # J = 3K - 2D
        
        return {
            "k": [None if pd.isna(x) else float(x) for x in k],
            "d": [None if pd.isna(x) else float(x) for x in d],
            "j": [None if pd.isna(x) else float(x) for x in j]
        }
    
    @staticmethod
    def calculate_all_indicators(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate all technical indicators at once
        
        Args:
            data: List of historical data with OHLCV
        
        Returns:
            Dictionary containing all indicators
        """
        return {
            "ma": TechnicalIndicatorService.calculate_ma(data),
            "macd": TechnicalIndicatorService.calculate_macd(data),
            "rsi": TechnicalIndicatorService.calculate_rsi(data),
            "kdj": TechnicalIndicatorService.calculate_kdj(data)
        }
