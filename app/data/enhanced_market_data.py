"""
Enhanced Market Data Integration - Uses Multiple APIs for Live Data

This module integrates multiple data sources for comprehensive market analysis:
- Yahoo Finance (Free, primary source)
- Alpha Vantage (Additional market data and fundamentals)
- X-RapidAPI/Quandl (Alternative financial data)
- Tavily (News and sentiment analysis)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config


class EnhancedMarketData:
    """Enhanced market data fetcher using multiple APIs"""

    def __init__(self):
        self.cache = {}
        self.cache_timeout = 1800  # 30 minutes for live data
        self.alpha_vantage_key = Config.ALPHA_VANTAGE_API_KEY
        self.rapid_api_key = Config.X_RAPID_API_KEY
        self.rapid_api_host = Config.X_RAPIDAPI_HOST
        self.tavily_key = Config.TAVILY_API_KEY

    def get_alpha_vantage_data(self, symbol: str, function: str = "TIME_SERIES_DAILY"):
        """
        Fetch data from Alpha Vantage API

        Args:
            symbol: Stock symbol
            function: Alpha Vantage function (TIME_SERIES_DAILY, GLOBAL_QUOTE, etc.)

        Returns:
            dict: Raw API response
        """
        if not self.alpha_vantage_key:
            print("⚠️ Alpha Vantage API key not configured")
            return None

        try:
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
                "outputsize": "compact"
            }

            print(f"📡 Fetching {symbol} from Alpha Vantage...")
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                print(f"❌ Alpha Vantage error: {data['Error Message']}")
                return None
            if "Note" in data:
                print(f"⚠️ Alpha Vantage rate limit: {data['Note']}")
                return None

            print(f"✅ Successfully fetched data from Alpha Vantage for {symbol}")
            return data

        except requests.exceptions.Timeout:
            print(f"⏱️ Alpha Vantage request timed out for {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Alpha Vantage request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error fetching Alpha Vantage data: {str(e)}")
            return None

    def get_rapid_api_quote(self, symbol: str):
        """
        Fetch real-time quote from RapidAPI/Quandl

        Args:
            symbol: Stock symbol

        Returns:
            dict: Quote data
        """
        if not self.rapid_api_key or not self.rapid_api_host:
            print("⚠️ RapidAPI credentials not configured")
            return None

        try:
            url = f"https://{self.rapid_api_host}/api/v3/stock/{symbol}/quote"

            headers = {
                "X-RapidAPI-Key": self.rapid_api_key,
                "X-RapidAPI-Host": self.rapid_api_host
            }

            print(f"📡 Fetching {symbol} from RapidAPI...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            print(f"✅ Successfully fetched data from RapidAPI for {symbol}")
            return data

        except requests.exceptions.Timeout:
            print(f"⏱️ RapidAPI request timed out for {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ RapidAPI request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error fetching RapidAPI data: {str(e)}")
            return None

    def get_company_fundamentals(self, symbol: str):
        """
        Get company fundamentals from Alpha Vantage

        Args:
            symbol: Stock symbol

        Returns:
            dict: Company fundamental data
        """
        if not self.alpha_vantage_key:
            return None

        try:
            # Get company overview
            overview_data = self.get_alpha_vantage_data(symbol, "OVERVIEW")

            if overview_data and overview_data != {}:
                fundamentals = {
                    "symbol": symbol,
                    "name": overview_data.get("Name", symbol),
                    "sector": overview_data.get("Sector", "Unknown"),
                    "industry": overview_data.get("Industry", "Unknown"),
                    "market_cap": overview_data.get("MarketCapitalization", 0),
                    "pe_ratio": overview_data.get("PERatio", "N/A"),
                    "eps": overview_data.get("EPS", "N/A"),
                    "dividend_yield": overview_data.get("DividendYield", "N/A"),
                    "52_week_high": overview_data.get("52WeekHigh", "N/A"),
                    "52_week_low": overview_data.get("52WeekLow", "N/A"),
                    "beta": overview_data.get("Beta", "N/A"),
                    "description": overview_data.get("Description", "N/A")[:300] + "..."
                }
                return fundamentals

        except Exception as e:
            print(f"❌ Error fetching fundamentals: {str(e)}")

        return None

    def get_news_sentiment(self, symbol: str, query: str = None):
        """
        Get news and sentiment using Tavily API

        Args:
            symbol: Stock symbol
            query: Custom search query (optional)

        Returns:
            dict: News articles and sentiment
        """
        if not self.tavily_key:
            print("⚠️ Tavily API key not configured")
            return None

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self.tavily_key)

            # Create search query
            search_query = query if query else f"{symbol} stock news latest market"

            print(f"📰 Fetching news for {symbol} from Tavily...")
            response = client.search(
                query=search_query,
                search_depth="basic",
                max_results=5
            )

            if response and "results" in response:
                articles = []
                for result in response["results"]:
                    articles.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", "")[:200] + "...",
                        "score": result.get("score", 0)
                    })

                print(f"✅ Found {len(articles)} news articles for {symbol}")
                return {
                    "symbol": symbol,
                    "articles": articles,
                    "query": search_query,
                    "timestamp": datetime.now().isoformat()
                }

        except ImportError:
            print("⚠️ Tavily package not installed. Run: pip install tavily-python")
            return None
        except Exception as e:
            print(f"❌ Error fetching news: {str(e)}")
            return None

        return None

    def get_real_time_quote(self, symbol: str):
        """
        Get real-time quote from multiple sources with fallback

        Args:
            symbol: Stock symbol

        Returns:
            dict: Real-time quote data
        """
        cache_key = f"quote_{symbol}"

        # Check cache
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=60):  # 1-minute cache for quotes
                print(f"💾 Using cached quote for {symbol}")
                return data

        # Try Alpha Vantage first
        av_data = self.get_alpha_vantage_data(symbol, "GLOBAL_QUOTE")
        if av_data and "Global Quote" in av_data:
            quote = av_data["Global Quote"]
            quote_data = {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "latest_trading_day": quote.get("07. latest trading day", ""),
                "source": "Alpha Vantage"
            }
            self.cache[cache_key] = (quote_data, datetime.now())
            return quote_data

        # Try RapidAPI as fallback
        rapid_data = self.get_rapid_api_quote(symbol)
        if rapid_data:
            quote_data = {
                "symbol": symbol,
                "price": rapid_data.get("price", 0),
                "change": rapid_data.get("change", 0),
                "change_percent": f"{rapid_data.get('changesPercentage', 0)}%",
                "volume": rapid_data.get("volume", 0),
                "latest_trading_day": rapid_data.get("timestamp", ""),
                "source": "RapidAPI"
            }
            self.cache[cache_key] = (quote_data, datetime.now())
            return quote_data

        print(f"⚠️ Could not fetch real-time quote for {symbol} from any source")
        return None

    def get_comprehensive_analysis(self, symbol: str):
        """
        Get comprehensive analysis combining multiple data sources

        Args:
            symbol: Stock symbol

        Returns:
            dict: Comprehensive analysis data
        """
        print(f"\n📊 Fetching comprehensive analysis for {symbol}...")
        print("=" * 60)

        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "data_sources": []
        }

        # 1. Real-time quote
        quote = self.get_real_time_quote(symbol)
        if quote:
            analysis["quote"] = quote
            analysis["data_sources"].append(quote["source"])
            print(f"✅ Real-time quote: ${quote['price']} ({quote['change_percent']})")

        # 2. Company fundamentals
        fundamentals = self.get_company_fundamentals(symbol)
        if fundamentals:
            analysis["fundamentals"] = fundamentals
            analysis["data_sources"].append("Alpha Vantage Fundamentals")
            print(f"✅ Fundamentals: {fundamentals['name']} | Sector: {fundamentals['sector']}")

        # 3. News and sentiment
        news = self.get_news_sentiment(symbol)
        if news:
            analysis["news"] = news
            analysis["data_sources"].append("Tavily News")
            print(f"✅ News: Found {len(news['articles'])} recent articles")

        print("=" * 60)
        print(f"✅ Analysis complete using {len(analysis['data_sources'])} data sources\n")

        return analysis

    def get_intraday_data(self, symbol: str, interval: str = "5min"):
        """
        Get intraday data from Alpha Vantage

        Args:
            symbol: Stock symbol
            interval: Time interval (1min, 5min, 15min, 30min, 60min)

        Returns:
            pandas.DataFrame: Intraday OHLCV data
        """
        if not self.alpha_vantage_key:
            return None

        try:
            data = self.get_alpha_vantage_data(symbol, f"TIME_SERIES_INTRADAY")

            if not data:
                return None

            # Parse time series data
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                print(f"⚠️ Intraday data not available for interval {interval}")
                return None

            time_series = data[time_series_key]

            # Convert to DataFrame
            df_data = []
            for timestamp, values in time_series.items():
                df_data.append({
                    "timestamp": pd.to_datetime(timestamp),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"])
                })

            df = pd.DataFrame(df_data)
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)

            print(f"✅ Fetched {len(df)} intraday data points for {symbol}")
            return df

        except Exception as e:
            print(f"❌ Error fetching intraday data: {str(e)}")
            return None

    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        print("🧹 Cache cleared")

    def get_cache_info(self):
        """Get cache statistics"""
        return {
            "cached_items": len(self.cache),
            "cache_timeout_seconds": self.cache_timeout,
            "items": list(self.cache.keys())
        }


# Example usage and testing
if __name__ == "__main__":
    print("🚀 Enhanced Market Data Integration Test")
    print("=" * 60)

    # Initialize
    market_data = EnhancedMarketData()

    # Test symbol
    test_symbol = "AAPL"

    # Test 1: Real-time quote
    print("\n1️⃣ Testing Real-Time Quote...")
    quote = market_data.get_real_time_quote(test_symbol)
    if quote:
        print(f"   Price: ${quote['price']}")
        print(f"   Change: {quote['change_percent']}")

    # Test 2: Fundamentals
    print("\n2️⃣ Testing Company Fundamentals...")
    fundamentals = market_data.get_company_fundamentals(test_symbol)
    if fundamentals:
        print(f"   Company: {fundamentals['name']}")
        print(f"   Sector: {fundamentals['sector']}")
        print(f"   Market Cap: ${fundamentals['market_cap']}")

    # Test 3: News
    print("\n3️⃣ Testing News & Sentiment...")
    news = market_data.get_news_sentiment(test_symbol)
    if news:
        print(f"   Found {len(news['articles'])} articles")
        if news['articles']:
            print(f"   Latest: {news['articles'][0]['title'][:60]}...")

    # Test 4: Comprehensive Analysis
    print("\n4️⃣ Testing Comprehensive Analysis...")
    analysis = market_data.get_comprehensive_analysis(test_symbol)
    print(f"   Data Sources: {', '.join(analysis['data_sources'])}")

    print("\n" + "=" * 60)
    print("✅ Testing complete!")
