import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db.database import Database
from data.market_data import MarketData
from data.enhanced_market_data import EnhancedMarketData
from agents.pydantic_agents import PydanticTradingAgentSystem, Dependencies

# Initialize components
storage = Database()
market_data = MarketData()
enhanced_data = EnhancedMarketData()


# Initialize PydanticAI system
@st.cache_resource
def get_pydantic_agents():
    return PydanticTradingAgentSystem(use_openai=True)

def extract_readable_text(analysis_obj, field_name, field_name2):
    if hasattr(analysis_obj, field_name):
        return getattr(analysis_obj, field_name)
    elif hasattr(analysis_obj, field_name2):
        return getattr(analysis_obj, field_name2)
    else:
        return str(analysis_obj)
            
# Individual Agent Functions
def run_market_analyst():
    """Run Market Analyst Agent individually"""
    try:
        pydantic_system = get_pydantic_agents()
        print(f"📈 Running Market Analyst for {st.session_state.symbol}...")
        
        #TODO:  This is optional.  We collect three types of information in the market analysis call and preserve
        # them in the session state for later use by other agents.  Right now this is convenient but 
        # can you change the code so that the strategy agent and risk manager do not depend on the market analysis call
        # but instead run on their own calls.  
        market_results = pydantic_system.run_market_analysis(st.session_state.symbol, st.session_state.data)
        
        if "error" in market_results:
            return {"error": market_results["error"]}
        
        market_analysis = market_results.get("market_analysis", {}).get("analysis", "No market analysis available")
        
        market_text = extract_readable_text(market_analysis, "market_analysis", "analysis")
        
        return {
            "analysis": market_text,
            "confidence": 0.8,
            "raw_results": market_results,
            "timestamp": pd.Timestamp.now()
        }
    except Exception as e:
        return {"error": str(e)}

def run_strategy_agent():
    """Run Strategy Agent individually"""
    # Check if Market Analyst has run
    if 'market_analysis' not in st.session_state or not st.session_state.market_analysis:
        return {"error": "❌ Please run Market Analyst first - Strategy Agent needs market data"}

    try:
        symbol = st.session_state.symbol
        print(f"🎯 Running Strategy Agent for {symbol}...")
        
        # Use market results from session state
        market_results = st.session_state.market_analysis["raw_results"]
        strategy_analysis = market_results.get("strategy_analysis", {}).get("analysis", "No strategy analysis available")
        
        strategy_text = extract_readable_text(strategy_analysis, "rationale", "rationale")
        
        return {
            "analysis": strategy_text,
            "confidence": 0.75,
            "timestamp": pd.Timestamp.now()
        }
    except Exception as e:
        return {"error": str(e)}

def run_risk_manager():
    """Run Risk Manager Agent individually"""
    # Check if Market Analyst has run
    if 'market_analysis' not in st.session_state or not st.session_state.market_analysis:
        return {"error": "❌ Please run Market Analyst first - Risk Manager needs market data"}

    try:
        symbol = st.session_state.symbol
        print(f"⚠️ Running Risk Manager for {symbol}...")
        
        # Use market results from session state
        market_results = st.session_state.market_analysis["raw_results"]
        risk_analysis = market_results.get("risk_analysis", {}).get("analysis", "No risk analysis available")
        
        risk_text = extract_readable_text(risk_analysis, "rationale", "rationale")
        
        return {
            "analysis": risk_text,
            "confidence": 0.85,
            "timestamp": pd.Timestamp.now()
        }
    except Exception as e:
        return {"error": str(e)}

def run_trading_signal_agent():
    """Run Trading Signal Agent individually"""
    try:
        pydantic_system = get_pydantic_agents()
        symbol = st.session_state.symbol
        print(f"📊 Running Trading Signal Agent for {symbol}...")

        signal_results = pydantic_system.run_trading_signal_analysis(symbol, st.session_state.data)

        if "error" in signal_results:
            return {"error": signal_results["error"]}

        signal_analysis = signal_results.get("analysis", "No signal analysis available")

        if hasattr(signal_analysis, 'decision'):
            decision_signal = signal_analysis.decision.value if hasattr(signal_analysis.decision, 'value') else str(signal_analysis.decision)
            risk_level = signal_analysis.risk_level.value if hasattr(signal_analysis.risk_level, 'value') else str(signal_analysis.risk_level)
            signal_text = f"SIGNAL: {decision_signal}\nRISK LEVEL: {risk_level}\n\nRATIONALE: {signal_analysis.rationale}"
            confidence = signal_analysis.confidence
        else:
            signal_text = str(signal_analysis)
            confidence = signal_results.get("confidence", 0.8)
            decision_signal = "HOLD"
            risk_level = "MEDIUM"

        return {
            "analysis": signal_text,
            "decision": decision_signal,
            "risk_level": risk_level,
            "confidence": confidence,
            "timestamp": pd.Timestamp.now()
        }
    except Exception as e:
        return {"error": str(e)}

def run_regulatory_agent(symbol):
    """Run Regulatory Agent individually"""
    # Check if other agents have run
    missing_agents = []
    if 'market_analysis' not in st.session_state or not st.session_state.market_analysis:
        missing_agents.append("Market Analyst")
    if 'strategy_analysis' not in st.session_state or not st.session_state.strategy_analysis:
        missing_agents.append("Strategy Agent")
    
    if missing_agents:
        return {"error": f"❌ Please run {', '.join(missing_agents)} first - Regulatory Agent needs their analysis"}
    
    try:
        pydantic_system = get_pydantic_agents()
        print(f"🏛️ Running Regulatory Agent for {symbol}...")
        
        # Use market results from session state
        market_results = st.session_state.market_analysis["raw_results"]
        regulatory_results = pydantic_system.run_regulatory_compliance(symbol, market_results)
        
        compliance_data = regulatory_results.get("analysis", "No regulatory analysis")
        if hasattr(compliance_data, 'explanation'):
            compliance_text = compliance_data.explanation
            status = compliance_data.compliance_status.value if hasattr(compliance_data.compliance_status, 'value') else str(compliance_data.compliance_status)
            recommendation = compliance_data.recommendation
        else:
            compliance_text = str(compliance_data)
            status = "PROCESSED_BY_PYDANTICAI"
            recommendation = "SEE_AGENT_OUTPUT"
        
        result = {
            "analysis": compliance_text,
            "compliance_status": status,
            "recommendation": recommendation,
            "confidence": 0.9,
            "timestamp": pd.Timestamp.now()
        }
        
        # Save audit entry for regulatory compliance
        storage.save_audit_entry(
            symbol=symbol,
            decision_type="REGULATORY",
            action=recommendation,
            confidence=0.9,
            rationale=compliance_text,
            compliance_status=status
        )
        
        return result
    except Exception as e:
        return {"error": str(e)}

def run_supervisor_agent(symbol):
    """Run Supervisor Agent individually"""
    # Check if ALL other agents have run
    missing_agents = []
    if 'market_analysis' not in st.session_state or not st.session_state.market_analysis:
        missing_agents.append("Market Analyst")
    if 'strategy_analysis' not in st.session_state or not st.session_state.strategy_analysis:
        missing_agents.append("Strategy Agent")
    if 'risk_analysis' not in st.session_state or not st.session_state.risk_analysis:
        missing_agents.append("Risk Manager")
    if 'regulatory_analysis' not in st.session_state or not st.session_state.regulatory_analysis:
        missing_agents.append("Regulatory Agent")
    
    if missing_agents:
        return {"error": f"❌ Please run {', '.join(missing_agents)} first - Supervisor needs ALL agent analysis"}
    
    try:
        pydantic_system = get_pydantic_agents()
        print(f"🎯 Running Supervisor Agent for {symbol}...")
        
        # Use market results from session state
        market_results = st.session_state.market_analysis["raw_results"]
        supervisor_results = pydantic_system.run_supervisor_decision(symbol, market_results)
        
        supervisor_data = supervisor_results.get("decision", "No supervisor decision available")
        if hasattr(supervisor_data, 'rationale'):
            decision_signal = supervisor_data.final_decision.value if hasattr(supervisor_data.final_decision, 'value') else str(supervisor_data.final_decision)
            decision_text = f"FINAL DECISION: {decision_signal}\n\nANALYSIS: {supervisor_data.rationale}"
            confidence = supervisor_data.confidence
        else:
            decision_text = str(supervisor_data)
            confidence = supervisor_results.get("confidence", 0.8)
            decision_signal = "HOLD"
        
        result = {
            "analysis": decision_text,
            "decision": decision_signal,
            "confidence": confidence,
            "timestamp": pd.Timestamp.now()
        }
        
        # Save audit entry for supervisor decision
        storage.save_audit_entry(
            symbol=symbol,
            decision_type="SUPERVISOR", 
            action=decision_signal,
            confidence=confidence,
            rationale=decision_text
        )
        
        return result
    except Exception as e:
        return {"error": str(e)}

def save_trade_to_database(symbol):
    """Save all agent results to CSV database when Trade button is clicked"""
    try:
        # Check if supervisor has run (which means all agents should have run)
        if 'supervisor_analysis' not in st.session_state or not st.session_state.supervisor_analysis:
            return "❌ Please run all agents first, especially Supervisor Agent, before executing trade"
        
        # Save each agent's decision to CSV
        if 'market_analysis' in st.session_state and st.session_state.market_analysis:
            storage.save_trading_decision(symbol, "Market Analysis Completed", 
                                        st.session_state.market_analysis['confidence'], 'market_analyst')
        
        if 'strategy_analysis' in st.session_state and st.session_state.strategy_analysis:
            storage.save_trading_decision(symbol, "Strategy Analysis Completed", 
                                        st.session_state.strategy_analysis['confidence'], 'strategy_agent')
        
        if 'risk_analysis' in st.session_state and st.session_state.risk_analysis:
            storage.save_trading_decision(symbol, "Risk Analysis Completed",
                                        st.session_state.risk_analysis['confidence'], 'risk_manager')

        if 'trading_signal_analysis' in st.session_state and st.session_state.trading_signal_analysis:
            storage.save_trading_decision(symbol, st.session_state.trading_signal_analysis['decision'],
                                        st.session_state.trading_signal_analysis['confidence'], 'trading_signal')

        if 'regulatory_analysis' in st.session_state and st.session_state.regulatory_analysis:
            storage.save_trading_decision(symbol, st.session_state.regulatory_analysis['recommendation'], 
                                        st.session_state.regulatory_analysis['confidence'], 'regulatory_agent')
        
        if 'supervisor_analysis' in st.session_state and st.session_state.supervisor_analysis:
            storage.save_trading_decision(symbol, st.session_state.supervisor_analysis['decision'], 
                                        st.session_state.supervisor_analysis['confidence'], 'supervisor')
        
        return f"✅ Trade executed and saved to database for {symbol} at {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
    except Exception as e:
        return f"❌ Error saving trade: {str(e)}"



# Streamlit UI for AI Agent Teaching
st.set_page_config(page_title="AI Agent Hedgefund", layout="wide")

# Initialize session state
if 'signals' not in st.session_state:
    st.session_state.signals = None
if 'trend_analysis' not in st.session_state:
    st.session_state.trend_analysis = None
if 'sentiment_analysis' not in st.session_state:
    st.session_state.sentiment_analysis = None
if 'trading_signal_analysis' not in st.session_state:
    st.session_state.trading_signal_analysis = None
if 'regulatory_analysis' not in st.session_state:
    st.session_state.regulatory_analysis = None
if 'decision' not in st.session_state:
    st.session_state.decision = None
if 'symbol' not in st.session_state:
    st.session_state.symbol = "AAPL"
if 'data' not in st.session_state:
    st.session_state.data = None
if 'chart_ready' not in st.session_state:
    st.session_state.chart_ready = False

# Main dashboard - single focused view
st.title("🤖 AI Agent Interaction Teaching Dashboard")

# Educational content about AI agents
st.markdown("""
This dashboard demonstrates how **PydanticAI** (the type-safe Python agent framework) enables AI agents to collaborate:
- **Market Analyst Agent**: Uses advanced tools to fetch stock data, calculate Fibonacci levels, and analyze sentiment
- **Strategy Agent**: Develops trading strategies using technical indicators and generates buy/sell signals
- **Regulatory Agent**: Ensures SEC Regulation M compliance and maintains detailed audit trails
- **Risk Manager Agent**: Assesses portfolio risk, volatility patterns, and position sizing
- **Supervisor Agent**: Makes final decisions by analyzing all agent inputs and managing portfolio exposure

""")

# Sidebar for symbol selection and controls
st.sidebar.markdown("### 📊 Stock Selection")

# Add popular symbols for easy selection
popular_symbols = market_data.get_popular_symbols()
selected_from_list = st.sidebar.selectbox("Choose a popular stock:",
                                          options=[''] + popular_symbols,
                                          format_func=lambda x: f"{x}"
                                          if x else "Select a symbol...")

# Manual input
new_symbol = st.sidebar.text_input("Or enter any symbol:",
                                   value=st.session_state.symbol)

# Use selected symbol if one was chosen from dropdown
if selected_from_list:
    new_symbol = selected_from_list

# Check if symbol changed
if new_symbol != st.session_state.symbol:
    st.session_state.symbol = new_symbol
    st.session_state.chart_ready = False
    st.session_state.data = None
    st.session_state.signals = None
    st.session_state.trend_analysis = None
    st.session_state.sentiment_analysis = None
    st.session_state.trading_signal_analysis = None
    st.session_state.regulatory_analysis = None
    st.session_state.decision = None

load_data_button = st.sidebar.button("Load Stock Data")
# Individual Agent Buttons - Replace old analyze button
st.sidebar.write("**🤖 Run Individual AI Agents:**")

market_button = st.sidebar.button("📈 Market Analyst", use_container_width=True, key="market_btn")
strategy_button = st.sidebar.button("🎯 Strategy Agent", use_container_width=True, key="strategy_btn")
risk_button = st.sidebar.button("⚠️ Risk Manager", use_container_width=True, key="risk_btn")
trading_signal_button = st.sidebar.button("📊 Trading Signal Agent", use_container_width=True, key="trading_signal_btn")
regulatory_button = st.sidebar.button("🏛️ Regulatory Agent", use_container_width=True, key="regulatory_btn")
supervisor_button = st.sidebar.button("🎯 Supervisor Agent", use_container_width=True, key="supervisor_btn")

st.sidebar.write("---")
st.sidebar.write("**💰 Execute Trade:**")
trade_button = st.sidebar.button("🚀 EXECUTE TRADE", type="primary", use_container_width=True, key="trade_btn")


# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Price Chart with Technical Indicators")

    if load_data_button or st.session_state.chart_ready:
        with st.spinner(f"Loading data for {st.session_state.symbol}..."):
            if load_data_button or st.session_state.data is None:
                data = market_data.get_stock_data(st.session_state.symbol)
                if not data.empty:
                    data = market_data.calculate_technical_indicators(data)
                    st.session_state.data = data
                    st.session_state.chart_ready = True
                else:
                    st.error(
                        f"No data available for {st.session_state.symbol}. Please try another symbol."
                    )
                    fig = go.Figure()
                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state.chart_ready = False
            else:
                data = st.session_state.data

        if st.session_state.chart_ready and not data.empty:
            # Display real-time market data with live APIs
            st.markdown("### Real-Time Market Data")

            # Fetch real-time quote
            with st.spinner("Fetching real-time data..."):
                real_time_quote = enhanced_data.get_real_time_quote(st.session_state.symbol)

            if real_time_quote and "error" not in real_time_quote:
                # Display price metrics
                col_price1, col_price2, col_price3, col_price4 = st.columns(4)

                # Helper function to safely convert values
                def safe_float(value, default=0.0):
                    try:
                        if isinstance(value, str):
                            # Remove % sign and convert
                            value = value.replace('%', '').strip()
                        return float(value)
                    except (ValueError, TypeError, AttributeError):
                        return default

                def safe_int(value, default=0):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return default

                with col_price1:
                    price = safe_float(real_time_quote.get('price', 0))
                    change_pct = safe_float(real_time_quote.get('change_percent', 0))
                    st.metric(
                        label="Current Price",
                        value=f"${price:.2f}",
                        delta=f"{change_pct:.2f}%"
                    )

                with col_price2:
                    change = safe_float(real_time_quote.get('change', 0))
                    st.metric(
                        label="Day Change",
                        value=f"${change:.2f}"
                    )

                with col_price3:
                    volume = safe_int(real_time_quote.get('volume', 0))
                    st.metric(
                        label="Volume",
                        value=f"{volume:,.0f}"
                    )

                with col_price4:
                    st.metric(
                        label="Data Source",
                        value=real_time_quote.get('source', 'Unknown')
                    )

                # Company Fundamentals
                with st.expander("Company Fundamentals & Metrics", expanded=False):
                    fundamentals = enhanced_data.get_company_fundamentals(st.session_state.symbol)

                    if fundamentals and "error" not in fundamentals:
                        fund_col1, fund_col2, fund_col3, fund_col4 = st.columns(4)

                        with fund_col1:
                            st.metric("Market Cap", fundamentals.get('market_cap', 'N/A'))
                            st.metric("P/E Ratio", fundamentals.get('pe_ratio', 'N/A'))

                        with fund_col2:
                            eps = fundamentals.get('eps', 'N/A')
                            eps_display = f"${safe_float(eps):.2f}" if eps != 'N/A' else 'N/A'
                            st.metric("EPS", eps_display)
                            st.metric("Dividend Yield", fundamentals.get('dividend_yield', 'N/A'))

                        with fund_col3:
                            week_high = fundamentals.get('week_52_high', 'N/A')
                            week_low = fundamentals.get('week_52_low', 'N/A')
                            high_display = f"${safe_float(week_high):.2f}" if week_high != 'N/A' else 'N/A'
                            low_display = f"${safe_float(week_low):.2f}" if week_low != 'N/A' else 'N/A'
                            st.metric("52 Week High", high_display)
                            st.metric("52 Week Low", low_display)

                        with fund_col4:
                            st.metric("Beta", fundamentals.get('beta', 'N/A'))
                            avg_vol = fundamentals.get('avg_volume', 'N/A')
                            vol_display = f"{safe_int(avg_vol):,.0f}" if avg_vol != 'N/A' else 'N/A'
                            st.metric("Avg Volume", vol_display)

                        st.write(f"**Company:** {fundamentals.get('name', 'N/A')}")
                        st.write(f"**Sector:** {fundamentals.get('sector', 'N/A')}")
                        st.write(f"**Industry:** {fundamentals.get('industry', 'N/A')}")
                    else:
                        st.info("Fundamental data not available")

                # News & Sentiment Analysis
                with st.expander("AI-Powered News & Sentiment", expanded=False):
                    with st.spinner("Analyzing news sentiment..."):
                        news_data = enhanced_data.get_news_sentiment(
                            st.session_state.symbol,
                            query=f"{st.session_state.symbol} stock market news"
                        )

                    if news_data and "articles" in news_data:
                        articles = news_data.get("articles", [])
                        overall_sentiment = news_data.get("overall_sentiment", "NEUTRAL")

                        # Display overall sentiment
                        if overall_sentiment == "POSITIVE":
                            st.success(f"Overall Sentiment: {overall_sentiment}")
                        elif overall_sentiment == "NEGATIVE":
                            st.error(f"Overall Sentiment: {overall_sentiment}")
                        else:
                            st.info(f"Overall Sentiment: {overall_sentiment}")

                        st.write(f"**Total Articles Analyzed:** {len(articles)}")

                        # Display articles
                        for i, article in enumerate(articles[:5], 1):
                            st.markdown(f"**{i}. [{article.get('title', 'No title')}]({article.get('url', '#')})**")
                            st.write(f"*Source: {article.get('source', 'Unknown')}*")
                            score = safe_float(article.get('score', 0))
                            st.write(f"Sentiment: {article.get('sentiment', 'NEUTRAL')} | Score: {score:.2f}")
                            st.write("---")
                    else:
                        st.info("No recent news articles found")
            else:
                st.warning("Unable to fetch real-time data. Using historical data only.")

            st.markdown("---")

            fig = go.Figure()

            # Candlestick chart
            fig.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               name='OHLC'))

            # Bollinger Bands if available
            if 'Upper_Band' in data.columns and 'Lower_Band' in data.columns and pd.notna(
                    data['Upper_Band'].iloc[-1]):
                fig.add_trace(
                    go.Scatter(x=data.index,
                               y=data['Upper_Band'],
                               name='Upper Band',
                               line=dict(color='gray', dash='dash')))

                fig.add_trace(
                    go.Scatter(x=data.index,
                               y=data['Lower_Band'],
                               name='Lower Band',
                               line=dict(color='gray', dash='dash'),
                               fill='tonexty'))

            fig.update_layout(title=f"{st.session_state.symbol} Stock Price")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            f"Click 'Load Stock Data' to view the price chart for {st.session_state.symbol}"
        )

# Handle Individual Agent Button Clicks
if 'data' in st.session_state and st.session_state.data is not None and not st.session_state.data.empty:
    symbol = st.session_state.symbol
    
    # Market Analyst Button
    if market_button:
        with st.spinner("📈 Running Market Analyst..."):
            result = run_market_analyst()
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.market_analysis = result
                st.success("✅ Market Analyst completed!")
                st.rerun()
    
    # Strategy Agent Button
    if strategy_button:
        with st.spinner("🎯 Running Strategy Agent..."):
            result = run_strategy_agent()
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.strategy_analysis = result
                st.success("✅ Strategy Agent completed!")
                st.rerun()
    
    # Risk Manager Button
    if risk_button:
        with st.spinner("⚠️ Running Risk Manager..."):
            result = run_risk_manager()
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.risk_analysis = result
                st.success("✅ Risk Manager completed!")
                st.rerun()

    # Trading Signal Agent Button
    if trading_signal_button:
        with st.spinner("📊 Running Trading Signal Agent..."):
            result = run_trading_signal_agent()
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.trading_signal_analysis = result
                st.success("✅ Trading Signal Agent completed!")
                st.rerun()

    # Regulatory Agent Button
    if regulatory_button:
        with st.spinner("🏛️ Running Regulatory Agent..."):
            result = run_regulatory_agent(symbol)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.regulatory_analysis = result
                st.success("✅ Regulatory Agent completed!")
                st.rerun()
    
    # Supervisor Agent Button
    if supervisor_button:
        with st.spinner("🎯 Running Supervisor Agent..."):
            result = run_supervisor_agent(symbol)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.supervisor_analysis = result
                st.success("✅ Supervisor Agent completed!")
                st.rerun()
    
    # Trade Button
    if trade_button:
        with st.spinner("💰 Executing trade and saving to database..."):
            trade_result = save_trade_to_database(symbol)
            if "❌" in trade_result:
                st.error(trade_result)
            else:
                st.success(trade_result)
                st.rerun()
else:
    if market_button or strategy_button or risk_button or trading_signal_button or regulatory_button or supervisor_button or trade_button:
        st.error("Please load stock data first by clicking 'Load Stock Data'.")

with col2:
    st.subheader("🤖 Individual AI Agent Results")
    
    # Show execution progress
    agents_run = 0
    total_agents = 6

    if 'market_analysis' in st.session_state and st.session_state.market_analysis:
        agents_run += 1
    if 'strategy_analysis' in st.session_state and st.session_state.strategy_analysis:
        agents_run += 1
    if 'risk_analysis' in st.session_state and st.session_state.risk_analysis:
        agents_run += 1
    if 'trading_signal_analysis' in st.session_state and st.session_state.trading_signal_analysis:
        agents_run += 1
    if 'regulatory_analysis' in st.session_state and st.session_state.regulatory_analysis:
        agents_run += 1
    if 'supervisor_analysis' in st.session_state and st.session_state.supervisor_analysis:
        agents_run += 1
    
    progress = agents_run / total_agents
    st.write(f"**Analysis Progress: {agents_run}/{total_agents} agents completed**")
    st.progress(progress)
    
    if agents_run == total_agents:
        st.success("🎉 All agents completed! Click Execute Trade to save results to database.")
    elif agents_run > 0:
        st.info(f"📊 {agents_run} agents completed. Continue running remaining agents.")

    # Market Analyst Results
    if 'market_analysis' in st.session_state and st.session_state.market_analysis:
        with st.expander("📈 Market Analyst Results", expanded=False):
            result = st.session_state.market_analysis
            st.write(result['analysis'])
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("📈 Market Analyst: Not run yet - Click button in sidebar")
    
    # Strategy Agent Results
    if 'strategy_analysis' in st.session_state and st.session_state.strategy_analysis:
        with st.expander("🎯 Strategy Agent Results", expanded=False):
            result = st.session_state.strategy_analysis
            st.write(result['analysis'])
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("🎯 Strategy Agent: Not run yet (requires Market Analyst first)")
    
    # Risk Manager Results
    if 'risk_analysis' in st.session_state and st.session_state.risk_analysis:
        with st.expander("⚠️ Risk Manager Results", expanded=False):
            result = st.session_state.risk_analysis
            st.write(result['analysis'])
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("⚠️ Risk Manager: Not run yet (requires Market Analyst first)")

    # Trading Signal Agent Results
    if 'trading_signal_analysis' in st.session_state and st.session_state.trading_signal_analysis:
        with st.expander("📊 Trading Signal Agent Results", expanded=True):
            result = st.session_state.trading_signal_analysis
            st.write(result['analysis'])

            # Highlight the signal decision
            decision = result.get('decision', 'HOLD')
            if decision == 'BUY':
                st.success(f"🟢 **Signal: {decision}**")
            elif decision == 'SELL':
                st.error(f"🔴 **Signal: {decision}**")
            else:
                st.warning(f"🟡 **Signal: {decision}**")

            st.write(f"**Risk Level:** {result.get('risk_level', 'MEDIUM')}")
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("📊 Trading Signal Agent: Not run yet - Click button in sidebar")

    # Regulatory Agent Results
    if 'regulatory_analysis' in st.session_state and st.session_state.regulatory_analysis:
        with st.expander("🏛️ Regulatory Agent Results", expanded=False):
            result = st.session_state.regulatory_analysis
            st.write(result['analysis'])
            st.write(f"**Status:** {result['compliance_status']}")
            st.write(f"**Recommendation:** {result['recommendation']}")
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("🏛️ Regulatory Agent: Not run yet (requires Market Analyst + Strategy Agent)")
    
    # Supervisor Agent Results
    if 'supervisor_analysis' in st.session_state and st.session_state.supervisor_analysis:
        with st.expander("🎯 Supervisor Agent Results", expanded=False):
            result = st.session_state.supervisor_analysis
            st.write(result['analysis'])
            st.write(f"**Final Decision:** {result['decision']}")
            st.write(f"**Confidence:** {result['confidence']:.1%}")
            st.write(f"**Completed:** {result['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("🎯 Supervisor Agent: Not run yet (requires ALL other agents)")

    if st.session_state.trend_analysis:
        st.write("**Market Trend Analysis:**")
        for timeframe, analysis in st.session_state.trend_analysis.items():
            st.write(f"- {timeframe}: {analysis['analysis']}")

    if st.session_state.sentiment_analysis:
        st.write("**Sentiment Analysis:**")
        for timeframe, analysis in st.session_state.sentiment_analysis.items():
            st.write(f"- {timeframe}: {analysis['analysis']}")


    # Final supervisor decision
    if st.session_state.decision:
        st.write("---")
        st.write("**🎯 Supervisor Agent Final Decision:**")
        st.write(
            st.session_state.decision.get('decision', 'No decision available'))
        st.write(
            f"**Confidence:** {st.session_state.decision.get('confidence', 0.0):.2f}"
        )

        # Note: PydanticAI agents automatically save decisions using their built-in tools
        # This demonstrates how agents can use storage tools independently
        st.info(
            "💡 **PydanticAI Integration**: The agents automatically saved their decisions using built-in storage tools during analysis!"
        )

# Add a data viewer section at the bottom
st.write("---")
st.subheader("📁 Stored AI Agent Data")

# Show recent decisions in an expandable section
with st.expander("View Recent Agent Decisions", expanded=False):
    try:
        summary = storage.get_all_decisions_summary()

        if summary["total_decisions"] > 0:
            st.write(
                f"**Total Decisions Stored:** {summary['total_decisions']}")
            st.write(f"**Active Agents:** {', '.join(summary['agents'])}")
            st.write(f"**Analyzed Symbols:** {', '.join(summary['symbols'])}")

            st.write("**Recent Decisions:**")
            recent_df = pd.DataFrame(summary["latest_decisions"])
            if len(recent_df) > 0:
                # Format the dataframe for better display
                recent_df['created_at'] = pd.to_datetime(
                    recent_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                recent_df['confidence'] = recent_df['confidence'].round(2)
                # Keep full decision text without truncation

                st.dataframe(recent_df[[
                    'symbol', 'agent_name', 'decision', 'confidence',
                    'created_at'
                ]],
                             use_container_width=True,
                             hide_index=True)
        else:
            st.info(
                "No agent decisions stored yet. Run an analysis to see data appear here!"
            )

    except Exception as e:
        st.error(f"Error reading stored data: {str(e)}")

# Show PydanticAI Tools Integration
with st.expander("🛠️ PydanticAI Tools & Agent Actions", expanded=False):
    st.markdown("""
    **Advanced Tool Integration with PydanticAI:**
    
    PydanticAI provides type-safe tools and structured responses that our AI agents use to perform complex analysis:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📊 Market Analysis Tools:**
        - `get_stock_data()` - Fetches real-time stock data with technical indicators
        - `calculate_fibonacci_levels()` - Computes retracement levels for entry/exit points  
        - `analyze_market_sentiment()` - Processes price action and volume for sentiment analysis
        
        **🏛️ Compliance Tools:**
        - `check_regulation_m_compliance()` - Monitors SEC regulation violations
        - `save_audit_entry()` - Maintains detailed compliance audit trails
        - `get_audit_trail()` - Retrieves historical compliance decisions
        """)

    with col2:
        st.markdown("""
        **💾 Storage & Analysis Tools:**
        - `save_trading_decision()` - Stores agent decisions with confidence scores
        - `analyze_decision_patterns()` - Identifies trends in agent decision-making
        - `get_trading_decisions_summary()` - Provides comprehensive decision analytics
        
        """)


# Show audit trail for compliance review
with st.expander("📋 Audit Trail & Compliance Review", expanded=False):
    try:
        audit_summary = storage.get_audit_summary()

        if audit_summary["total_entries"] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Audit Entries",
                          audit_summary["total_entries"])
            with col2:
                st.metric("Supervisor Decisions",
                          audit_summary["supervisor_decisions"])
            with col3:
                st.metric("Regulatory Reviews",
                          audit_summary["regulatory_decisions"])

            st.write("**Recent Audit Entries:**")
            audit_trail = storage.get_audit_trail(limit=10)

            if audit_trail:
                audit_df = pd.DataFrame(audit_trail)
                # Format for display
                audit_df['timestamp'] = pd.to_datetime(
                    audit_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                audit_df['confidence'] = audit_df['confidence'].round(2)
                # Keep full rationale text without truncation

                display_columns = [
                    'symbol', 'decision_type', 'action', 'confidence',
                    'compliance_status', 'timestamp'
                ]
                st.dataframe(audit_df[display_columns],
                             use_container_width=True,
                             hide_index=True)

                # Show detailed view for specific symbol
                if st.session_state.symbol:
                    symbol_audit = storage.get_audit_trail(
                        symbol=st.session_state.symbol, limit=5)
                    if symbol_audit:
                        st.write(
                            f"**Detailed Audit for {st.session_state.symbol}:**"
                        )
                        for entry in symbol_audit:
                            with st.container():
                                st.markdown(
                                    f"**{entry['decision_type']}** - {entry['action']} (Confidence: {entry['confidence']:.2f})"
                                )
                                st.text(f"Time: {entry['timestamp']}")
                                
                                # Handle compliance status with NaN checking
                                compliance = entry.get('compliance_status', '')
                                if compliance and str(compliance).lower() not in ['nan', 'none', '']:
                                    st.text(f"Compliance: {compliance}")
                                
                                # Handle blocked trades with NaN checking  
                                blocked = entry.get('blocked_trades', '')
                                if blocked and str(blocked).lower() not in ['nan', 'none', '']:
                                    st.text(f"Blocked Trades: {blocked}")
                                
                                # Handle rationale with NaN checking
                                rationale = entry.get('rationale', '')
                                if rationale and str(rationale).lower() not in ['nan', 'none', '']:
                                    st.text(f"Rationale: {rationale}")
                                st.markdown("---")
        else:
            st.info(
                "No audit entries yet. Run an analysis to create audit trail!")

    except Exception as e:
        st.error(f"Error reading audit trail: {str(e)}")

# Show file locations for educational purposes
with st.expander("📂 Data Storage Information", expanded=False):
    st.markdown("""
    **CSV File Storage:**
    - All AI agent decisions are saved to local CSV files
    - No database required - perfect for learning and development
    - Data persists between sessions
    
    **File Locations:**
    - `data_storage/trading_decisions.csv` - All agent decisions and analysis results
    - `data_storage/trading_signals.csv` - Individual trading signals  
    - `data_storage/screened_stocks.csv` - Stock screening results
    - `data_storage/audit_trail.csv` - **Detailed audit trail for compliance review**
    
    """)

    if st.button("🗑️ Clear All Stored Data"):
        try:
            # Clear database tables
            with storage.conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE trading_decisions CASCADE")
                cur.execute("TRUNCATE TABLE audit_trail CASCADE")
                cur.execute("TRUNCATE TABLE trading_signals CASCADE")
                cur.execute("TRUNCATE TABLE screened_stocks CASCADE")
                storage.conn.commit()
            st.success("All stored data cleared from database!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
