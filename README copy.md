# AI Trading System - Setup Instructions

## Overview
This AI Trading System has been converted to use configuration files instead of environment variables, making it completely portable and downloadable.

## Quick Setup

### 1. **Get your OpenAI API Key**
- Go to [OpenAI Platform](https://platform.openai.com/api-keys)
- Create a new API key
- Copy the key (starts with `sk-proj-` or `sk-`)

### 2. **Configure API Keys**
- Open `app/config.py` 
- Replace `"your_openai_api_key_here"` with your actual OpenAI API key
- Example: `OPENAI_API_KEY = "sk-proj-abc123..."`

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run the Application**
```bash
streamlit run app/main.py --server.port 5000 --server.address 0.0.0.0
```

## File Structure
```
AI-Trading-System/
├── app/
│   ├── config.py          # ← Configure your API keys here
│   ├── main.py            # Main Streamlit application
│   ├── agents/            # AI trading agents
│   ├── models/            # Data models
│   ├── tools/             # Trading tools
│   ├── storage/           # Data storage
│   └── data/              # Market data handlers
├── requirements.txt       # Python dependencies
└── SETUP_INSTRUCTIONS.md  # This file
```

## Optional Configuration

### Additional API Keys (Optional)
- **Tavily API** (for news sentiment): Add your key to `Config.TAVILY_API_KEY`
- **Alpha Vantage** (backup market data): Add your key to `Config.ALPHA_VANTAGE_API_KEY`
- **Anthropic Claude** (alternative AI): Add your key to `Config.ANTHROPIC_API_KEY`

### Database Configuration
- Default: Uses CSV files for storage
- For PostgreSQL: Update `Config.DATABASE_URL` with your database connection string

## Features

### Individual AI Agent Control
- **📈 Market Analyst**: Analyzes market data and technical indicators
- **🎯 Strategy Agent**: Develops trading strategies (requires Market Analyst)
- **⚠️ Risk Manager**: Assesses trading risks (requires Market Analyst)
- **🏛️ Regulatory Agent**: Checks compliance (requires Market + Strategy)
- **🎯 Supervisor Agent**: Makes final decisions (requires ALL other agents)

### Dependency System
- Each agent checks if required prerequisite agents have run
- Clear error messages tell you which agents to run first
- Progress tracking shows completion status

### Trade Execution
- Separate "Execute Trade" button saves results to database
- No automatic database updates during analysis
- Full control over when trades are recorded

## Usage Flow
1. **Load Stock Data** - Enter symbol (e.g., AAPL, MSFT) and click "Load Stock Data"
2. **Run Agents** - Click individual agent buttons in the sidebar in order
3. **Review Analysis** - Each agent provides detailed analysis results
4. **Execute Trade** - Click "Execute Trade" to save final decision to database

## Troubleshooting

### "Model initialization issue"
- Check that your OpenAI API key is correctly set in `app/config.py`
- Ensure your API key is valid and has sufficient credits

### "Please load stock data first"
- Click "Load Stock Data" in the sidebar before running agents
- Make sure the stock symbol is valid

### Database connection errors
- The system will work with CSV storage even if database connection fails
- For PostgreSQL, ensure your `DATABASE_URL` is correct in config.py

## Offline Usage
- The system can work offline using demo data
- CSV storage works without internet connection
- Only AI analysis requires internet for API calls

## Download and Portability
- All configuration is in files (no environment variables)
- Complete system can be zipped and moved to any computer
- Just install Python dependencies and add your API key

---

🚀 **Ready to trade!** The system is now completely portable and ready for download.