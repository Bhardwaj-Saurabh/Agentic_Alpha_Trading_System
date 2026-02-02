# """Smolagents-based trading agents with enhanced tool integration"""

# import os
# from smolagents import ToolCallingAgent, LiteLLMModel, InferenceClientModel
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# from config import Config
# from tools.market_tools import (
#     get_stock_data, calculate_fibonacci_levels, 
#     analyze_market_sentiment, check_regulation_m_compliance
# )
# from tools.storage_tools import (
#     save_trading_decision, save_audit_entry, get_audit_trail,
#     get_trading_decisions_summary, analyze_decision_patterns
# )

# class SmolTradingAgentSystem:
#     """Advanced trading agent system using smolagents framework"""
    
#     def __init__(self, use_openai=True):
#         """Initialize the multi-agent trading system"""
        
#         # Initialize LLM model
#         try:
#             if use_openai and Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
#                 self.model = LiteLLMModel(
#                     model_id="gpt-4o",
#                     api_key=Config.OPENAI_API_KEY
#                 )
#             else:
#                 # Fallback to Hugging Face model (free, no API key needed)
#                 self.model = InferenceClientModel()
#         except Exception as e:
#             print(f"Model initialization issue: {e}")
#             # Double fallback to ensure system works
#             self.model = InferenceClientModel()
        
#         # Create specialized trading agents
#         self.agents = self._create_agents()
        
#     def _create_agents(self):
#         """Create specialized trading agents with different tool sets"""
        
#         # Market Data Analyst Agent
#         market_agent = ToolCallingAgent(
#             tools=[
#                 get_stock_data,
#                 calculate_fibonacci_levels,
#                 analyze_market_sentiment
#             ],
#             model=self.model,
#             name="market_analyst",
#             description="Specializes in market data analysis, technical indicators, and sentiment analysis. Uses tools to fetch stock data, calculate Fibonacci levels, and analyze market sentiment across different timeframes."
#         )
        
#         # Strategy Agent - focuses on trading strategies
#         strategy_agent = ToolCallingAgent(
#             tools=[
#                 get_stock_data,
#                 calculate_fibonacci_levels,
#                 save_trading_decision,
#                 save_audit_entry
#             ],
#             model=self.model,
#             name="strategy_agent", 
#             description="Develops trading strategies using technical analysis tools. Analyzes market data and generates buy/sell signals with confidence scores using predefined analysis functions."
#         )
        
#         # Compliance & Regulatory Agent
#         regulatory_agent = ToolCallingAgent(
#             tools=[
#                 check_regulation_m_compliance,
#                 get_stock_data,
#                 save_audit_entry,
#                 get_audit_trail
#             ],
#             model=self.model,
#             name="regulatory_agent",
#             description="Ensures regulatory compliance with SEC Regulation M using compliance checking tools. Can identify violations and maintain detailed audit trails through tool calls."
#         )
        
#         # Portfolio Manager & Supervisor Agent
#         supervisor_agent = ToolCallingAgent(
#             tools=[
#                 get_stock_data,
#                 save_audit_entry,
#                 get_trading_decisions_summary,
#                 analyze_decision_patterns,
#                 get_audit_trail
#             ],
#             model=self.model,
#             name="supervisor",
#             description="Senior portfolio manager that makes final trading decisions using analysis tools. Reviews data from other agents and makes comprehensive trading decisions."
#         )
        
#         # Risk Management Agent
#         risk_agent = ToolCallingAgent(
#             tools=[
#                 get_stock_data,
#                 analyze_market_sentiment,
#                 analyze_decision_patterns,
#                 save_audit_entry
#             ],
#             model=self.model,
#             name="risk_manager",
#             description="Focuses on risk assessment using market analysis tools. Evaluates volatility, position sizing, and overall portfolio risk exposure through tool calls."
#         )
        
#         return {
#             "market_analyst": market_agent,
#             "strategy_agent": strategy_agent,
#             "regulatory_agent": regulatory_agent,
#             "supervisor": supervisor_agent,
#             "risk_manager": risk_agent
#         }
    
#     def run_market_analysis(self, symbol: str, quick_mode=False):
#         """Run comprehensive market analysis using specialized agents"""
#         try:
#             results = {}
            
#             # Market Data Analysis
#             market_prompt = f"""
#             Analyze the market data for {symbol}. Please:
#             1. Get current stock data with technical indicators
#             2. Analyze market sentiment over the past 3 days
#             3. Calculate Fibonacci retracement levels
#             4. Provide a summary of key findings including price trends, volume patterns, and technical signal strength
            
#             Focus on actionable insights for trading decisions.
#             """
            
#             market_result = self.agents["market_analyst"].run(market_prompt)
#             results["market_analysis"] = {
#                 "agent": "market_analyst",
#                 "analysis": market_result,
#                 "confidence": 0.8  # Placeholder
#             }
            
#             if not quick_mode:
#                 # Strategy Analysis
#                 strategy_prompt = f"""
#                 Based on the stock data for {symbol}, develop trading strategies:
#                 1. Analyze MACD crossovers and momentum indicators
#                 2. Check Bollinger Band signals for entry/exit points
#                 3. Evaluate Fibonacci levels for support and resistance
#                 4. Generate a trading signal (BUY/SELL/HOLD) with confidence score
#                 5. Save your decision using the save_trading_decision tool
                
#                 Provide specific entry/exit points and position sizing recommendations.
#                 """
                
#                 strategy_result = self.agents["strategy_agent"].run(strategy_prompt)
#                 results["strategy_analysis"] = {
#                     "agent": "strategy_agent", 
#                     "analysis": strategy_result,
#                     "confidence": 0.75
#                 }
                
#                 # Risk Assessment
#                 risk_prompt = f"""
#                 Assess the risk profile for trading {symbol}:
#                 1. Analyze recent volatility and price patterns
#                 2. Review historical decision patterns for this symbol
#                 3. Evaluate market sentiment and potential risks
#                 4. Recommend position sizing and risk management measures
#                 5. Save risk assessment using save_audit_entry tool
                
#                 Focus on downside protection and risk-adjusted returns.
#                 """
                
#                 risk_result = self.agents["risk_manager"].run(risk_prompt)
#                 results["risk_analysis"] = {
#                     "agent": "risk_manager",
#                     "analysis": risk_result, 
#                     "confidence": 0.85
#                 }
            
#             return results
            
#         except Exception as e:
#             print(f"Error in market analysis: {str(e)}")
#             return {"error": str(e)}
    
#     def run_regulatory_compliance(self, symbol: str, trading_signals: dict):
#         """Run regulatory compliance check"""
#         try:
#             compliance_prompt = f"""
#             Perform SEC Regulation M compliance check for {symbol}:
#             1. Check current trading signals for potential violations: {trading_signals}
#             2. Analyze recent volume and price patterns for distribution indicators
#             3. Determine if any trades should be blocked for compliance reasons
#             4. Save detailed compliance analysis using save_audit_entry tool
#             5. Provide clear recommendation: APPROVED, PROCEED_WITH_CAUTION, or BLOCK_TRADES
            
#             Focus on preventing market manipulation and ensuring regulatory compliance.
#             """
            
#             compliance_result = self.agents["regulatory_agent"].run(compliance_prompt)
            
#             return {
#                 "agent": "regulatory_agent",
#                 "analysis": compliance_result,
#                 "compliance_check": True
#             }
            
#         except Exception as e:
#             print(f"Error in compliance check: {str(e)}")
#             return {"error": str(e), "compliance_check": False}
    
#     def run_supervisor_decision(self, symbol: str, all_analysis: dict):
#         """Run final supervisor decision combining all agent inputs"""
#         try:
#             # Prepare context from all agents
#             context_summary = self._prepare_supervisor_context(all_analysis)
            
#             supervisor_prompt = f"""
#             As the senior portfolio manager, make the final trading decision for {symbol}.
            
#             Agent Analysis Summary:
#             {context_summary}
            
#             Please:
#             1. Review all agent recommendations and analysis
#             2. Consider market conditions, regulatory compliance, and risk factors
#             3. Make a final trading decision (BUY/SELL/HOLD) with specific reasoning
#             4. Recommend position size as a percentage of portfolio
#             5. Assess overall risk level (LOW/MEDIUM/HIGH)
#             6. Save your final decision using save_audit_entry tool with decision_type='SUPERVISOR'
#             7. Provide clear rationale explaining how you weighed different agent inputs
            
#             Your decision should balance profit potential with risk management and regulatory compliance.
#             """
            
#             supervisor_result = self.agents["supervisor"].run(supervisor_prompt)
            
#             return {
#                 "agent": "supervisor",
#                 "decision": supervisor_result,
#                 "final_decision": True,
#                 "confidence": 0.90
#             }
            
#         except Exception as e:
#             print(f"Error in supervisor decision: {str(e)}")
#             return {"error": str(e), "final_decision": False}
    
#     def _prepare_supervisor_context(self, all_analysis: dict):
#         """Prepare summary context for supervisor agent"""
#         context = []
        
#         for analysis_type, data in all_analysis.items():
#             if isinstance(data, dict) and "analysis" in data:
#                 agent_name = data.get("agent", "unknown")
#                 analysis_text = str(data["analysis"])[:300] + "..." if len(str(data["analysis"])) > 300 else str(data["analysis"])
#                 context.append(f"\n{analysis_type.upper()} ({agent_name}):\n{analysis_text}")
        
#         return "\n".join(context)
    
#     def get_audit_summary(self, symbol: str):
#         """Get audit trail summary using storage tools"""
#         try:
#             audit_prompt = f"""
#             Retrieve and analyze the audit trail for {symbol}:
#             1. Get recent audit trail entries using get_audit_trail tool
#             2. Analyze decision patterns using analyze_decision_patterns tool
#             3. Summarize key compliance and decision trends
#             4. Highlight any important patterns or concerns
            
#             Focus on regulatory compliance and decision quality over time.
#             """
            
#             audit_result = self.agents["regulatory_agent"].run(audit_prompt)
            
#             return {
#                 "agent": "regulatory_agent",
#                 "audit_summary": audit_result
#             }
            
#         except Exception as e:
#             print(f"Error getting audit summary: {str(e)}")
#             return {"error": str(e)}