import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_demo_stock_data(symbol, days=30):
    """
    Generate realistic demo stock data for teaching purposes
    This ensures the AI agents have data to analyze even if external APIs fail
    """
    
    # Define realistic base prices for common symbols
    base_prices = {
        'AAPL': 150.0,
        'MSFT': 280.0,
        'GOOGL': 2500.0,
        'AMZN': 3000.0,
        'TSLA': 200.0,
        'META': 200.0,
        'NVDA': 400.0,
        'NFLX': 400.0,
        'DIS': 100.0,
        'BA': 200.0,
        'JPM': 150.0,
        'JNJ': 160.0,
        'V': 250.0,
        'WMT': 140.0,
        'PG': 150.0
    }
    
    # Get base price or use a default
    base_price = base_prices.get(symbol.upper(), 100.0)
    
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Remove weekends (simulate market days only)
    dates = [d for d in dates if d.weekday() < 5]  # Monday=0, Friday=4
    
    # Generate realistic price movements
    np.random.seed(hash(symbol) % 2147483647)  # Consistent data for same symbol
    
    prices = []
    current_price = base_price
    
    for i, date in enumerate(dates):
        # Add some trend and volatility
        trend = 0.0005 * (i - len(dates)/2)  # Slight upward trend over time
        volatility = np.random.normal(0, 0.02)  # 2% daily volatility
        
        # Calculate daily change
        daily_change = trend + volatility
        current_price = current_price * (1 + daily_change)
        
        # Ensure price doesn't go negative
        current_price = max(current_price, 1.0)
        prices.append(current_price)
    
    # Generate OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic intraday high/low based on volatility
        daily_vol = abs(np.random.normal(0, 0.015))  # Intraday volatility
        
        open_price = close * (1 + np.random.normal(0, 0.005))
        high = max(open_price, close) * (1 + daily_vol)
        low = min(open_price, close) * (1 - daily_vol)
        
        # Generate volume (higher volume on bigger price moves)
        price_change = abs((close - open_price) / open_price) if open_price > 0 else 0
        base_volume = 1000000  # Base volume
        volume = int(base_volume * (1 + price_change * 5) * np.random.uniform(0.5, 2.0))
        
        data.append({
            'Open': round(open_price, 2),
            'High': round(high, 2),
            'Low': round(low, 2),
            'Close': round(close, 2),
            'Volume': volume
        })
    
    # Create DataFrame
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    
    return df

def get_demo_company_info(symbol):
    """
    Return demo company information for common symbols
    """
    company_data = {
        'AAPL': {
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'market_cap': 3000000000000,
            'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...'
        },
        'MSFT': {
            'name': 'Microsoft Corporation',
            'sector': 'Technology', 
            'industry': 'Software',
            'market_cap': 2800000000000,
            'description': 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide...'
        },
        'GOOGL': {
            'name': 'Alphabet Inc.',
            'sector': 'Communication Services',
            'industry': 'Internet Content & Information',
            'market_cap': 2000000000000,
            'description': 'Alphabet Inc. provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America...'
        },
        'AMZN': {
            'name': 'Amazon.com Inc.',
            'sector': 'Consumer Discretionary',
            'industry': 'Internet & Direct Marketing Retail',
            'market_cap': 1500000000000,
            'description': 'Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally...'
        },
        'TSLA': {
            'name': 'Tesla Inc.',
            'sector': 'Consumer Discretionary',
            'industry': 'Auto Manufacturers',
            'market_cap': 800000000000,
            'description': 'Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems...'
        }
    }
    
    return company_data.get(symbol.upper(), {
        'name': f'{symbol.upper()} Corporation',
        'sector': 'Technology',
        'industry': 'Software',
        'market_cap': 100000000000,
        'description': f'Demo company data for {symbol.upper()} - used for AI agent teaching demonstrations...'
    })