"""
Agent Consistency Tests
Tests if agents give consistent results for the same input
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.pydantic_agents import PydanticTradingAgentSystem
from app.data.market_data import MarketData
from collections import Counter


def test_agent_consistency(runs: int = 3):
    """Test if agents give consistent results for the same input"""
    print("=" * 70)
    print("AGENT CONSISTENCY TEST SUITE")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    # Test with a stable symbol
    symbol = "AAPL"

    print(f"\nTesting consistency for {symbol} across {runs} runs...")
    print(f"Note: Some variation is expected due to AI non-determinism")

    # Get market data once (same data for all runs)
    print(f"\n[0] Fetching market data...")
    data = market_data.get_stock_data(symbol, period='1mo')
    if data.empty:
        print(f"❌ No data available for {symbol}")
        return False

    data = market_data.calculate_technical_indicators(data)
    print(f"    ✅ Retrieved {len(data)} data points")

    # Test each agent multiple times
    agents_to_test = [
        ("Market Analyst", lambda: system.run_market_analysis(symbol, data)),
        ("Trading Signal", lambda: system.run_trading_signal_analysis(symbol, data)),
        ("Risk Manager", lambda: system.run_risk_management(symbol, data)),
    ]

    all_consistent = True
    consistency_results = {}

    for agent_name, agent_func in agents_to_test:
        print(f"\n{'='*70}")
        print(f"Testing {agent_name} Agent")
        print(f"{'='*70}")

        results = []
        decisions = []
        confidences = []

        for i in range(runs):
            print(f"\nRun {i+1}/{runs}...")

            try:
                result = agent_func()

                if agent_name == "Trading Signal":
                    if "analysis" in result and hasattr(result["analysis"], 'decision'):
                        analysis = result["analysis"]
                        decision = str(analysis.decision)
                        confidence = analysis.confidence
                        risk = str(analysis.risk_level)

                        decisions.append(decision)
                        confidences.append(confidence)

                        print(f"  Decision: {decision}")
                        print(f"  Risk Level: {risk}")
                        print(f"  Confidence: {confidence:.2%}")

                        results.append({
                            "decision": decision,
                            "risk": risk,
                            "confidence": confidence
                        })

                elif agent_name == "Market Analyst":
                    if "analysis" in result:
                        # Just verify it completes
                        print(f"  ✅ Analysis completed")
                        results.append({"status": "success"})

                elif agent_name == "Risk Manager":
                    if "analysis" in result:
                        print(f"  ✅ Risk assessment completed")
                        results.append({"status": "success"})

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                results.append({"error": str(e)})

        # Analyze consistency
        print(f"\n{'─'*70}")
        print(f"Consistency Analysis for {agent_name}")
        print(f"{'─'*70}")

        success_count = sum(1 for r in results if "error" not in r)
        print(f"\nSuccess Rate: {success_count}/{runs} ({success_count/runs*100:.1f}%)")

        if agent_name == "Trading Signal" and decisions:
            # Check decision consistency
            decision_counts = Counter(decisions)
            most_common = decision_counts.most_common(1)[0]
            consistency_pct = (most_common[1] / len(decisions)) * 100

            print(f"\nDecision Consistency:")
            print(f"  Most Common Decision: {most_common[0]} ({most_common[1]}/{len(decisions)} times, {consistency_pct:.1f}%)")

            if len(decision_counts) == 1:
                print(f"  ✅ Perfect Consistency: All runs produced '{most_common[0]}'")
                is_consistent = True
            elif consistency_pct >= 66:
                print(f"  ✅ High Consistency: {consistency_pct:.1f}% agreement")
                is_consistent = True
            else:
                print(f"  ⚠️  Low Consistency: Only {consistency_pct:.1f}% agreement")
                print(f"  All decisions: {decisions}")
                is_consistent = False
                all_consistent = False

            # Check confidence stability
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                conf_range = max(confidences) - min(confidences)

                print(f"\nConfidence Stability:")
                print(f"  Average: {avg_conf:.2%}")
                print(f"  Range: {min(confidences):.2%} to {max(confidences):.2%} (spread: {conf_range:.2%})")

                if conf_range < 0.15:
                    print(f"  ✅ Stable: Confidence range < 15%")
                elif conf_range < 0.30:
                    print(f"  ⚠️  Moderate: Confidence range < 30%")
                else:
                    print(f"  ❌ Unstable: Confidence range > 30%")

        else:
            # For other agents, just check success rate
            if success_count == runs:
                print(f"  ✅ Consistent: All runs successful")
                is_consistent = True
            else:
                print(f"  ⚠️  Inconsistent: {runs - success_count} failures")
                is_consistent = False
                all_consistent = False

        consistency_results[agent_name] = is_consistent

    # Final Summary
    print(f"\n{'='*70}")
    print("CONSISTENCY TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for v in consistency_results.values() if v)
    total = len(consistency_results)

    print(f"\nAgent Consistency Results:")
    for agent, consistent in consistency_results.items():
        emoji = "✅" if consistent else "⚠️"
        status = "CONSISTENT" if consistent else "INCONSISTENT"
        print(f"  {emoji} {agent}: {status}")

    print(f"\nOverall: {passed}/{total} agents showed consistent behavior")

    if all_consistent:
        print(f"\n🎉 Success! All agents demonstrated consistent behavior!")
    else:
        print(f"\n⚠️  Note: Some variation is normal for AI agents. Review results above.")

    return all_consistent


def test_determinism_with_caching():
    """Test if caching improves consistency"""
    print("\n" + "=" * 70)
    print("CACHING CONSISTENCY TEST")
    print("=" * 70)

    market_data = MarketData()
    symbol = "AAPL"

    print(f"\nTesting cache consistency for {symbol}...")

    # First call
    print(f"[1] First data fetch (should hit API)...")
    data1 = market_data.get_stock_data(symbol, period='5d')

    # Second call (should hit cache)
    print(f"[2] Second data fetch (should hit cache)...")
    data2 = market_data.get_stock_data(symbol, period='5d')

    # Compare
    if data1.equals(data2):
        print(f"    ✅ Data is identical: Cache working correctly")
        return True
    else:
        print(f"    ⚠️  Data differs: Cache may not be working")
        print(f"    Data1 shape: {data1.shape}, Data2 shape: {data2.shape}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test agent consistency")
    parser.add_argument("--runs", type=int, default=3, help="Number of test runs (default: 3)")

    args = parser.parse_args()

    consistency_pass = test_agent_consistency(runs=args.runs)
    cache_pass = test_determinism_with_caching()

    final_result = consistency_pass and cache_pass

    print(f"\n{'='*70}")
    print(f"FINAL RESULT: {'✅ TESTS PASSED' if final_result else '⚠️  SEE RESULTS ABOVE'}")
    print(f"{'='*70}")

    sys.exit(0 if final_result else 1)
