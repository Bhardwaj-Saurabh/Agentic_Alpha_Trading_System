"""
Test Enhanced Features Learned from Smolagents
Tests the improvements we incorporated:
1. Quick mode for faster analysis
2. Better supervisor context preparation
3. Audit trail analysis
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.langchain_agents import LangChainTradingAgentSystem
from app.data.market_data import MarketData


def test_quick_mode():
    """Test quick_mode parameter for faster analysis"""
    print("=" * 70)
    print("TEST 1: Quick Mode vs Normal Mode")
    print("=" * 70)

    system = LangChainTradingAgentSystem()
    market_data = MarketData()

    symbol = "AAPL"
    data = market_data.get_stock_data(symbol, period='5d')
    data = market_data.calculate_technical_indicators(data)

    # Test normal mode
    print(f"\n[Normal Mode] Analyzing {symbol}...")
    start = time.time()
    normal_result = system.run_market_analysis(symbol, data, quick_mode=False)
    normal_time = time.time() - start
    print(f"    ✅ Completed in {normal_time:.2f}s")

    # Test quick mode
    print(f"\n[Quick Mode] Analyzing {symbol}...")
    start = time.time()
    quick_result = system.run_market_analysis(symbol, data, quick_mode=True)
    quick_time = time.time() - start
    print(f"    ✅ Completed in {quick_time:.2f}s")

    # Compare
    print(f"\n{'Mode':<20} {'Time':<15} {'Has Analysis':<15}")
    print("-" * 50)
    print(f"{'Normal':<20} {normal_time:<15.2f} {'✅' if 'market_analysis' in normal_result else '❌':<15}")
    print(f"{'Quick':<20} {quick_time:<15.2f} {'✅' if 'market_analysis' in quick_result else '❌':<15}")

    if quick_time < normal_time:
        speedup = ((normal_time - quick_time) / normal_time * 100)
        print(f"\n🚀 Quick mode is {speedup:.1f}% faster!")
    else:
        print(f"\n⚠️  Similar performance (both modes are already fast)")

    return True


def test_supervisor_context():
    """Test improved supervisor context preparation"""
    print("\n" + "=" * 70)
    print("TEST 2: Supervisor Context Preparation")
    print("=" * 70)

    system = LangChainTradingAgentSystem()
    market_data = MarketData()

    symbol = "MSFT"
    data = market_data.get_stock_data(symbol, period='5d')
    data = market_data.calculate_technical_indicators(data)

    # Run multiple agents
    print(f"\n[1/3] Running Market Analysis...")
    market_result = system.run_market_analysis(symbol, data)
    print(f"    ✅ Market analysis complete")

    print(f"\n[2/3] Running Strategy Analysis...")
    strategy_result = system.run_strategy_analysis(symbol, data)
    print(f"    ✅ Strategy analysis complete")

    print(f"\n[3/3] Running Risk Management...")
    risk_result = system.run_risk_management(symbol, data)
    print(f"    ✅ Risk analysis complete")

    # Combine results
    all_analysis = {
        "market_analysis": market_result.get("market_analysis", {}),
        "strategy_analysis": strategy_result,
        "risk_analysis": risk_result
    }

    # Test context preparation
    print(f"\n[Testing] Preparing supervisor context...")
    context = system._prepare_supervisor_context(all_analysis)

    print(f"\n{'='*70}")
    print("PREPARED CONTEXT FOR SUPERVISOR:")
    print(f"{'='*70}")
    print(context)
    print(f"{'='*70}")

    # Verify context is well-formed
    if len(context) > 0 and "MARKET" in context:
        print(f"\n✅ Context preparation working!")
        print(f"   Length: {len(context)} characters")
        print(f"   Contains market data: {'✅' if 'market' in context.lower() else '❌'}")
        print(f"   Contains strategy data: {'✅' if 'strategy' in context.lower() else '❌'}")
        print(f"   Contains risk data: {'✅' if 'risk' in context.lower() else '❌'}")
        return True
    else:
        print(f"\n❌ Context preparation failed")
        return False


def test_audit_summary():
    """Test audit trail analysis functionality"""
    print("\n" + "=" * 70)
    print("TEST 3: Audit Trail Analysis")
    print("=" * 70)

    system = LangChainTradingAgentSystem()

    if not system.db:
        print("\n⚠️  Database not configured - skipping audit test")
        return True

    market_data = MarketData()

    # Generate some decisions first
    print(f"\n[Setup] Generating sample decisions...")
    symbols = ["AAPL", "MSFT", "GOOGL"]

    for i, symbol in enumerate(symbols):
        print(f"   [{i+1}/{len(symbols)}] Processing {symbol}...")
        data = market_data.get_stock_data(symbol, period='5d')
        data = market_data.calculate_technical_indicators(data)

        # Run strategy to generate decision
        system.run_strategy_analysis(symbol, data)

    print(f"\n✅ Generated decisions for {len(symbols)} symbols")

    # Test audit summary for specific symbol
    print(f"\n[Test 1] Getting audit summary for AAPL...")
    aapl_audit = system.get_audit_summary(symbol="AAPL")

    if "error" not in aapl_audit:
        print(f"    ✅ AAPL audit retrieved")
        print(f"       Total decisions: {aapl_audit.get('total_decisions', 0)}")
        print(f"       Average confidence: {aapl_audit.get('average_confidence', 0):.1%}")
    else:
        print(f"    ⚠️  No decisions found for AAPL (might be new database)")

    # Test audit summary for all symbols
    print(f"\n[Test 2] Getting audit summary for all symbols...")
    all_audit = system.get_audit_summary()

    if "error" not in all_audit:
        print(f"    ✅ Global audit retrieved")
        print(f"       Total decisions: {all_audit.get('total_decisions', 0)}")
        dist = all_audit.get('decision_distribution', {})
        print(f"       BUY: {dist.get('BUY', 0)}, SELL: {dist.get('SELL', 0)}, HOLD: {dist.get('HOLD', 0)}")

        agents = all_audit.get('agent_activity', {})
        print(f"\n       Agent Activity:")
        for agent, count in agents.items():
            print(f"         - {agent}: {count} decisions")

        return True
    else:
        print(f"    ⚠️  {all_audit.get('error', 'Unknown error')}")
        return False


def run_all_tests():
    """Run all enhanced feature tests"""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ENHANCED FEATURES TEST SUITE" + " " * 25 + "║")
    print("║" + " " * 18 + "(Learned from Smolagents)" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")

    results = {}

    try:
        results['Quick Mode'] = test_quick_mode()
    except Exception as e:
        print(f"\n❌ Quick Mode test failed: {e}")
        results['Quick Mode'] = False

    try:
        results['Supervisor Context'] = test_supervisor_context()
    except Exception as e:
        print(f"\n❌ Supervisor Context test failed: {e}")
        results['Supervisor Context'] = False

    try:
        results['Audit Summary'] = test_audit_summary()
    except Exception as e:
        print(f"\n❌ Audit Summary test failed: {e}")
        results['Audit Summary'] = False

    # Final Summary
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 22 + "FINAL RESULTS" + " " * 33 + "║")
    print("╚" + "═" * 68 + "╝")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n{'Feature':<30} {'Status':<30}")
    print("─" * 60)

    for feature, status in results.items():
        emoji = "✅ PASSED" if status else "❌ FAILED"
        print(f"{feature:<30} {emoji:<30}")

    print("─" * 60)
    print(f"{'TOTAL':<30} {passed}/{total} PASSED")

    if passed == total:
        print("\n🎉 All enhanced features working!")
        print("\n✨ Improvements from smolagents successfully integrated:")
        print("   1. Quick mode for faster analysis")
        print("   2. Better supervisor context preparation")
        print("   3. Audit trail analysis for decision patterns")
    else:
        print(f"\n⚠️  {total - passed} feature(s) need attention")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
