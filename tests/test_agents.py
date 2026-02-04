"""
Comprehensive Agent Testing Suite
Tests each agent individually with various market scenarios
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.pydantic_agents import PydanticTradingAgentSystem
from app.data.market_data import MarketData

def test_agent_suite():
    """Test all agents across different market scenarios"""
    print("=" * 70)
    print("AGENTIC SYSTEM TEST SUITE")
    print("=" * 70)

    # Initialize system
    try:
        system = PydanticTradingAgentSystem(use_openai=True)
        market_data = MarketData()
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False

    # Test scenarios with different market conditions
    test_symbols = {
        "stable_blue_chip": "AAPL",      # Large cap, stable
        "volatile_tech": "TSLA",          # High volatility
        "financial": "JPM",               # Bank stock
        "healthcare": "JNJ",              # Healthcare sector
        "etf": "SPY"                      # Market ETF
    }

    results = {}

    for scenario, symbol in test_symbols.items():
        print(f"\n{'='*70}")
        print(f"Testing Scenario: {scenario.upper()} ({symbol})")
        print(f"{'='*70}")

        try:
            # Get market data
            print(f"\n[0] Fetching market data for {symbol}...")
            data = market_data.get_stock_data(symbol)
            if data.empty:
                print(f"❌ No data available for {symbol}")
                results[scenario] = {
                    "symbol": symbol,
                    "status": "FAILED",
                    "error": "No market data available"
                }
                continue

            data = market_data.calculate_technical_indicators(data)
            print(f"    ✅ Market data retrieved ({len(data)} data points)")

            # Test Market Analyst
            print(f"\n[1] Testing Market Analyst Agent...")
            market_result = system.run_market_analysis(symbol, data)
            if "analysis" in market_result and market_result["analysis"]:
                print(f"    ✅ Market analysis completed")
                print(f"    📊 Current Price: ${market_result.get('current_price', 'N/A')}")
            else:
                raise Exception("Market analysis failed or returned empty")

            # Test Trading Signal
            print(f"\n[2] Testing Trading Signal Agent...")
            signal_result = system.run_trading_signal_analysis(symbol, data)
            if "analysis" in signal_result:
                analysis = signal_result["analysis"]
                if hasattr(analysis, 'decision'):
                    print(f"    ✅ Trading signal generated")
                    print(f"    📈 Signal: {analysis.decision}")
                    print(f"    ⚠️  Risk: {analysis.risk_level}")
                    print(f"    🎯 Confidence: {analysis.confidence:.2%}")
                else:
                    raise Exception("Trading signal missing decision field")
            else:
                raise Exception("Trading signal analysis failed")

            # Test Regulatory Agent
            print(f"\n[3] Testing Regulatory Agent...")
            reg_result = system.run_regulatory_compliance(symbol, market_result)
            if "analysis" in reg_result and reg_result["analysis"]:
                analysis = reg_result["analysis"]
                if hasattr(analysis, 'compliance_status'):
                    print(f"    ✅ Regulatory check completed")
                    print(f"    🏛️  Status: {analysis.compliance_status}")
                else:
                    print(f"    ✅ Regulatory check completed (legacy format)")
            else:
                raise Exception("Regulatory compliance check failed")

            # Test Risk Manager
            print(f"\n[4] Testing Risk Manager Agent...")
            risk_result = system.run_risk_management(symbol, data)
            if "analysis" in risk_result and risk_result["analysis"]:
                print(f"    ✅ Risk assessment completed")
            else:
                raise Exception("Risk management analysis failed")

            # Test Supervisor
            print(f"\n[5] Testing Supervisor Agent...")
            supervisor_result = system.run_supervisor_decision(symbol, market_result)
            if "decision" in supervisor_result and supervisor_result["decision"]:
                decision = supervisor_result["decision"]
                if hasattr(decision, 'final_decision'):
                    print(f"    ✅ Supervisor decision made")
                    print(f"    🎯 Final Decision: {decision.final_decision}")
                    print(f"    💪 Confidence: {decision.confidence:.2%}")
                else:
                    print(f"    ✅ Supervisor decision made (legacy format)")
            else:
                raise Exception("Supervisor decision failed")

            results[scenario] = {
                "symbol": symbol,
                "status": "PASSED",
                "market_analyst": "✅",
                "trading_signal": "✅",
                "regulatory": "✅",
                "risk_manager": "✅",
                "supervisor": "✅"
            }

            print(f"\n✅ All agents passed for {symbol}")

        except Exception as e:
            print(f"\n❌ Error in {scenario}: {str(e)}")
            results[scenario] = {
                "symbol": symbol,
                "status": "FAILED",
                "error": str(e)
            }

    # Summary Report
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for r in results.values() if r["status"] == "PASSED")
    total = len(results)

    print(f"\nResults: {passed}/{total} scenarios passed")
    print()

    for scenario, result in results.items():
        status_emoji = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_emoji} {scenario.ljust(20)}: {result['symbol'].ljust(6)} - {result['status']}")
        if result["status"] == "FAILED" and "error" in result:
            print(f"   └─ Error: {result['error']}")

    if passed == total:
        print(f"\n🎉 SUCCESS! All {total} test scenarios passed!")
    else:
        print(f"\n⚠️  WARNING: {total - passed} scenario(s) failed")

    return passed == total


def test_individual_agent(agent_name: str, symbol: str = "AAPL"):
    """Test a single agent in isolation"""
    print(f"\n{'='*70}")
    print(f"Testing Individual Agent: {agent_name}")
    print(f"{'='*70}")

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    data = market_data.get_stock_data(symbol)
    if data.empty:
        print(f"❌ No data for {symbol}")
        return False

    data = market_data.calculate_technical_indicators(data)

    try:
        if agent_name.lower() == "market":
            result = system.run_market_analysis(symbol, data)
        elif agent_name.lower() == "trading_signal":
            result = system.run_trading_signal_analysis(symbol, data)
        elif agent_name.lower() == "regulatory":
            market_result = system.run_market_analysis(symbol, data)
            result = system.run_regulatory_compliance(symbol, market_result)
        elif agent_name.lower() == "risk":
            result = system.run_risk_management(symbol, data)
        elif agent_name.lower() == "supervisor":
            market_result = system.run_market_analysis(symbol, data)
            result = system.run_supervisor_decision(symbol, market_result)
        else:
            print(f"❌ Unknown agent: {agent_name}")
            return False

        print(f"✅ {agent_name} agent test passed")
        print(f"Result keys: {result.keys()}")
        return True

    except Exception as e:
        print(f"❌ {agent_name} agent test failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test trading agents")
    parser.add_argument("--agent", type=str, help="Test specific agent (market, trading_signal, regulatory, risk, supervisor)")
    parser.add_argument("--symbol", type=str, default="AAPL", help="Stock symbol to test with")

    args = parser.parse_args()

    if args.agent:
        # Test individual agent
        success = test_individual_agent(args.agent, args.symbol)
    else:
        # Run full test suite
        success = test_agent_suite()

    sys.exit(0 if success else 1)
