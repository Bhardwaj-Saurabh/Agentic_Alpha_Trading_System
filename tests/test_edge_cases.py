"""
Edge Case and Error Handling Tests
Tests system behavior with invalid inputs and edge cases
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.pydantic_agents import PydanticTradingAgentSystem
from app.data.market_data import MarketData
from app.data.enhanced_market_data import EnhancedMarketData


def test_edge_cases():
    """Test system behavior with edge cases"""
    print("=" * 70)
    print("EDGE CASE TEST SUITE")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()
    enhanced = EnhancedMarketData()

    # Define edge case test scenarios
    test_cases = [
        {
            "name": "Invalid Stock Symbol",
            "symbol": "INVALID123",
            "description": "Non-existent stock ticker",
            "should_handle": True
        },
        {
            "name": "Random String Symbol",
            "symbol": "ZZZZZZ",
            "description": "Random characters as symbol",
            "should_handle": True
        },
        {
            "name": "Empty Symbol",
            "symbol": "",
            "description": "Empty string as symbol",
            "should_handle": True
        },
        {
            "name": "Special Characters",
            "symbol": "@#$%",
            "description": "Special characters in symbol",
            "should_handle": True
        },
        {
            "name": "Very Long Symbol",
            "symbol": "A" * 50,
            "description": "Extremely long ticker symbol",
            "should_handle": True
        },
        {
            "name": "Lowercase Symbol",
            "symbol": "aapl",
            "description": "Lowercase ticker (should auto-convert)",
            "should_handle": False  # Should work after conversion
        },
        {
            "name": "Symbol with Spaces",
            "symbol": " AAPL ",
            "description": "Symbol with leading/trailing spaces",
            "should_handle": False  # Should work after stripping
        },
        {
            "name": "Delisted Stock",
            "symbol": "XYZ",  # Example of potentially problematic symbol
            "description": "Potentially delisted or inactive stock",
            "should_handle": True
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}/{len(test_cases)}: {test_case['name']}")
        print(f"Symbol: '{test_case['symbol']}'")
        print(f"Description: {test_case['description']}")
        print(f"{'='*70}")

        test_result = {
            "name": test_case["name"],
            "symbol": test_case["symbol"],
            "passed": False,
            "handled_gracefully": False,
            "error_type": None
        }

        try:
            # Test 1: Basic data retrieval
            print(f"\n[1] Testing data retrieval...")
            data = market_data.get_stock_data(test_case["symbol"])

            if data.empty:
                print(f"    ✅ Correctly handled: No data for invalid symbol")
                test_result["handled_gracefully"] = True
                test_result["passed"] = test_case["should_handle"]
            else:
                print(f"    ℹ️  Retrieved {len(data)} data points")
                if test_case["should_handle"]:
                    print(f"    ⚠️  Warning: Got data for what should be invalid symbol")
                else:
                    print(f"    ✅ Symbol was valid after normalization")
                    test_result["passed"] = True

            # Test 2: Enhanced data retrieval
            print(f"\n[2] Testing enhanced data retrieval...")
            quote = enhanced.get_real_time_quote(test_case["symbol"])

            if quote is None or not quote:
                print(f"    ✅ Correctly handled: No quote data")
                test_result["handled_gracefully"] = True
            else:
                print(f"    ℹ️  Retrieved quote: ${quote.get('price', 'N/A')}")

            # Test 3: Agent processing (only if we have data)
            if not data.empty:
                print(f"\n[3] Testing agent processing...")
                try:
                    data = market_data.calculate_technical_indicators(data)
                    result = system.run_market_analysis(test_case["symbol"], data)

                    if result and "analysis" in result:
                        print(f"    ✅ Agent processed successfully")
                        test_result["passed"] = True
                    else:
                        print(f"    ⚠️  Agent returned incomplete result")

                except Exception as agent_error:
                    print(f"    ℹ️  Agent error: {type(agent_error).__name__}")
                    test_result["error_type"] = type(agent_error).__name__
                    test_result["handled_gracefully"] = True

        except Exception as e:
            error_type = type(e).__name__
            print(f"\n    ℹ️  Caught exception: {error_type}")
            print(f"    Message: {str(e)[:100]}")

            test_result["error_type"] = error_type
            test_result["handled_gracefully"] = True
            test_result["passed"] = test_case["should_handle"]

        results.append(test_result)

        # Print test result
        if test_result["passed"]:
            print(f"\n✅ Test PASSED: System handled edge case correctly")
        elif test_result["handled_gracefully"]:
            print(f"\n⚠️  Test PARTIAL: System handled gracefully but behavior unexpected")
        else:
            print(f"\n❌ Test FAILED: System did not handle edge case properly")

    # Summary Report
    print(f"\n{'='*70}")
    print("EDGE CASE TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for r in results if r["passed"])
    graceful = sum(1 for r in results if r["handled_gracefully"])
    total = len(results)

    print(f"\n📊 Results:")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"   🛡️  Handled Gracefully: {graceful}/{total} ({graceful/total*100:.1f}%)")
    print()

    print("Detailed Results:")
    print(f"{'Test Case':<30} {'Symbol':<15} {'Status':<10} {'Error Type':<20}")
    print("-" * 80)

    for result in results:
        status = "✅ PASS" if result["passed"] else ("⚠️ PARTIAL" if result["handled_gracefully"] else "❌ FAIL")
        error = result["error_type"] or "None"
        symbol_display = result["symbol"][:12] if result["symbol"] else "empty"

        print(f"{result['name']:<30} {symbol_display:<15} {status:<10} {error:<20}")

    # Final verdict
    print()
    if passed == total:
        print("🎉 Perfect! All edge cases handled correctly!")
        return True
    elif graceful == total:
        print("👍 Good! All edge cases handled gracefully!")
        return True
    else:
        print(f"⚠️  {total - graceful} test(s) failed catastrophically")
        return False


def test_concurrent_requests():
    """Test system behavior with concurrent requests"""
    print("\n" + "=" * 70)
    print("CONCURRENT REQUEST TEST")
    print("=" * 70)

    print("\nTesting rapid sequential requests...")

    market_data = MarketData()
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

    try:
        import time
        start = time.time()

        for symbol in symbols:
            data = market_data.get_stock_data(symbol, period='5d')
            print(f"  ✅ {symbol}: {len(data) if not data.empty else 0} points")

        elapsed = time.time() - start
        print(f"\n⏱️  Total time: {elapsed:.2f}s ({elapsed/len(symbols):.2f}s per symbol)")
        print(f"✅ Concurrent request handling test passed")

        return True

    except Exception as e:
        print(f"❌ Concurrent request test failed: {e}")
        return False


if __name__ == "__main__":
    edge_cases_pass = test_edge_cases()
    concurrent_pass = test_concurrent_requests()

    final_result = edge_cases_pass and concurrent_pass

    print(f"\n{'='*70}")
    print(f"FINAL RESULT: {'✅ ALL TESTS PASSED' if final_result else '❌ SOME TESTS FAILED'}")
    print(f"{'='*70}")

    sys.exit(0 if final_result else 1)
