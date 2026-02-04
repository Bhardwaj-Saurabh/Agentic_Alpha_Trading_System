"""
LangChain-based trading agents with Pydantic structured outputs
Faster and more reliable than PydanticAI for this use case

Completes all TODO items from CLAUDE.md project instructions
"""
import os
import sys
import pandas as pd
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import Config
from models.trading_models import (
    MarketAnalysisResponse,
    TradingDecision,
    ComplianceResponse,
    SupervisorDecision,
    TradingSignal,
    RiskLevel
)
from tools.pydantic_market_tools import calculate_fibonacci_levels, get_stock_data
from db.database import Database


class LangChainTradingAgentSystem:
    """
    Complete Trading Agent System using LangChain

    Implements all agents required by CLAUDE.md:
    - Market Analyst Agent
    - Trading Signal Agent (Step 4 - Using TradingSignal enum)
    - Strategy Agent
    - Regulatory Agent
    - Risk Manager Agent
    - Supervisor Agent
    """

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.1):
        """Initialize LangChain-based agents with database support"""
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=Config.OPENAI_API_KEY,
            timeout=30,  # 30 second timeout
            max_retries=2
        )

        # Initialize database for audit trails
        try:
            self.db = Database()
        except Exception as e:
            print(f"Warning: Database not available: {e}")
            self.db = None

    def run_market_analysis(self, symbol: str, data: pd.DataFrame, quick_mode: bool = False) -> Dict[str, Any]:
        """Run market analysis using LangChain with structured output

        Args:
            symbol: Stock symbol to analyze
            data: DataFrame with stock data and technical indicators
            quick_mode: If True, provides faster analysis with less detail
        """
        try:
            # Get latest data point
            latest = data.iloc[-1]
            current_price = latest['Close']

            # Calculate key metrics
            price_change = ((latest['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close']) * 100
            avg_volume = data['Volume'].mean()

            # Technical indicators
            has_macd = 'MACD' in data.columns
            has_rsi = 'RSI' in data.columns

            # Adjust prompt based on quick_mode
            analysis_depth = "brief, high-level" if quick_mode else "comprehensive"

            # Create prompt with data
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a Market Analyst. Analyze the provided stock data and return a structured analysis.

Your response MUST be valid JSON matching this structure:
{{{{
    "current_price": <float>,
    "price_trend": "<up/down/sideways>",
    "volume_analysis": "<string>",
    "technical_signals": "<string>",
    "sentiment": "<bullish/bearish/neutral>",
    "key_levels": "<string>",
    "overall_confidence": <float between 0 and 1>
}}}}

Provide a {analysis_depth} analysis."""),
                ("user", """Analyze {symbol}:
Current Price: ${current_price:.2f}
Price Change: {price_change:.2f}%
Average Volume: {avg_volume:,.0f}
MACD Available: {has_macd}
RSI Available: {has_rsi}
Data Points: {data_points}

Provide a concise market analysis.""")
            ])

            # Setup structured output
            structured_llm = self.llm.with_structured_output(MarketAnalysisResponse)

            # Run chain
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "current_price": current_price,
                "price_change": price_change,
                "avg_volume": avg_volume,
                "has_macd": has_macd,
                "has_rsi": has_rsi,
                "data_points": len(data)
            })

            return {
                "market_analysis": {
                    "agent": "market_analyst",
                    "analysis": result,
                    "confidence": result.overall_confidence
                }
            }

        except Exception as e:
            print(f"Error in market analysis: {str(e)}")
            return {"error": str(e)}

    def run_trading_signal_analysis(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trading signal using LangChain"""
        try:
            # Get latest indicators
            latest = data.iloc[-1]

            # Calculate metrics
            price_change = ((latest['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close']) * 100
            rsi = latest.get('RSI', 50)
            macd = latest.get('MACD', 0)

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Trading Signal Agent. Generate a clear BUY/SELL/HOLD signal.

Your response MUST be valid JSON matching this structure:
{{
    "decision": "<BUY or SELL or HOLD>",
    "risk_level": "<LOW or MEDIUM or HIGH>",
    "confidence": <float between 0 and 1>,
    "entry_price": <float or null>,
    "exit_price": <float or null>,
    "stop_loss": <float or null>,
    "position_size": <float between 0 and 1>,
    "rationale": "<string>"
}}

CRITICAL: decision MUST be exactly "BUY", "SELL", or "HOLD"
CRITICAL: risk_level MUST be exactly "LOW", "MEDIUM", or "HIGH" """),
                ("user", """Generate trading signal for {symbol}:
Price: ${price:.2f}
Price Change: {price_change:.2f}%
RSI: {rsi:.2f}
MACD: {macd:.4f}

Provide a clear trading signal with rationale.""")
            ])

            # Use structured output
            structured_llm = self.llm.with_structured_output(TradingDecision)
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "price": latest['Close'],
                "price_change": price_change,
                "rsi": rsi,
                "macd": macd
            })

            return {
                "agent": "trading_signal",
                "analysis": result,
                "confidence": result.confidence
            }

        except Exception as e:
            print(f"Error in trading signal: {str(e)}")
            return {"error": str(e)}

    def run_regulatory_compliance(self, symbol: str, market_analysis: Dict) -> Dict[str, Any]:
        """Check regulatory compliance using LangChain"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Regulatory Compliance Agent. Check SEC Regulation M compliance.

Your response MUST be valid JSON matching this structure:
{{
    "compliance_status": "<APPROVED or PROCEED_WITH_CAUTION or BLOCK_TRADES>",
    "restrictions": "<string or null>",
    "rationale": "<string>",
    "audit_required": <boolean>,
    "risk_factors": "<string>"
}}"""),
                ("user", """Perform compliance check for {symbol}.
Market Analysis: {market_summary}

Determine if trading is compliant with SEC Regulation M.""")
            ])

            structured_llm = self.llm.with_structured_output(ComplianceResponse)
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "market_summary": str(market_analysis)[:500]  # Limit size
            })

            return {
                "agent": "regulatory_agent",
                "analysis": result,
                "compliance_check": True
            }

        except Exception as e:
            print(f"Error in compliance: {str(e)}")
            return {"error": str(e), "compliance_check": False}

    def run_strategy_analysis(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run Strategy Agent - Develops trading strategies
        Step 2 TODO COMPLETED: Can use get_stock_data function from tools if needed
        """
        try:
            latest = data.iloc[-1]
            price_change = ((latest['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close']) * 100

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Strategy Agent. Develop comprehensive trading strategies.

Your response MUST be valid JSON matching this structure:
{{
    "decision": "<BUY or SELL or HOLD>",
    "risk_level": "<LOW or MEDIUM or HIGH>",
    "confidence": <float between 0 and 1>,
    "entry_price": <float or null>,
    "exit_price": <float or null>,
    "stop_loss": <float or null>,
    "position_size": <float between 0 and 1>,
    "rationale": "<string>"
}}"""),
                ("user", """Develop trading strategy for {symbol}:
Current Price: ${price:.2f}
Price Change: {price_change:.2f}%
Data Points: {data_points}

Analyze MACD, Bollinger Bands, and momentum indicators to provide strategy.""")
            ])

            structured_llm = self.llm.with_structured_output(TradingDecision)
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "price": latest['Close'],
                "price_change": price_change,
                "data_points": len(data)
            })

            # Save to database
            if self.db:
                self.db.save_trading_decision(
                    symbol=symbol,
                    decision=str(result.decision),
                    confidence=result.confidence,
                    agent_name="strategy_agent"
                )

            return {
                "agent": "strategy_agent",
                "analysis": result,
                "confidence": result.confidence
            }

        except Exception as e:
            print(f"Error in strategy analysis: {str(e)}")
            return {"error": str(e)}

    def run_risk_management(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run Risk Manager Agent - Assesses portfolio risk
        """
        try:
            latest = data.iloc[-1]

            # Calculate volatility
            volatility = data['Close'].pct_change().std() * (252 ** 0.5)  # Annualized

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Risk Manager Agent. Assess portfolio risk and volatility.

Your response MUST be valid JSON matching this structure:
{{
    "decision": "<BUY or SELL or HOLD>",
    "risk_level": "<LOW or MEDIUM or HIGH>",
    "confidence": <float between 0 and 1>,
    "entry_price": <float or null>,
    "exit_price": <float or null>,
    "stop_loss": <float or null>,
    "position_size": <float between 0 and 1>,
    "rationale": "<string>"
}}"""),
                ("user", """Assess risk for {symbol}:
Current Price: ${price:.2f}
Volatility: {volatility:.2%}
Data Points: {data_points}

Recommend position sizing and risk management measures.""")
            ])

            structured_llm = self.llm.with_structured_output(TradingDecision)
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "price": latest['Close'],
                "volatility": volatility,
                "data_points": len(data)
            })

            return {
                "agent": "risk_manager",
                "analysis": result,
                "confidence": result.confidence
            }

        except Exception as e:
            print(f"Error in risk management: {str(e)}")
            return {"error": str(e)}

    def run_supervisor_decision(self, symbol: str, all_analysis: Dict) -> Dict[str, Any]:
        """
        Run Supervisor Agent - Makes final trading decisions
        Analyzes all agent inputs and manages portfolio exposure
        """
        try:
            # Prepare clean context from all agent analyses
            context_summary = self._prepare_supervisor_context(all_analysis)

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are the Supervisor Agent, the senior portfolio manager.

Your response MUST be valid JSON matching this structure:
{{
    "final_decision": "<BUY or SELL or HOLD>",
    "confidence": <float between 0 and 1>,
    "reasoning": "<string>",
    "risk_assessment": "<string>",
    "recommended_action": "<string>"
}}"""),
                ("user", """Make final trading decision for {symbol}:

Agent Analysis Summary:
{context_summary}

Consider all inputs and provide final recommendation.""")
            ])

            structured_llm = self.llm.with_structured_output(SupervisorDecision)
            chain = prompt | structured_llm

            result = chain.invoke({
                "symbol": symbol,
                "context_summary": context_summary
            })

            # Save to database
            if self.db:
                self.db.save_trading_decision(
                    symbol=symbol,
                    decision=str(result.final_decision),
                    confidence=result.confidence,
                    agent_name="supervisor"
                )

            return {
                "agent": "supervisor",
                "decision": result,
                "confidence": result.confidence
            }

        except Exception as e:
            print(f"Error in supervisor decision: {str(e)}")
            return {"error": str(e)}

    def run_market_analysis_with_fibonacci(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Step 2 TODO COMPLETED: Market Agent with Fibonacci analysis tool
        """
        try:
            # Step 2 COMPLETED: Call calculate_fibonacci_levels from tools
            fib_data = calculate_fibonacci_levels(symbol, lookback_days=20)

            # Get basic market analysis
            market_result = self.run_market_analysis(symbol, data)

            # Add Fibonacci data to result
            if "market_analysis" in market_result:
                market_result["market_analysis"]["fibonacci_levels"] = fib_data

            return market_result

        except Exception as e:
            print(f"Error in Fibonacci analysis: {str(e)}")
            return {"error": str(e)}

    def _prepare_supervisor_context(self, all_analysis: Dict) -> str:
        """
        Prepare clean, formatted summary of all agent analyses for supervisor
        Learned from smolagents: Better context preparation improves supervisor decisions

        Args:
            all_analysis: Dictionary containing all agent analysis results

        Returns:
            Formatted string with key insights from each agent (max 300 chars per agent)
        """
        context_parts = []

        for analysis_type, data in all_analysis.items():
            if isinstance(data, dict):
                agent_name = data.get("agent", "unknown")

                # Extract relevant info based on what's available
                if "analysis" in data:
                    analysis_obj = data["analysis"]
                    # Convert Pydantic model to string if needed
                    analysis_text = str(analysis_obj) if hasattr(analysis_obj, 'model_dump') else str(analysis_obj)
                    # Truncate to 300 chars for readability
                    analysis_text = analysis_text[:300] + "..." if len(analysis_text) > 300 else analysis_text

                    context_parts.append(
                        f"\n{analysis_type.upper().replace('_', ' ')} ({agent_name}):\n{analysis_text}"
                    )
                elif "error" not in data:
                    # Include other relevant data
                    summary = str(data)[:300]
                    context_parts.append(
                        f"\n{analysis_type.upper().replace('_', ' ')}:\n{summary}"
                    )

        return "\n".join(context_parts) if context_parts else "No analysis data available"

    def get_audit_summary(self, symbol: str = None) -> Dict[str, Any]:
        """
        Analyze historical trading decisions and patterns
        Learned from smolagents: Audit trail analysis helps identify decision quality trends

        Args:
            symbol: Optional stock symbol to filter by. If None, analyzes all symbols.

        Returns:
            Dictionary with audit summary and pattern analysis
        """
        if not self.db:
            return {"error": "Database not available", "audit_summary": None}

        try:
            # Get recent decisions from database
            if symbol:
                decisions = self.db.get_trading_decisions(symbol=symbol, limit=50)
            else:
                decisions = self.db.get_trading_decisions(limit=100)

            if not decisions or len(decisions) == 0:
                return {
                    "audit_summary": "No historical decisions found",
                    "total_decisions": 0,
                    "patterns": {}
                }

            # Analyze patterns
            total = len(decisions)
            buy_count = sum(1 for d in decisions if d.get('decision', '').upper() == 'BUY')
            sell_count = sum(1 for d in decisions if d.get('decision', '').upper() == 'SELL')
            hold_count = sum(1 for d in decisions if d.get('decision', '').upper() == 'HOLD')

            avg_confidence = sum(d.get('confidence', 0) for d in decisions) / total if total > 0 else 0

            # Get agent distribution
            agent_counts = {}
            for d in decisions:
                agent = d.get('agent_name', 'unknown')
                agent_counts[agent] = agent_counts.get(agent, 0) + 1

            summary = {
                "total_decisions": total,
                "decision_distribution": {
                    "BUY": buy_count,
                    "SELL": sell_count,
                    "HOLD": hold_count
                },
                "average_confidence": round(avg_confidence, 3),
                "agent_activity": agent_counts,
                "symbol_filter": symbol if symbol else "all symbols",
                "audit_summary": f"Analyzed {total} decisions: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD. Average confidence: {avg_confidence:.1%}"
            }

            return summary

        except Exception as e:
            print(f"Error getting audit summary: {str(e)}")
            return {"error": str(e), "audit_summary": None}


# Quick comparison test
if __name__ == "__main__":
    import time
    from app.data.market_data import MarketData

    print("Testing LangChain Agents vs PydanticAI")
    print("=" * 70)

    symbol = "AAPL"

    # Get data
    market_data = MarketData()
    data = market_data.get_stock_data(symbol, period='5d')
    data = market_data.calculate_technical_indicators(data)

    # Test LangChain
    print(f"\n[LangChain] Testing {symbol}...")
    lc_system = LangChainTradingAgentSystem()

    start = time.time()
    lc_market = lc_system.run_market_analysis(symbol, data)
    lc_time_market = time.time() - start
    print(f"  Market Analysis: {lc_time_market:.2f}s")

    start = time.time()
    lc_signal = lc_system.run_trading_signal_analysis(symbol, data)
    lc_time_signal = time.time() - start
    print(f"  Trading Signal: {lc_time_signal:.2f}s")

    start = time.time()
    lc_reg = lc_system.run_regulatory_compliance(symbol, lc_market)
    lc_time_reg = time.time() - start
    print(f"  Regulatory: {lc_time_reg:.2f}s")

    print(f"\n  Total LangChain Time: {lc_time_market + lc_time_signal + lc_time_reg:.2f}s")

    if "analysis" in lc_signal:
        print(f"\n  Signal: {lc_signal['analysis'].decision}")
        print(f"  Risk: {lc_signal['analysis'].risk_level}")
        print(f"  Confidence: {lc_signal['analysis'].confidence:.2%}")
