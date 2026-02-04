"""PydanticAI-based trading agents with enhanced type safety and structured responses"""

import os
from pydantic_ai import Agent, RunContext
import pandas as pd
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys

#TODO: Optional.  Separate the agents into different files and run them as different classes.
#TODO:  Find a way to use TradingSignal and RiskLevel classes in the tools and models.

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from models.trading_models import (
    MarketAnalysisResponse, TradingDecision, SupervisorDecision,
    ComplianceResponse, TradingSignal, RiskLevel
)
from tools.pydantic_market_tools import (
    get_stock_data, calculate_fibonacci_levels, 
    analyze_market_sentiment, check_regulation_m_compliance
)
from tools.pydantic_storage_tools import (
    save_trading_decision, save_audit_entry, get_audit_trail,
    get_trading_decisions_summary, analyze_decision_patterns
)

#This is another way to maintain state in the backend of the program.
class Dependencies(BaseModel):
    """Dependencies for all agents"""
    symbol: Optional[str] = None
    user_context: Optional[str] = None
    data: Optional[pd.DataFrame] = None 

    class Config:
        arbitrary_types_allowed = True

class PydanticTradingAgentSystem:
    """Advanced trading agent system using PydanticAI framework with structured responses"""
    
    def __init__(self, use_openai: bool = True):
        """Initialize the multi-agent trading system with PydanticAI"""
        #TODO: populate your keys in the config file.
        # Determine which model to use
        try:
            if use_openai and Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
                self.model_name = "openai:gpt-4o"
                # Set the API key in environment for PydanticAI
                os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
            else:
                # Check if we have Anthropic key from config
                if Config.ANTHROPIC_API_KEY and Config.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
                    self.model_name = "anthropic:claude-sonnet-4-20250514"
                    os.environ["ANTHROPIC_API_KEY"] = Config.ANTHROPIC_API_KEY
                else:
                    # Fallback to OpenAI with error handling
                    self.model_name = "openai:gpt-4o"
                    if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
                        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        except Exception as e:
            print(f"Model initialization issue: {e}")
            self.model_name = "openai:gpt-4o"
        
        # Create specialized trading agents
        self.agents = self._create_agents()
        
    def _create_agents(self):
        """Create specialized trading agents with PydanticAI"""
        
        # Market Data Analyst Agent
        market_agent = Agent(
            model=self.model_name,
            deps_type=Dependencies,
            output_type=MarketAnalysisResponse
        )
        
        @market_agent.system_prompt
        def market_system_prompt(ctx: RunContext[Dependencies]) -> str:
            return f"""You are a Market Data Analyst specializing in technical analysis and market sentiment for {ctx.deps.symbol}.
            
            Your role:
            - Analyze stock data, technical indicators, and market trends
            - Calculate Fibonacci levels and sentiment analysis  
            - Provide clear, data-driven market insights
            - Use available tools to fetch and analyze real market data
            
            Always provide structured analysis with confidence scores and specific recommendations."""
        
        @market_agent.tool
        def get_market_data(ctx: RunContext[Dependencies], period: str = "1mo") -> str:
            """Get comprehensive stock data with technical indicators"""
            stock_data = get_stock_data(ctx.deps.symbol, period, data=ctx.deps.data)
            return f"Stock data retrieved: {stock_data.model_dump_json()}"
        
        @market_agent.tool
        def get_fibonacci_analysis(ctx: RunContext[Dependencies], lookback_days: int = 20) -> str:
            """Calculate Fibonacci retracement levels and trading signals"""
            fib_data = calculate_fibonacci_levels(ctx.deps.symbol, lookback_days)
            return f"Fibonacci analysis: {fib_data.model_dump_json()}"
        
        @market_agent.tool
        def get_sentiment_analysis(ctx: RunContext[Dependencies], timeframe: str = "3d") -> str:
            """Analyze market sentiment using price action and volume"""
            sentiment_data = analyze_market_sentiment(ctx.deps.symbol, timeframe)
            return f"Sentiment analysis: {sentiment_data.model_dump_json()}"
        
        # Strategy & Trading Agent
        strategy_agent = Agent(
            model=self.model_name,
            deps_type=Dependencies,
            output_type=TradingDecision
        )
        
        @strategy_agent.system_prompt
        def strategy_system_prompt(ctx: RunContext[Dependencies]) -> str:
            return f"""You are a Strategy Agent specializing in trading strategy development and signal generation for {ctx.deps.symbol}.
            
            Your role:
            - Develop comprehensive trading strategies using technical analysis
            - Generate buy/sell/hold signals with confidence scores
            - Provide specific entry/exit points and position sizing
            - Save trading decisions for audit purposes
            
            Always provide actionable trading recommendations with clear rationale."""
        
        @strategy_agent.tool
        def get_market_data(ctx: RunContext[Dependencies], period: str = "1mo") -> str:
            """Get comprehensive stock data with technical indicators"""
            stock_data = get_stock_data(ctx.deps.symbol, period, data=ctx.deps.data)
            return f"Stock data retrieved: {stock_data.model_dump_json()}"
        
        @strategy_agent.tool
        def get_fibonacci_analysis(ctx: RunContext[Dependencies], lookback_days: int = 20) -> str:
            """Calculate Fibonacci retracement levels and trading signals"""  
            fib_data = calculate_fibonacci_levels(ctx.deps.symbol, lookback_days)
            return f"Fibonacci analysis: {fib_data.model_dump_json()}"
        
        @strategy_agent.tool
        def save_strategy_decision(ctx: RunContext[Dependencies], decision: str, confidence: float) -> str:
            """Save trading decision to audit trail"""
            return save_trading_decision(ctx.deps.symbol, decision, confidence, "strategy_agent")
        
        @strategy_agent.tool
        def save_strategy_audit(ctx: RunContext[Dependencies], action: str, confidence: float, rationale: str, risk_level: str = "MEDIUM") -> str:
            """Save detailed strategy audit entry"""
            return save_audit_entry(ctx.deps.symbol, "STRATEGY", action, confidence, rationale, risk_level=risk_level)
        
        # Compliance & Regulatory Agent
        regulatory_agent = Agent(
            model=self.model_name,
            deps_type=Dependencies,
            output_type=ComplianceResponse
        )
        
        @regulatory_agent.system_prompt
        def regulatory_system_prompt(ctx: RunContext[Dependencies]) -> str:
            return f"""You are a Regulatory Compliance Agent specializing in SEC regulations and trading compliance for {ctx.deps.symbol}.
            
            Your role:
            - Ensure all trading decisions comply with SEC Regulation M
            - Identify potential compliance violations
            - Maintain detailed audit trails for regulatory review
            - Block trades when necessary for compliance
            
            Always prioritize regulatory compliance and provide clear explanations for decisions."""
        
        @regulatory_agent.tool
        def check_compliance(ctx: RunContext[Dependencies]) -> str:
            """Check SEC Regulation M compliance for the current symbol"""
            compliance_data = check_regulation_m_compliance(ctx.deps.symbol)
            return f"Compliance analysis: {compliance_data.model_dump_json()}"
        
        @regulatory_agent.tool
        def get_market_data(ctx: RunContext[Dependencies], period: str = "5d") -> str:
            """Get recent market data for compliance analysis"""
            stock_data = get_stock_data(ctx.deps.symbol, period, data=ctx.deps.data)
            return f"Stock data retrieved: {stock_data.model_dump_json()}"
        
        @regulatory_agent.tool
        def save_compliance_audit(ctx: RunContext[Dependencies], action: str, confidence: float, rationale: str, compliance_status: str) -> str:
            """Save compliance audit entry"""
            return save_audit_entry(ctx.deps.symbol, "REGULATORY", action, confidence, rationale, compliance_status=compliance_status)
        
        @regulatory_agent.tool
        def get_audit_history(ctx: RunContext[Dependencies], limit: int = 10) -> str:
            """Get recent audit trail for compliance review"""
            audit_data = get_audit_trail(ctx.deps.symbol, limit)
            return f"Audit trail: {audit_data}"
        
        # Risk Management Agent
        risk_agent = Agent(
            model=self.model_name,
            deps_type=Dependencies,
            output_type=TradingDecision
        )
        
        @risk_agent.system_prompt
        def risk_system_prompt(ctx: RunContext[Dependencies]) -> str:
            return f"""You are a Risk Management Agent specializing in portfolio risk assessment and position sizing for {ctx.deps.symbol}.
            
            Your role:
            - Evaluate market volatility and risk exposure
            - Recommend appropriate position sizing
            - Analyze historical decision patterns for risk insights
            - Provide risk-adjusted trading recommendations
            
            Always prioritize capital preservation and risk-adjusted returns."""
        
        @risk_agent.tool
        def get_market_data(ctx: RunContext[Dependencies], period: str = "1mo") -> str:
            """Get market data for risk analysis"""
            stock_data = get_stock_data(ctx.deps.symbol, period, data=ctx.deps.data)
            return f"Stock data retrieved: {stock_data.model_dump_json()}"
        
        @risk_agent.tool
        def get_sentiment_analysis(ctx: RunContext[Dependencies], timeframe: str = "7d") -> str:
            """Analyze market sentiment for risk assessment"""
            sentiment_data = analyze_market_sentiment(ctx.deps.symbol, timeframe)
            return f"Sentiment analysis: {sentiment_data.model_dump_json()}"
        
        @risk_agent.tool
        def analyze_patterns(ctx: RunContext[Dependencies], lookback_days: int = 30) -> str:
            """Analyze historical trading decision patterns"""
            pattern_data = analyze_decision_patterns(ctx.deps.symbol, lookback_days)
            return f"Decision patterns: {pattern_data}"
        
        @risk_agent.tool
        def save_risk_audit(ctx: RunContext[Dependencies], action: str, confidence: float, rationale: str, risk_level: str) -> str:
            """Save risk assessment audit entry"""
            return save_audit_entry(ctx.deps.symbol, "RISK", action, confidence, rationale, risk_level=risk_level)
        
        # Supervisor Agent
        supervisor_agent = Agent(
            model=self.model_name,
            deps_type=Dependencies,
            output_type=SupervisorDecision
        )
        
        @supervisor_agent.system_prompt
        def supervisor_system_prompt(ctx: RunContext[Dependencies]) -> str:
            return f"""You are the Supervisor Agent, the senior portfolio manager making final trading decisions for {ctx.deps.symbol}.
            
            Your role:
            - Review analysis from all specialized agents
            - Make final trading decisions (BUY/SELL/HOLD)
            - Balance profit potential with risk management and compliance
            - Provide comprehensive rationale for all decisions
            - Maintain detailed audit records
            
            Your decisions are final and must consider all agent inputs, market conditions, and regulatory requirements."""
        
        @supervisor_agent.tool
        def get_market_data(ctx: RunContext[Dependencies], period: str = "1mo") -> str:
            """Get comprehensive market data for final decision"""
            stock_data = get_stock_data(ctx.deps.symbol, period, data=ctx.deps.data)
            return f"Stock data retrieved: {stock_data.model_dump_json()}"
        
        @supervisor_agent.tool
        def get_trading_summary(ctx: RunContext[Dependencies]) -> str:
            """Get summary of all trading decisions"""
            summary_data = get_trading_decisions_summary(ctx.deps.symbol)
            return f"Trading decisions summary: {summary_data}"
        
        @supervisor_agent.tool
        def get_audit_history(ctx: RunContext[Dependencies], limit: int = 20) -> str:
            """Get comprehensive audit trail for decision context"""
            audit_data = get_audit_trail(ctx.deps.symbol, limit)
            return f"Full audit trail: {audit_data}"
        
        @supervisor_agent.tool
        def save_final_decision(ctx: RunContext[Dependencies], action: str, confidence: float, rationale: str, risk_level: str, position_size: str) -> str:
            """Save final supervisor decision to audit trail"""
            return save_audit_entry(ctx.deps.symbol, "SUPERVISOR", action, confidence, rationale, 
                                  risk_level=risk_level, position_size=position_size)
        
        return {
            "market_analyst": market_agent,
            "strategy_agent": strategy_agent,
            "regulatory_agent": regulatory_agent,
            "risk_manager": risk_agent,
            "supervisor": supervisor_agent
        }
    
    def run_market_analysis(self, symbol: str, data : pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive market analysis using PydanticAI agents"""
        try:
            #TODO:  How can I break this up instead of running all agents at once?
            deps = Dependencies(symbol=symbol, data=data)
            results = {}
            
            # Market Analysis
            market_prompt = f"""
            Analyze the market data for {symbol}. Please:
            1. Get current stock data with technical indicators using the get_market_data tool
            2. Calculate Fibonacci retracement levels using get_fibonacci_analysis tool
            3. Analyze market sentiment using get_sentiment_analysis tool for multiple timeframes
            4. Provide a comprehensive market analysis with confidence scores
            
            Focus on actionable insights including price trends, volume patterns, technical signal strength, and sentiment indicators.
            Return a structured MarketAnalysisResponse with your complete analysis.
            """
            
            market_result = self.agents["market_analyst"].run_sync(market_prompt, deps=deps)
            results["market_analysis"] = {
                "agent": "market_analyst",
                "analysis": market_result.output,
                "confidence": market_result.output.overall_confidence if hasattr(market_result.output, 'overall_confidence') else 0.8
            }
            
            # Always run Strategy and Risk agents for complete analysis
            # Strategy Analysis
            strategy_prompt = f"""
            Based on market data for {symbol}, develop comprehensive trading strategies:
            1. Get current stock data and Fibonacci levels using available tools
            2. Analyze MACD crossovers, Bollinger Band signals, and momentum indicators
            3. Generate a specific trading signal (BUY/SELL/HOLD) with confidence score
            4. Provide entry/exit points and position sizing recommendations
            5. Save your trading decision using save_strategy_decision tool
            6. Create an audit entry using save_strategy_audit tool
            
            Return a structured TradingDecision with specific recommendations.
            """
            #run sync is running all tools in parallel.
            strategy_result = self.agents["strategy_agent"].run_sync(strategy_prompt, deps=deps)
            results["strategy_analysis"] = {
                "agent": "strategy_agent", 
                "analysis": strategy_result.output,
                "confidence": strategy_result.output.confidence if hasattr(strategy_result.output, 'confidence') else 0.75
            }
            
            # Risk Assessment
            risk_prompt = f"""
            Assess the risk profile for trading {symbol}:
            1. Get market data and sentiment analysis using available tools
            2. Analyze recent volatility and price patterns
            3. Review historical decision patterns using analyze_patterns tool
            4. Evaluate market sentiment and potential risks
            5. Recommend position sizing and risk management measures
            6. Save risk assessment using save_risk_audit tool
            
            Return a structured TradingDecision focused on risk management.
            """
            
            risk_result = self.agents["risk_manager"].run_sync(risk_prompt, deps=deps)
            results["risk_analysis"] = {
                "agent": "risk_manager",
                "analysis": risk_result.output, 
                "confidence": risk_result.output.confidence if hasattr(risk_result.output, 'confidence') else 0.85
            }
            
            return results
            
        except Exception as e:
            print(f"Error in market analysis: {str(e)}")
            return {"error": str(e)}
    
    def run_strategy_analysis(self, symbol: str, data : pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive market analysis using PydanticAI agents"""
        try:
            deps = Dependencies(symbol=symbol, data=data)
            results = {}
            
            # Always run Strategy and Risk agents for complete analysis
            # Strategy Analysis
            strategy_prompt = f"""
            Based on market data for {symbol}, develop comprehensive trading strategies:
            1. Get current stock data and Fibonacci levels using available tools
            2. Analyze MACD crossovers, Bollinger Band signals, and momentum indicators
            3. Generate a specific trading signal (BUY/SELL/HOLD) with confidence score
            4. Provide entry/exit points and position sizing recommendations
            5. Save your trading decision using save_strategy_decision tool
            6. Create an audit entry using save_strategy_audit tool
            
            Return a structured TradingDecision with specific recommendations.
            """
            
            strategy_result = self.agents["strategy_agent"].run_sync(strategy_prompt, deps=deps)
            results["strategy_analysis"] = {
                "agent": "strategy_agent", 
                "analysis": strategy_result.output,
                "confidence": strategy_result.output.confidence if hasattr(strategy_result.output, 'confidence') else 0.75
            }
            
            return results
            
        except Exception as e:
            print(f"Error in market analysis: {str(e)}")
            return {"error": str(e)}
        
    def run_regulatory_compliance(self, symbol: str, trading_signals: Dict) -> Dict[str, Any]:
        """Run regulatory compliance check with PydanticAI"""
        try:
            deps = Dependencies(symbol=symbol)
            
            compliance_prompt = f"""
            Perform comprehensive SEC Regulation M compliance check for {symbol}:
            1. Use check_compliance tool to analyze current compliance status
            2. Get recent market data for volume and price pattern analysis
            3. Review audit history using get_audit_history tool for context
            4. Analyze trading signals for potential violations: {trading_signals}
            5. Determine if any trades should be blocked for compliance reasons
            6. Save detailed compliance analysis using save_compliance_audit tool
            7. Provide clear recommendation: APPROVED, PROCEED_WITH_CAUTION, or BLOCK_TRADES
            
            Return a structured ComplianceResponse with detailed compliance analysis.
            """
            
            compliance_result = self.agents["regulatory_agent"].run_sync(compliance_prompt, deps=deps)
            
            return {
                "agent": "regulatory_agent",
                "analysis": compliance_result.output,
                "compliance_check": True
            }
            
        except Exception as e:
            print(f"Error in compliance check: {str(e)}")
            return {"error": str(e), "compliance_check": False}
    
    def run_supervisor_decision(self, symbol: str, all_analysis: Dict) -> Dict[str, Any]:
        """Run final supervisor decision with comprehensive analysis"""
        try:
            deps = Dependencies(symbol=symbol)
            
            # Prepare context from all agents
            context_summary = self._prepare_supervisor_context(all_analysis)
            
            supervisor_prompt = f"""
            As the senior portfolio manager, make the final trading decision for {symbol}.
            
            Agent Analysis Summary:
            {context_summary}
            
            Please:
            1. Get current market data using get_market_data tool for final confirmation
            2. Review trading decisions summary using get_trading_summary tool
            3. Check comprehensive audit history using get_audit_history tool
            4. Consider all agent recommendations, market conditions, and regulatory compliance
            5. Make a final trading decision (BUY/SELL/HOLD) with specific reasoning
            6. Determine appropriate risk level and position size percentage
            7. Save your final decision using save_final_decision tool
            8. Provide clear rationale explaining how you balanced different agent inputs
            
            Return a structured SupervisorDecision with your final recommendation and comprehensive rationale.
            """
            
            supervisor_result = self.agents["supervisor"].run_sync(supervisor_prompt, deps=deps)
            
            return {
                "agent": "supervisor",
                "decision": supervisor_result.output,
                "final_decision": True,
                "confidence": supervisor_result.output.confidence if hasattr(supervisor_result.output, 'confidence') else 0.90
            }
            
        except Exception as e:
            print(f"Error in supervisor decision: {str(e)}")
            return {"error": str(e), "final_decision": False}
    
    def _prepare_supervisor_context(self, all_analysis: Dict) -> str:
        """Prepare summary context for supervisor agent"""
        context = []
        
        for analysis_type, data in all_analysis.items():
            if isinstance(data, dict) and "analysis" in data:
                agent_name = data.get("agent", "unknown")
                analysis_data = data["analysis"]
                
                # Handle structured Pydantic responses
                if hasattr(analysis_data, 'model_dump'):
                    analysis_text = str(analysis_data.model_dump())
                else:
                    analysis_text = str(analysis_data)
                    
                context.append(f"\n{analysis_type.upper()} ({agent_name}):\n{analysis_text}")
        
        return "\n".join(context)