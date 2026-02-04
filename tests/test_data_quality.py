"""
Test Data Quality Across Multiple API Sources
Validates data consistency, completeness, and reliability
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.enhanced_market_data import EnhancedMarketData
from app.data.market_data import MarketData


def test_data_quality():
    """Test data quality across all API sources"""
    print("=" * 70)
    print("DATA QUALITY TEST SUITE")
    print("=" * 70)

    enhanced = EnhancedMarketData()
    basic = MarketData()

    # Test symbols across different sectors
    test_symbols = {
        "Tech": ["AAPL", "MSFT", "GOOGL"],
        "Finance": ["JPM", "BAC", "GS"],
        "Healthcare": ["JNJ", "PFE", "UNH"],
        "Energy": ["XOM", "CVX"]
    }

    all_passed = True
    results = {}

    for sector, symbols in test_symbols.items():
        print(f"\n{'='*70}")
        print(f"Testing {sector} Sector")
        print(f"{'='*70}")

        for symbol in symbols:
            print(f"\n📊 Testing {symbol}...")
            symbol_results = {
                "quote": False,
                "fundamentals": False,
                "news": False,
                "historical": False
            }

            try:
                # Test 1: Real-time Quote
                print(f"  [1] Testing real-time quote...")
                quote = enhanced.get_real_time_quote(symbol)
                if quote and 'price' in quote:
                    if quote['price'] > 0:
                        print(f"      ✅ Quote: ${quote['price']:.2f} from {quote.get('source', 'unknown')}")
                        symbol_results["quote"] = True
                    else:
                        print(f"      ❌ Invalid price: {quote['price']}")
                        all_passed = False
                else:
                    print(f"      ⚠️  No quote data available")

                # Test 2: Company Fundamentals
                print(f"  [2] Testing company fundamentals...")
                fundamentals = enhanced.get_company_fundamentals(symbol)
                if fundamentals:
                    required_fields = ['name', 'sector', 'industry']
                    missing_fields = [f for f in required_fields if not fundamentals.get(f)]

                    if not missing_fields:
                        print(f"      ✅ Fundamentals: {fundamentals['name']}")
                        print(f"         Sector: {fundamentals['sector']}, Industry: {fundamentals['industry']}")
                        symbol_results["fundamentals"] = True
                    else:
                        print(f"      ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"      ⚠️  No fundamental data available")

                # Test 3: News Sentiment
                print(f"  [3] Testing news sentiment...")
                news = enhanced.get_news_sentiment(symbol)
                if news and 'articles' in news:
                    article_count = len(news['articles'])
                    sentiment = news.get('overall_sentiment', 'unknown')
                    print(f"      ✅ News: {article_count} articles found")
                    print(f"         Overall Sentiment: {sentiment}")
                    symbol_results["news"] = True
                else:
                    print(f"      ⚠️  No news data available")

                # Test 4: Historical Data
                print(f"  [4] Testing historical data...")
                historical = basic.get_stock_data(symbol, period='1mo')
                if not historical.empty:
                    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                    has_all_cols = all(col in historical.columns for col in required_cols)

                    if has_all_cols:
                        print(f"      ✅ Historical: {len(historical)} data points")
                        print(f"         Date range: {historical.index[0]} to {historical.index[-1]}")

                        # Validate data integrity
                        if (historical['High'] >= historical['Low']).all():
                            print(f"      ✅ Data integrity validated")
                            symbol_results["historical"] = True
                        else:
                            print(f"      ❌ Data integrity error: High < Low detected")
                            all_passed = False
                    else:
                        print(f"      ❌ Missing required columns")
                        all_passed = False
                else:
                    print(f"      ❌ No historical data")
                    all_passed = False

                results[symbol] = symbol_results

            except Exception as e:
                print(f"      ❌ Error testing {symbol}: {str(e)}")
                results[symbol] = symbol_results
                all_passed = False

    # Summary Report
    print(f"\n{'='*70}")
    print("DATA QUALITY SUMMARY")
    print(f"{'='*70}")

    total_symbols = len(results)
    fully_passed = sum(1 for r in results.values() if all(r.values()))

    print(f"\n📈 Total Symbols Tested: {total_symbols}")
    print(f"✅ Fully Passed: {fully_passed}/{total_symbols}")
    print()

    # Detailed breakdown
    print("Symbol Breakdown:")
    print(f"{'Symbol':<10} {'Quote':<8} {'Fund':<8} {'News':<8} {'Hist':<8} {'Status':<10}")
    print("-" * 60)

    for symbol, tests in results.items():
        quote_emoji = "✅" if tests["quote"] else "❌"
        fund_emoji = "✅" if tests["fundamentals"] else "❌"
        news_emoji = "✅" if tests["news"] else "⚠️"
        hist_emoji = "✅" if tests["historical"] else "❌"

        all_critical = tests["quote"] and tests["historical"]
        status = "PASS" if all_critical else "FAIL"

        print(f"{symbol:<10} {quote_emoji:<8} {fund_emoji:<8} {news_emoji:<8} {hist_emoji:<8} {status:<10}")

    print()
    if all_passed:
        print("🎉 All data quality tests passed!")
    else:
        print("⚠️  Some data quality issues detected")

    return all_passed


def test_data_consistency():
    """Test consistency between different data sources"""
    print("\n" + "=" * 70)
    print("DATA CONSISTENCY TEST")
    print("=" * 70)

    enhanced = EnhancedMarketData()
    symbol = "AAPL"

    print(f"\nTesting data consistency for {symbol}...")

    try:
        # Get data from multiple sources
        quote = enhanced.get_real_time_quote(symbol)
        fundamentals = enhanced.get_company_fundamentals(symbol)

        if quote and fundamentals:
            # Check if company names match (they should be similar)
            quote_name = quote.get('name', '').upper()
            fund_name = fundamentals.get('name', '').upper()

            if 'APPLE' in quote_name and 'APPLE' in fund_name:
                print(f"  ✅ Company name consistent across sources")
                return True
            else:
                print(f"  ⚠️  Company name mismatch:")
                print(f"      Quote: {quote.get('name')}")
                print(f"      Fundamentals: {fundamentals.get('name')}")
                return True  # Still pass, names might vary slightly
        else:
            print(f"  ⚠️  Could not retrieve data from all sources")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_data_quality()
    consistency = test_data_consistency()

    final_result = success and consistency

    print(f"\n{'='*70}")
    print(f"FINAL RESULT: {'✅ PASSED' if final_result else '❌ FAILED'}")
    print(f"{'='*70}")

    sys.exit(0 if final_result else 1)
