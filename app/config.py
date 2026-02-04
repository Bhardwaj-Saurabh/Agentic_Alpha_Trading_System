# Configuration file for API keys and settings
# Replace the placeholder values with your actual API keys
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API Configuration
    #TODO: Replace with the openai key.  
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your OpenAI API key
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # Default model is gpt-4o
    
    # Alternative AI Service (Anthropic) - Optional
    ANTHROPIC_API_KEY = "your_anthropic_api_key_here"  # Optional, only if using Anthropic
    
    # Financial Data APIs - Optional
    # I am leaving these here to know there are other apis that you can use in the future.
    ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key_here"  # Optional, for additional market data
    QUANDL_API_KEY = "your_quandl_key_here"  # Optional, for financial data
    
    # News and Sentiment APIs - Optional  
    # I am leaving this here to show that taviliy is a great way to use news api to get better sentiment analysis.
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Optional, for news sentiment analysis
    
    # Database Configuration
    # Set DATABASE_URL in your .env file or update below
    # Format: postgresql://username:password@host:port/database_name
    # Example: postgresql://postgres:password@localhost:5432/trading_db
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/trading_db")
    
    # Application Settings
    DEFAULT_SYMBOL = "AAPL"
    CACHE_TIMEOUT_HOURS = 12
    
    # AI Model Settings
    DEFAULT_AI_MODEL = "gpt-4o"  # or "claude-sonnet-4-20250514" if using Anthropic
    USE_OPENAI = True  # Set to False to use Anthropic instead

# Instructions for setup:
# 1. Replace "your_openai_api_key_here" with your actual OpenAI API key in .env file
# 2. Database Setup (PostgreSQL):
#    a. Install PostgreSQL: https://www.postgresql.org/download/
#    b. Create a database: CREATE DATABASE trading_db;
#    c. Update DATABASE_URL in .env file:
#       DATABASE_URL=postgresql://username:password@localhost:5432/trading_db
#    d. The application will automatically create all required tables on first run
#
# Alternative: For quick testing without PostgreSQL, the app will attempt to use the default connection

