"""Pydantic models for structured responses in the trading system"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Sentiment(str, Enum):
    VERY_BULLISH = "VERY_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    VERY_BEARISH = "VERY_BEARISH"

class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    VIOLATION_DETECTED = "VIOLATION_DETECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class PriceInfo(BaseModel):
    current_price: float
    previous_close: float
    high_52w: float
    low_52w: float
    volume_avg: float

class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_middle: Optional[float] = None

class StockDataResponse(BaseModel):
    symbol: str
    period: str
    data_points: int
    price_info: PriceInfo
    technical_indicators: TechnicalIndicators
    trend_analysis: str
    volume_analysis: str

class FibonacciResponse(BaseModel):
    symbol: str
    current_price: float
    fibonacci_levels: Dict[str, float]
    signal: TradingSignal
    confidence: float = Field(ge=0, le=1)
    analysis: str

class SentimentResponse(BaseModel):
    symbol: str
    timeframe: str
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    price_change_percent: float
    volume_trend: float
    volatility: float
    analysis: str

class VolumeAnalysis(BaseModel):
    recent_volume: int
    average_volume: int
    volume_spike_ratio: float

class ComplianceResponse(BaseModel):
    symbol: str
    compliance_status: ComplianceStatus
    recommendation: str
    confidence: float = Field(ge=0, le=1)
    violations: List[str]
    volume_analysis: VolumeAnalysis
    explanation: str

class MarketAnalysisResponse(BaseModel):
    symbol: str
    market_analysis: str
    strategy_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None
    overall_confidence: float = Field(ge=0, le=1)
    technical_summary: str
    sentiment_summary: str

class TradingDecision(BaseModel):
    symbol: str
    decision: TradingSignal
    confidence: float = Field(ge=0, le=1)
    rationale: str
    risk_level: RiskLevel
    position_size_percent: Optional[float] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None

class SupervisorDecision(BaseModel):
    symbol: str
    final_decision: TradingSignal
    confidence: float = Field(ge=0, le=1)
    rationale: str
    risk_assessment: RiskLevel
    position_size_percent: float = Field(ge=0, le=100)
    compliance_approved: bool
    agent_consensus: str
    market_conditions_summary: str