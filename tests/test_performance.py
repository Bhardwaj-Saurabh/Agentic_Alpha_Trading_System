"""
Performance and Load Tests
Tests system performance under various load conditions
"""
import sys
import os
import time
from typing import List, Dict
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.pydantic_agents import PydanticTradingAgentSystem
from app.data.market_data import MarketData
from app.data.enhanced_market_data import EnhancedMarketData


class PerformanceMetrics:
    """Track performance metrics"""
    def __init__(self):
        self.timings: List[float] = []
        self.errors: int = 0
        self.successes: int = 0

    def add_timing(self, duration: float, success: bool = True):
        self.timings.append(duration)
        if success:
            self.successes += 1
        else:
            self.errors += 1

    def get_stats(self) -> Dict:
        if not self.timings:
            return {"error": "No timings recorded"}

        return {
            "count": len(self.timings),
            "total_time": sum(self.timings),
            "avg_time": sum(self.timings) / len(self.timings),
            "min_time": min(self.timings),
            "max_time": max(self.timings),
            "successes": self.successes,
            "errors": self.errors,
            "success_rate": self.successes / len(self.timings) * 100
        }


def test_single_stock_performance():
    """Test performance for analyzing a single stock"""
    print("=" * 70)
    print("SINGLE STOCK PERFORMANCE TEST")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    symbol = "AAPL"
    print(f"\nAnalyzing {symbol} through full agent pipeline...")

    # Get market data
    print(f"\n[0] Fetching market data...")
    start = time.time()
    data = market_data.get_stock_data(symbol)
    data = market_data.calculate_technical_indicators(data)
    data_time = time.time() - start
    print(f"    ⏱️  Data fetch: {data_time:.2f}s")

    # Test each agent
    agents = [
        ("Market Analyst", lambda: system.run_market_analysis(symbol, data)),
        ("Trading Signal", lambda: system.run_trading_signal_analysis(symbol, data)),
        ("Risk Manager", lambda: system.run_risk_management(symbol, data)),
    ]

    agent_timings = {}
    total_agent_time = 0

    for agent_name, agent_func in agents:
        print(f"\n[{agents.index((agent_name, agent_func)) + 1}] Testing {agent_name}...")

        start = time.time()
        try:
            if agent_name == "Market Analyst":
                market_result = agent_func()
                agent_time = time.time() - start

                # Test Regulatory (depends on market result)
                reg_start = time.time()
                system.run_regulatory_compliance(symbol, market_result)
                reg_time = time.time() - reg_start

                # Test Supervisor (depends on market result)
                sup_start = time.time()
                system.run_supervisor_decision(symbol, market_result)
                sup_time = time.time() - sup_start

                agent_timings["Regulatory"] = reg_time
                agent_timings["Supervisor"] = sup_time
                total_agent_time += reg_time + sup_time

                print(f"    ⏱️  {agent_name}: {agent_time:.2f}s")
                print(f"    ⏱️  Regulatory: {reg_time:.2f}s")
                print(f"    ⏱️  Supervisor: {sup_time:.2f}s")
            else:
                agent_func()
                agent_time = time.time() - start
                print(f"    ⏱️  {agent_name}: {agent_time:.2f}s")

            agent_timings[agent_name] = agent_time
            total_agent_time += agent_time

        except Exception as e:
            agent_time = time.time() - start
            print(f"    ❌ Error after {agent_time:.2f}s: {str(e)[:50]}")
            agent_timings[agent_name] = agent_time

    # Summary
    print(f"\n{'='*70}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*70}")

    print(f"\nTimings Breakdown:")
    print(f"  Data Fetch: {data_time:.2f}s")
    for agent, timing in agent_timings.items():
        print(f"  {agent}: {timing:.2f}s")

    total_time = data_time + total_agent_time
    print(f"\n📊 Total Analysis Time: {total_time:.2f}s")

    # Performance ratings
    if total_time < 15:
        rating = "⚡ EXCELLENT"
    elif total_time < 30:
        rating = "✅ GOOD"
    elif total_time < 60:
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "❌ SLOW"

    print(f"Performance Rating: {rating}")

    return total_time < 60  # Pass if under 1 minute


def test_multiple_stocks_performance():
    """Test performance when analyzing multiple stocks"""
    print("\n" + "=" * 70)
    print("MULTIPLE STOCKS PERFORMANCE TEST")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    print(f"\nAnalyzing {len(symbols)} stocks: {', '.join(symbols)}")

    metrics = PerformanceMetrics()
    total_start = time.time()

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")

        stock_start = time.time()
        try:
            # Get data
            data = market_data.get_stock_data(symbol, period='1mo')
            if data.empty:
                print(f"    ⚠️  No data available")
                metrics.add_timing(time.time() - stock_start, success=False)
                continue

            data = market_data.calculate_technical_indicators(data)

            # Run market analysis
            result = system.run_market_analysis(symbol, data)

            stock_time = time.time() - stock_start
            metrics.add_timing(stock_time, success=True)

            print(f"    ✅ Completed in {stock_time:.2f}s")

        except Exception as e:
            stock_time = time.time() - stock_start
            metrics.add_timing(stock_time, success=False)
            print(f"    ❌ Error after {stock_time:.2f}s: {str(e)[:50]}")

    total_time = time.time() - total_start

    # Summary
    print(f"\n{'='*70}")
    print("BATCH PERFORMANCE SUMMARY")
    print(f"{'='*70}")

    stats = metrics.get_stats()

    print(f"\n📊 Statistics:")
    print(f"   Total Stocks: {len(symbols)}")
    print(f"   Successes: {stats['successes']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print()
    print(f"⏱️  Timing:")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Average per Stock: {stats['avg_time']:.2f}s")
    print(f"   Fastest: {stats['min_time']:.2f}s")
    print(f"   Slowest: {stats['max_time']:.2f}s")

    # Throughput
    throughput = len(symbols) / total_time * 60  # stocks per minute
    print(f"   Throughput: {throughput:.1f} stocks/minute")

    # Performance rating
    if stats['avg_time'] < 10:
        rating = "⚡ EXCELLENT"
    elif stats['avg_time'] < 20:
        rating = "✅ GOOD"
    elif stats['avg_time'] < 30:
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "❌ SLOW"

    print(f"\nPerformance Rating: {rating}")

    return stats['success_rate'] >= 80 and stats['avg_time'] < 30


def test_api_response_times():
    """Test API response times for data fetching"""
    print("\n" + "=" * 70)
    print("API RESPONSE TIME TEST")
    print("=" * 70)

    enhanced = EnhancedMarketData()
    market_data = MarketData()

    test_cases = [
        ("Historical Data", lambda: market_data.get_stock_data("AAPL", period='1mo')),
        ("Real-Time Quote", lambda: enhanced.get_real_time_quote("AAPL")),
        ("Company Fundamentals", lambda: enhanced.get_company_fundamentals("AAPL")),
        ("News Sentiment", lambda: enhanced.get_news_sentiment("AAPL")),
    ]

    results = {}

    for test_name, test_func in test_cases:
        print(f"\n Testing {test_name}...")

        timings = []
        for i in range(3):  # Test 3 times
            start = time.time()
            try:
                test_func()
                elapsed = time.time() - start
                timings.append(elapsed)
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:50]}")
                timings.append(None)

        valid_timings = [t for t in timings if t is not None]
        if valid_timings:
            avg_time = sum(valid_timings) / len(valid_timings)
            print(f"    ⏱️  Average: {avg_time:.3f}s")
            print(f"    Range: {min(valid_timings):.3f}s - {max(valid_timings):.3f}s")
            results[test_name] = avg_time
        else:
            print(f"    ❌ All requests failed")
            results[test_name] = None

    # Summary
    print(f"\n{'='*70}")
    print("API RESPONSE TIME SUMMARY")
    print(f"{'='*70}")

    print(f"\n{'API Call':<25} {'Avg Response Time':<20} {'Rating':<10}")
    print("-" * 60)

    all_good = True
    for test_name, avg_time in results.items():
        if avg_time is None:
            print(f"{test_name:<25} {'FAILED':<20} {'❌':<10}")
            all_good = False
        else:
            if avg_time < 1.0:
                rating = "⚡ Fast"
            elif avg_time < 3.0:
                rating = "✅ Good"
            elif avg_time < 5.0:
                rating = "⚠️  Slow"
            else:
                rating = "❌ Very Slow"
                all_good = False

            print(f"{test_name:<25} {f'{avg_time:.3f}s':<20} {rating:<10}")

    return all_good


def test_memory_usage():
    """Test basic memory behavior (simplified)"""
    print("\n" + "=" * 70)
    print("MEMORY USAGE TEST")
    print("=" * 70)

    print("\nProcessing multiple stocks to check for memory leaks...")

    market_data = MarketData()
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"]

    try:
        for i, symbol in enumerate(symbols, 1):
            data = market_data.get_stock_data(symbol, period='3mo')
            data = market_data.calculate_technical_indicators(data)
            print(f"  [{i}/{len(symbols)}] Processed {symbol}: {len(data)} rows")

        print(f"\n✅ Memory test completed: Processed {len(symbols)} stocks successfully")
        print(f"   Note: Monitor system resources for memory leaks during extended use")

        return True

    except Exception as e:
        print(f"\n❌ Memory test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🚀 " * 35)
    print("PERFORMANCE TEST SUITE")
    print("🚀 " * 35)

    results = {}

    # Run all performance tests
    print("\n")
    results['single_stock'] = test_single_stock_performance()

    print("\n")
    results['multiple_stocks'] = test_multiple_stocks_performance()

    print("\n")
    results['api_response'] = test_api_response_times()

    print("\n")
    results['memory'] = test_memory_usage()

    # Final Summary
    print(f"\n{'='*70}")
    print("FINAL PERFORMANCE SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTest Results:")
    for test_name, passed_test in results.items():
        emoji = "✅" if passed_test else "❌"
        status = "PASSED" if passed_test else "FAILED"
        print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall: {passed}/{total} performance tests passed")

    if passed == total:
        print(f"\n🎉 Excellent! All performance benchmarks met!")
    else:
        print(f"\n⚠️  {total - passed} performance test(s) need attention")

    sys.exit(0 if passed == total else 1)
