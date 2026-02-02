import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .demo_data import generate_demo_stock_data, get_demo_company_info


class MarketData:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour cache to improve performance

    def get_stock_data(self, symbol, period='1mo', interval='1d'):
        """
        Get stock data using Yahoo Finance (completely free, no API limits)
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Period to fetch ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            pandas.DataFrame: Stock data with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        # Standardize the symbol to uppercase
        symbol = symbol.upper().strip()
        cache_key = f"{symbol}_{period}_{interval}"

        # Check cache first to improve performance
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                print(f"Using cached data for {symbol}")
                return data

        try:
            print(f"Fetching fresh data for {symbol} from Yahoo Finance (Free API)")
            
            # Create ticker object with session for better reliability
            stock = yf.Ticker(symbol)
            
            # Try different approaches if first one fails
            data = None
            
            # First attempt: Normal fetch
            try:
                data = stock.history(period=period, interval=interval)
                if data.empty:
                    print(f"Empty data returned for {symbol}, trying alternative method...")
                    # Try with different parameters
                    data = stock.history(period='5d', interval='1d')
            except Exception as first_error:
                print(f"First fetch attempt failed: {str(first_error)}")
                
                # Second attempt: Use shorter period as fallback
                try:
                    print(f"Trying fallback fetch for {symbol}...")
                    data = stock.history(period='5d', interval='1d')
                except Exception as second_error:
                    print(f"Second fetch attempt failed: {str(second_error)}")
                    
                    # Third attempt: Use even shorter period
                    try:
                        print(f"Trying minimal fetch for {symbol}...")
                        data = stock.history(period='1d', interval='1d')
                    except Exception as third_error:
                        print(f"All fetch attempts failed: {str(third_error)}")
                        data = pd.DataFrame()

            # Ensure we have data
            if data is not None and not data.empty:
                # Remove timezone information if present for consistency
                if data.index.tz is not None:
                    data.index = data.index.tz_localize(None)
                
                # Ensure we have the required columns
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in required_columns:
                    if col not in data.columns:
                        data[col] = 0  # Add missing columns with zeros
                
                # Cache the result
                self.cache[cache_key] = (data, datetime.now())
                print(f"Successfully fetched {len(data)} rows of data for {symbol}")
                return data
            else:
                print(f"Yahoo Finance failed to provide data for {symbol}. Using demo data for AI agent teaching.")
                # Use demo data as fallback for teaching purposes
                demo_data = generate_demo_stock_data(symbol, days=30)
                self.cache[cache_key] = (demo_data, datetime.now())
                print(f"Generated {len(demo_data)} rows of demo data for {symbol}")
                return demo_data
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            print(f"Using demo data as fallback for teaching purposes")
            # Generate demo data as final fallback
            try:
                demo_data = generate_demo_stock_data(symbol, days=30)
                self.cache[cache_key] = (demo_data, datetime.now())
                return demo_data
            except Exception as demo_error:
                print(f"Error generating demo data: {str(demo_error)}")
                return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

    # def get_company_info(self, symbol):
    #     """
    #     Get basic company information (optional - for educational purposes)
        
    #     Args:
    #         symbol: Stock symbol
            
    #     Returns:
    #         dict: Company information
    #     """
    #     try:
    #         stock = yf.Ticker(symbol.upper())
    #         info = stock.info
            
    #         # Extract basic info safely
    #         if info and len(info) > 1:  # Check if we got real data
    #             company_info = {
    #                 'name': info.get('longName', symbol.upper()),
    #                 'sector': info.get('sector', 'Unknown'),
    #                 'industry': info.get('industry', 'Unknown'),
    #                 'market_cap': info.get('marketCap', 0),
    #                 'description': info.get('longBusinessSummary', 'No description available')[:200] + '...'
    #             }
    #             return company_info
    #         else:
    #             # Fallback to demo data
    #             return get_demo_company_info(symbol)
            
    #     except Exception as e:
    #         print(f"Error fetching company info for {symbol}: {str(e)}, using demo data")
    #         return get_demo_company_info(symbol)

    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators for the stock data
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame: Original data with added technical indicators
        """
        if df.empty:
            return df

        try:
            # Make a copy to avoid modifying the original
            df = df.copy()
            
            # MACD (Moving Average Convergence Divergence)
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

            # Bollinger Bands
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['20dSTD'] = df['Close'].rolling(window=20).std()
            df['Upper_Band'] = df['MA20'] + (df['20dSTD'] * 2)
            df['Lower_Band'] = df['MA20'] - (df['20dSTD'] * 2)

            # RSI (Relative Strength Index)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Simple Moving Averages
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()

            # Volume Moving Average
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

            # Price change percentage
            df['Price_Change_Pct'] = df['Close'].pct_change() * 100

            print(f"Successfully calculated technical indicators")
            return df
            
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            return df

    def get_popular_symbols(self):
        """
        Return a list of popular stock symbols for testing/demo purposes
        
        Returns:
            list: Popular stock symbols
        """
        return [
            'AAPL',  # Apple
            'MSFT',  # Microsoft  
            'GOOGL', # Alphabet/Google
            'AMZN',  # Amazon
            'TSLA',  # Tesla
            'META',  # Meta/Facebook
            'NVDA',  # NVIDIA
            'NFLX',  # Netflix
            'DIS',   # Disney
            'BA',    # Boeing
            'JPM',   # JPMorgan Chase
            'JNJ',   # Johnson & Johnson
            'V',     # Visa
            'WMT',   # Walmart
            'PG'     # Procter & Gamble
        ]

    def clear_cache(self):
        """Clear the data cache"""
        self.cache = {}
        print("Data cache cleared")
        
    def get_cache_info(self):
        """Get information about cached data"""
        return {
            'cached_symbols': len(self.cache),
            'cache_timeout_hours': self.cache_timeout / 3600,
            'symbols': [key.split('_')[0] for key in self.cache.keys()]
        }