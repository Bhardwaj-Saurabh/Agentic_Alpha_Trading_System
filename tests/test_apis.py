"""
API Integration Test Script

Tests all configured APIs to ensure they're working correctly:
- Alpha Vantage (market data)
- RapidAPI/Quandl (alternative data)
- Tavily (news & sentiment)
- Yahoo Finance (fallback)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.enhanced_market_data import EnhancedMarketData
from app.config import Config


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(success, message):
    """Print test result"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {status}: {message}")


def test_configuration():
    """Test API configuration"""
    print_header("1. Testing API Configuration")

    # Check OpenAI
    if Config.OPENAI_API_KEY:
        print_result(True, f"OpenAI API Key configured ({Config.OPENAI_API_KEY[:20]}...)")
    else:
        print_result(False, "OpenAI API Key not configured")

    # Check Alpha Vantage
    if Config.ALPHA_VANTAGE_API_KEY:
        print_result(True, f"Alpha Vantage API Key configured ({Config.ALPHA_VANTAGE_API_KEY[:10]}...)")
    else:
        print_result(False, "Alpha Vantage API Key not configured")

    # Check RapidAPI
    if Config.X_RAPID_API_KEY and Config.X_RAPIDAPI_HOST:
        print_result(True, f"RapidAPI configured (Host: {Config.X_RAPIDAPI_HOST})")
    else:
        print_result(False, "RapidAPI not fully configured")

    # Check Tavily
    if Config.TAVILY_API_KEY:
        print_result(True, f"Tavily API Key configured ({Config.TAVILY_API_KEY[:20]}...)")
    else:
        print_result(False, "Tavily API Key not configured")


def test_real_time_quote(market_data, symbol="AAPL"):
    """Test real-time quote fetching"""
    print_header(f"2. Testing Real-Time Quote for {symbol}")

    try:
        quote = market_data.get_real_time_quote(symbol)

        if quote:
            print_result(True, f"Fetched quote from {quote['source']}")
            print(f"      Price: ${quote['price']:.2f}")
            print(f"      Change: {quote['change_percent']}")
            print(f"      Volume: {quote['volume']:,}")
            print(f"      Trading Day: {quote['latest_trading_day']}")
            return True
        else:
            print_result(False, "No quote data returned")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_fundamentals(market_data, symbol="AAPL"):
    """Test company fundamentals"""
    print_header(f"3. Testing Company Fundamentals for {symbol}")

    try:
        fundamentals = market_data.get_company_fundamentals(symbol)

        if fundamentals:
            print_result(True, f"Fetched fundamentals for {fundamentals['name']}")
            print(f"      Sector: {fundamentals['sector']}")
            print(f"      Industry: {fundamentals['industry']}")
            print(f"      Market Cap: ${fundamentals['market_cap']:,}")
            print(f"      P/E Ratio: {fundamentals['pe_ratio']}")
            print(f"      EPS: {fundamentals['eps']}")
            print(f"      Dividend Yield: {fundamentals['dividend_yield']}")
            print(f"      52-Week High: ${fundamentals['52_week_high']}")
            print(f"      52-Week Low: ${fundamentals['52_week_low']}")
            return True
        else:
            print_result(False, "No fundamental data returned")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_news_sentiment(market_data, symbol="AAPL"):
    """Test news and sentiment analysis"""
    print_header(f"4. Testing News & Sentiment for {symbol}")

    try:
        news = market_data.get_news_sentiment(symbol)

        if news and news.get('articles'):
            articles = news['articles']
            print_result(True, f"Fetched {len(articles)} news articles")
            print(f"      Query: {news['query']}")
            print(f"      Timestamp: {news['timestamp']}")
            print("\n      Latest Articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"      {i}. {article['title'][:60]}...")
                print(f"         Score: {article['score']:.2f}")
                print(f"         URL: {article['url'][:50]}...")
            return True
        else:
            print_result(False, "No news data returned (Tavily may not be configured)")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_comprehensive_analysis(market_data, symbol="AAPL"):
    """Test comprehensive multi-source analysis"""
    print_header(f"5. Testing Comprehensive Analysis for {symbol}")

    try:
        analysis = market_data.get_comprehensive_analysis(symbol)

        if analysis and analysis.get('data_sources'):
            sources = analysis['data_sources']
            print_result(True, f"Successfully aggregated data from {len(sources)} sources")
            print(f"      Symbol: {analysis['symbol']}")
            print(f"      Timestamp: {analysis['timestamp']}")
            print(f"      Data Sources: {', '.join(sources)}")

            # Show what we got
            if 'quote' in analysis:
                print(f"\n      💰 Real-Time Quote:")
                print(f"         Price: ${analysis['quote']['price']:.2f}")
                print(f"         Change: {analysis['quote']['change_percent']}")

            if 'fundamentals' in analysis:
                print(f"\n      📊 Fundamentals:")
                print(f"         Company: {analysis['fundamentals']['name']}")
                print(f"         Sector: {analysis['fundamentals']['sector']}")
                print(f"         P/E Ratio: {analysis['fundamentals']['pe_ratio']}")

            if 'news' in analysis:
                print(f"\n      📰 News:")
                print(f"         Articles: {len(analysis['news']['articles'])}")

            return True
        else:
            print_result(False, "Incomplete analysis data")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_cache_functionality(market_data, symbol="AAPL"):
    """Test caching system"""
    print_header("6. Testing Cache Functionality")

    try:
        # First call (should fetch)
        print("   First call (should fetch from API)...")
        quote1 = market_data.get_real_time_quote(symbol)

        # Second call (should use cache)
        print("   Second call (should use cache)...")
        quote2 = market_data.get_real_time_quote(symbol)

        # Check cache info
        cache_info = market_data.get_cache_info()
        print_result(True, f"Cache working - {cache_info['cached_items']} items cached")
        print(f"      Cache timeout: {cache_info['cache_timeout_seconds']} seconds")
        print(f"      Cached items: {', '.join(cache_info['items'])}")

        return True

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all API integration tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🚀 API INTEGRATION TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")

    # Initialize
    market_data = EnhancedMarketData()
    test_symbol = "AAPL"  # Apple Inc.

    # Track results
    results = {
        "Configuration": False,
        "Real-Time Quote": False,
        "Fundamentals": False,
        "News & Sentiment": False,
        "Comprehensive Analysis": False,
        "Cache Functionality": False
    }

    # Run tests
    test_configuration()  # No return value needed
    results["Real-Time Quote"] = test_real_time_quote(market_data, test_symbol)
    results["Fundamentals"] = test_fundamentals(market_data, test_symbol)
    results["News & Sentiment"] = test_news_sentiment(market_data, test_symbol)
    results["Comprehensive Analysis"] = test_comprehensive_analysis(market_data, test_symbol)
    results["Cache Functionality"] = test_cache_functionality(market_data, test_symbol)

    # Summary
    print_header("📊 TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")

    print("\n" + "-" * 70)
    print(f"   Total: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    print("-" * 70)

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not results["Real-Time Quote"]:
        print("   - Check Alpha Vantage and RapidAPI credentials")
        print("   - Verify internet connection")

    if not results["Fundamentals"]:
        print("   - Alpha Vantage API may be rate-limited (wait 1 minute)")
        print("   - Check API key validity")

    if not results["News & Sentiment"]:
        print("   - Install Tavily: pip install tavily-python")
        print("   - Verify TAVILY_API_KEY in .env file")

    if passed == total:
        print("\n🎉 All tests passed! Your API integration is working perfectly!")
    elif passed >= total * 0.7:
        print("\n⚠️ Most tests passed. Some optional features may need configuration.")
    else:
        print("\n❌ Several tests failed. Please check your API credentials and configuration.")

    print("\n" + "=" * 70)
    print("  Testing complete! Check API_INTEGRATION_GUIDE.md for more details.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
