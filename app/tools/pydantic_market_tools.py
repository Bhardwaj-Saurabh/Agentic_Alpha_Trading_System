"""Market data and analysis tools for PydanticAI"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import yfinance as yf
import sys
import os
from data.market_data import MarketData

market_data = MarketData()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.trading_models import (
    StockDataResponse, FibonacciResponse, SentimentResponse, 
    ComplianceResponse, TradingSignal, Sentiment, ComplianceStatus,
    PriceInfo, TechnicalIndicators, VolumeAnalysis
)

def get_stock_data(symbol: str, period: str = "1mo", data: pd.DataFrame = None) -> StockDataResponse:
    """Fetch stock data from Yahoo Finance with technical indicators.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y')
    
    Returns:
        Structured stock data with technical indicators
    """
    try:
        # Try to fetch real data first
        if data is None:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
        
            if data.empty:
                # Generate demo data if real data unavailable
                from data.demo_data import generate_demo_stock_data
                print(f"Using demo data for {symbol}")
                data = generate_demo_stock_data(symbol, 30)
            
            # Calculate technical indicators
            data = market_data.calculate_technical_indicators(data)
        
        # Create structured response
        price_info = PriceInfo(
            current_price=float(data['Close'].iloc[-1]),
            previous_close=float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[-1]),
            high_52w=float(data['Close'].max()),
            low_52w=float(data['Close'].min()),
            volume_avg=float(data['Volume'].mean())
        )
        
        tech_indicators = TechnicalIndicators(
            rsi=float(data['RSI'].iloc[-1]) if 'RSI' in data.columns and pd.notna(data['RSI'].iloc[-1]) else None,
            macd=float(data['MACD'].iloc[-1]) if 'MACD' in data.columns and pd.notna(data['MACD'].iloc[-1]) else None,
            macd_signal=float(data['MACD_Signal'].iloc[-1]) if 'MACD_Signal' in data.columns and pd.notna(data['MACD_Signal'].iloc[-1]) else None,
            bb_upper=float(data['BB_Upper'].iloc[-1]) if 'BB_Upper' in data.columns and pd.notna(data['BB_Upper'].iloc[-1]) else None,
            bb_lower=float(data['BB_Lower'].iloc[-1]) if 'BB_Lower' in data.columns and pd.notna(data['BB_Lower'].iloc[-1]) else None,
            bb_middle=float(data['BB_Middle'].iloc[-1]) if 'BB_Middle' in data.columns and pd.notna(data['BB_Middle'].iloc[-1]) else None,
        )
        
        return StockDataResponse(
            symbol=symbol,
            period=period,
            data_points=len(data),
            price_info=price_info,
            technical_indicators=tech_indicators,
            trend_analysis=analyze_price_trend(data),
            volume_analysis=analyze_volume_patterns(data)
        )
        
    except Exception as e:
        # Return minimal response on error
        return StockDataResponse(
            symbol=symbol,
            period=period,
            data_points=0,
            price_info=PriceInfo(current_price=0, previous_close=0, high_52w=0, low_52w=0, volume_avg=0),
            technical_indicators=TechnicalIndicators(),
            trend_analysis="ERROR",
            volume_analysis="ERROR"
        )

def calculate_fibonacci_levels(symbol: str, lookback_days: int = 20) -> FibonacciResponse:
    """Calculate Fibonacci retracement levels for a stock.
    
    Args:
        symbol: Stock symbol
        lookback_days: Number of days to look back for high/low calculation
        
    Returns:
        Structured Fibonacci analysis with trading signal
    """
    try:
        # Get stock data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=f"{lookback_days*2}d")
        
        if data.empty:
            from data.demo_data import generate_demo_stock_data
            data = generate_demo_stock_data(symbol, lookback_days)
        
        # Get recent high and low
        recent_data = data.tail(lookback_days)
        high_price = recent_data['High'].max()
        low_price = recent_data['Low'].min()
        current_price = data['Close'].iloc[-1]
        
        # Calculate Fibonacci levels
        price_range = high_price - low_price
        fib_levels = {
            "0%": high_price,
            "23.6%": high_price - (0.236 * price_range),
            "38.2%": high_price - (0.382 * price_range), 
            "50%": high_price - (0.5 * price_range),
            "61.8%": high_price - (0.618 * price_range),
            "100%": low_price
        }
        
        # Determine trading signal
        signal = TradingSignal.HOLD
        confidence = 0.5
        
        if current_price <= fib_levels["38.2%"] and current_price >= fib_levels["61.8%"]:
            signal = TradingSignal.BUY
            confidence = 0.75
        elif current_price >= fib_levels["23.6%"]:
            signal = TradingSignal.SELL
            confidence = 0.65
            
        return FibonacciResponse(
            symbol=symbol,
            current_price=float(current_price),
            fibonacci_levels={k: float(v) for k, v in fib_levels.items()},
            signal=signal,
            confidence=confidence,
            analysis=f"Price is at {current_price:.2f}, near {find_nearest_fib_level(current_price, fib_levels)}"
        )
        
    except Exception as e:
        return FibonacciResponse(
            symbol=symbol,
            current_price=0.0,
            fibonacci_levels={},
            signal=TradingSignal.HOLD,
            confidence=0.0,
            analysis=f"Error calculating Fibonacci levels: {str(e)}"
        )

def analyze_market_sentiment(symbol: str, timeframe: str = "3d") -> SentimentResponse:
    """Analyze market sentiment using price action and volume patterns.
    
    Args:
        symbol: Stock symbol
        timeframe: Analysis timeframe ('1d', '3d', '7d', '30d')
        
    Returns:
        Structured sentiment analysis
    """
    try:
        # Convert timeframe to period
        period_map = {'1d': '2d', '3d': '5d', '7d': '1mo', '30d': '3mo'}
        period = period_map.get(timeframe, '5d')
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            from data.demo_data import generate_demo_stock_data
            days = {'1d': 5, '3d': 10, '7d': 20, '30d': 60}.get(timeframe, 10)
            data = generate_demo_stock_data(symbol, days)
        
        # Calculate sentiment indicators
        price_change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
        volume_trend = data['Volume'].rolling(window=min(5, len(data))).mean().iloc[-1] / data['Volume'].mean()
        
        # Volatility analysis
        returns = data['Close'].pct_change()
        volatility = returns.std()
        
        # Determine sentiment
        if price_change > 0.05 and volume_trend > 1.2:
            sentiment = Sentiment.VERY_BULLISH
            confidence = 0.85
        elif price_change > 0.02:
            sentiment = Sentiment.BULLISH
            confidence = 0.70
        elif price_change < -0.05 and volume_trend > 1.2:
            sentiment = Sentiment.VERY_BEARISH
            confidence = 0.85
        elif price_change < -0.02:
            sentiment = Sentiment.BEARISH
            confidence = 0.70
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.60
            
        return SentimentResponse(
            symbol=symbol,
            timeframe=timeframe,
            sentiment=sentiment,
            confidence=confidence,
            price_change_percent=round(price_change * 100, 2),
            volume_trend=round(volume_trend, 2),
            volatility=round(volatility * 100, 2),
            analysis=f"Over {timeframe}: {sentiment.lower()} sentiment with {price_change*100:.1f}% price change and {volume_trend:.1f}x volume trend"
        )
        
    except Exception as e:
        return SentimentResponse(
            symbol=symbol,
            timeframe=timeframe,
            sentiment=Sentiment.NEUTRAL,
            confidence=0.0,
            price_change_percent=0.0,
            volume_trend=1.0,
            volatility=0.0,
            analysis=f"Error analyzing sentiment: {str(e)}"
        )

def check_regulation_m_compliance(symbol: str) -> ComplianceResponse:
    """Check SEC Regulation M compliance for trading decisions.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Structured compliance analysis
    """
    try:
        # Get recent volume and price data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")
        
        if data.empty:
            from data.demo_data import generate_demo_stock_data
            data = generate_demo_stock_data(symbol, 5)
        
        # Analyze for Regulation M violations
        violations = []
        compliance_status = ComplianceStatus.COMPLIANT
        
        # Check volume patterns (simplified)
        recent_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].mean()
        volume_spike = recent_volume / avg_volume if avg_volume > 0 else 1.0
        
        if volume_spike > 3.0:
            violations.append("High volume activity may indicate distribution period")
            compliance_status = ComplianceStatus.VIOLATION_DETECTED
        
        # Check price volatility  
        price_changes = data['Close'].pct_change().abs()
        high_volatility = (price_changes > 0.05).sum() >= 2
        
        if high_volatility:
            violations.append("High price volatility during analysis period")
            if compliance_status == ComplianceStatus.COMPLIANT:
                compliance_status = ComplianceStatus.REVIEW_REQUIRED
        
        # Recommendation based on compliance
        if compliance_status == ComplianceStatus.VIOLATION_DETECTED:
            recommendation = "BLOCK_TRADES"
            confidence = 0.90
        elif compliance_status == ComplianceStatus.REVIEW_REQUIRED:
            recommendation = "PROCEED_WITH_CAUTION"
            confidence = 0.70
        else:
            recommendation = "APPROVED"
            confidence = 0.85
            
        return ComplianceResponse(
            symbol=symbol,
            compliance_status=compliance_status,
            recommendation=recommendation,
            confidence=confidence,
            violations=violations,
            volume_analysis=VolumeAnalysis(
                recent_volume=int(recent_volume),
                average_volume=int(avg_volume),
                volume_spike_ratio=round(volume_spike, 2)
            ),
            explanation=f"Compliance check for {symbol}: {compliance_status.value.lower()} status with {len(violations)} potential issues identified"
        )
        
    except Exception as e:
        return ComplianceResponse(
            symbol=symbol,
            compliance_status=ComplianceStatus.REVIEW_REQUIRED,
            recommendation="ERROR_ANALYSIS",
            confidence=0.0,
            violations=[f"Error checking compliance: {str(e)}"],
            volume_analysis=VolumeAnalysis(recent_volume=0, average_volume=0, volume_spike_ratio=0.0),
            explanation=f"Error checking compliance: {str(e)}"
        )

def analyze_price_trend(data):
    """Analyze overall price trend"""
    try:
        if len(data) < 5:
            return "INSUFFICIENT_DATA"
            
        recent_prices = data['Close'].tail(5)
        price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
        
        if price_change > 0.05:
            return "STRONG_UPTREND"
        elif price_change > 0.02:
            return "UPTREND"
        elif price_change < -0.05:
            return "STRONG_DOWNTREND"
        elif price_change < -0.02:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    except:
        return "UNKNOWN"

def analyze_volume_patterns(data):
    """Analyze volume patterns"""
    try:
        if len(data) < 5:
            return "INSUFFICIENT_DATA"
            
        recent_volume = data['Volume'].tail(3).mean()
        historical_volume = data['Volume'].mean()
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1.0
        
        if volume_ratio > 2.0:
            return "HIGH_VOLUME"
        elif volume_ratio > 1.5:
            return "ELEVATED_VOLUME"
        elif volume_ratio < 0.5:
            return "LOW_VOLUME"
        else:
            return "NORMAL_VOLUME"
    except:
        return "UNKNOWN"

def find_nearest_fib_level(price, fib_levels):
    """Find the nearest Fibonacci level to current price"""
    try:
        min_diff = float('inf')
        nearest_level = None
        
        for level, value in fib_levels.items():
            diff = abs(price - value)
            if diff < min_diff:
                min_diff = diff
                nearest_level = level
                
        return f"{nearest_level} level (${fib_levels[nearest_level]:.2f})"
    except:
        return "unknown level"