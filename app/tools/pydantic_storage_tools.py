"""Storage and data management tools for PydanticAI"""

import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.trading_models import TradingSignal, RiskLevel

def save_trading_decision(symbol: str, decision: str, confidence: float, agent_name: str) -> str:
    """Save a trading decision to the audit trail.
    
    Args:
        symbol: Stock symbol
        decision: Trading decision or analysis
        confidence: Confidence score (0-1)
        agent_name: Name of the agent making the decision
        
    Returns:
        Confirmation message
    """
    try:
        #TODO:  Can you convert this to use a database instead of csv storage?
        from storage.csv_storage import CSVStorage
        storage = CSVStorage()
        
        # Save to regular storage
        storage.save_trading_decision(symbol, decision, confidence, agent_name)
        
        return f"Successfully saved {agent_name} decision for {symbol} with confidence {confidence:.2f}"
        
    except Exception as e:
        return f"Error saving decision: {str(e)}"

def save_audit_entry(symbol: str, decision_type: str, action: str, confidence: float, 
                    rationale: str, compliance_status: Optional[str] = None, 
                    risk_level: Optional[str] = None, position_size: Optional[str] = None,
                    blocked_trades: Optional[str] = None) -> str:
    """Save detailed audit entry for compliance review.
    
    Args:
        symbol: Stock symbol
        decision_type: 'SUPERVISOR' or 'REGULATORY' or 'STRATEGY'
        action: Trading action (BUY/SELL/HOLD)
        confidence: Confidence score (0-1)
        rationale: Detailed reasoning
        compliance_status: Regulatory compliance status
        risk_level: Risk assessment
        position_size: Recommended position size
        blocked_trades: Information about blocked trades
        
    Returns:
        Confirmation message
    """
    try:
        from storage.csv_storage import CSVStorage
        storage = CSVStorage()
        
        storage.save_audit_entry(
            symbol=symbol,
            decision_type=decision_type,
            action=action,
            confidence=confidence,
            rationale=rationale,
            compliance_status=compliance_status,
            risk_level=risk_level,
            position_size=position_size,
            blocked_trades=blocked_trades
        )
        
        return f"Successfully saved {decision_type} audit entry for {symbol}"
        
    except Exception as e:
        return f"Error saving audit entry: {str(e)}"

def get_audit_trail(symbol: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Retrieve audit trail entries for review.
    
    Args:
        symbol: Optional symbol to filter by
        limit: Maximum number of entries to return
        
    Returns:
        List of audit trail entries
    """
    try:
        from storage.csv_storage import CSVStorage
        storage = CSVStorage()
        
        entries = storage.get_audit_trail(symbol=symbol, limit=limit)
        return entries
        
    except Exception as e:
        print(f"Error retrieving audit trail: {str(e)}")
        return []

def get_trading_decisions_summary(symbol: Optional[str] = None) -> Dict:
    """Get summary of all trading decisions.
    
    Args:
        symbol: Optional symbol to filter by
        
    Returns:
        Dictionary with decisions summary
    """
    try:
        from storage.csv_storage import CSVStorage
        storage = CSVStorage()
        
        if symbol:
            # Get decisions for specific symbol
            decisions = storage.get_trading_decisions(symbol=symbol)
            result = {
                "symbol": symbol,
                "total_decisions": len(decisions),
                "recent_decisions": decisions[:10]  # Last 10 decisions
            }
        else:
            # Get overall summary
            summary = storage.get_decisions_summary()
            result = summary
            
        return result
        
    except Exception as e:
        print(f"Error getting decisions summary: {str(e)}")
        return {"error": str(e)}

def analyze_decision_patterns(symbol: str, lookback_days: int = 30) -> Dict:
    """Analyze patterns in trading decisions for a symbol.
    
    Args:
        symbol: Stock symbol to analyze
        lookback_days: Number of days to look back
        
    Returns:
        Dictionary with pattern analysis
    """
    try:
        from storage.csv_storage import CSVStorage
        from datetime import datetime, timedelta
        
        storage = CSVStorage()
        decisions = storage.get_trading_decisions(symbol=symbol)
        
        if not decisions:
            return {"error": f"No decisions found for {symbol}"}
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        recent_decisions = [
            d for d in decisions 
            if datetime.fromisoformat(d.get('created_at', '2024-01-01')) >= cutoff_date
        ]
        
        # Analyze patterns
        agent_counts = {}
        decision_types = {}
        confidence_scores = []
        
        for decision in recent_decisions:
            agent_name = decision.get('agent_name', 'unknown')
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
            
            decision_text = decision.get('decision', '').upper()
            if 'BUY' in decision_text:
                decision_types['BUY'] = decision_types.get('BUY', 0) + 1
            elif 'SELL' in decision_text:
                decision_types['SELL'] = decision_types.get('SELL', 0) + 1
            else:
                decision_types['HOLD'] = decision_types.get('HOLD', 0) + 1
                
            confidence_scores.append(decision.get('confidence', 0.0))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        result = {
            "symbol": symbol,
            "analysis_period": f"{lookback_days} days",
            "total_decisions": len(recent_decisions),
            "agent_activity": agent_counts,
            "decision_breakdown": decision_types,
            "average_confidence": round(avg_confidence, 2),
            "confidence_range": {
                "min": min(confidence_scores) if confidence_scores else 0,
                "max": max(confidence_scores) if confidence_scores else 0
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Error analyzing decision patterns: {str(e)}"}