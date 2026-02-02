import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class CSVStorage:
    def __init__(self):
        # Create storage directory if it doesn't exist
        self.storage_dir = "data_storage"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Define CSV file paths
        self.trading_signals_file = os.path.join(self.storage_dir, "trading_signals.csv")
        self.trading_decisions_file = os.path.join(self.storage_dir, "trading_decisions.csv")
        self.screened_stocks_file = os.path.join(self.storage_dir, "screened_stocks.csv")
        
        # Initialize CSV files with headers if they don't exist
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize CSV files with proper headers if they don't exist"""
        
        # Trading signals CSV
        if not os.path.exists(self.trading_signals_file):
            signals_df = pd.DataFrame(columns=[
                'id', 'symbol', 'signal_type', 'strategy', 'confidence', 'timestamp'
            ])
            signals_df.to_csv(self.trading_signals_file, index=False)
        
        # Trading decisions CSV
        if not os.path.exists(self.trading_decisions_file):
            decisions_df = pd.DataFrame(columns=[
                'id', 'symbol', 'decision', 'confidence', 'agent_name', 'created_at'
            ])
            decisions_df.to_csv(self.trading_decisions_file, index=False)
        
        # Audit trail CSV for detailed supervisor and regulatory decisions
        self.audit_trail_file = os.path.join(self.storage_dir, "audit_trail.csv")
        if not os.path.exists(self.audit_trail_file):
            audit_df = pd.DataFrame(columns=[
                'id', 'symbol', 'timestamp', 'decision_type', 'action', 'confidence', 
                'rationale', 'compliance_status', 'risk_level', 'position_size', 'blocked_trades'
            ])
            audit_df.to_csv(self.audit_trail_file, index=False)
        
        # Screened stocks CSV
        if not os.path.exists(self.screened_stocks_file):
            stocks_df = pd.DataFrame(columns=[
                'id', 'symbol', 'company_name', 'current_price', 'average_volume', 'last_updated'
            ])
            stocks_df.to_csv(self.screened_stocks_file, index=False)
    
    def add_signal(self, symbol: str, signal_type: str, strategy: str, confidence: float):
        """Add a trading signal to CSV"""
        try:
            # Read existing data
            if os.path.exists(self.trading_signals_file):
                df = pd.read_csv(self.trading_signals_file)
            else:
                df = pd.DataFrame(columns=['id', 'symbol', 'signal_type', 'strategy', 'confidence', 'timestamp'])
            
            # Create new row
            new_id = len(df) + 1
            new_row = {
                'id': new_id,
                'symbol': symbol,
                'signal_type': signal_type,
                'strategy': strategy,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add row and save
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.trading_signals_file, index=False)
            
        except Exception as e:
            print(f"Error saving signal to CSV: {str(e)}")
    
    def save_trading_decision(self, symbol: str, decision: str, confidence: float, agent_name: str = 'supervisor'):
        """Save a trading decision to CSV"""
        try:
            # Read existing data
            if os.path.exists(self.trading_decisions_file):
                df = pd.read_csv(self.trading_decisions_file)
            else:
                df = pd.DataFrame(columns=['id', 'symbol', 'decision', 'confidence', 'agent_name', 'created_at'])
            
            # Create new row
            new_id = len(df) + 1
            new_row = {
                'id': new_id,
                'symbol': symbol,
                'decision': decision,
                'confidence': confidence,
                'agent_name': agent_name,
                'created_at': datetime.now().isoformat()
            }
            
            # Add row and save
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.trading_decisions_file, index=False)
            
        except Exception as e:
            print(f"Error saving trading decision to CSV: {str(e)}")
    
    def get_latest_trading_decisions(self, symbol: str, limit: int = 2) -> List[Dict]:
        """Get the latest trading decisions for a symbol"""
        try:
            if not os.path.exists(self.trading_decisions_file):
                return []
            
            df = pd.read_csv(self.trading_decisions_file)
            
            # Filter by symbol and sort by created_at (most recent first)
            symbol_df = df[df['symbol'] == symbol].copy()
            if len(symbol_df) == 0:
                return []
            
            symbol_df['created_at'] = pd.to_datetime(symbol_df['created_at'])
            symbol_df = symbol_df.sort_values('created_at', ascending=False)
            
            # Limit results
            symbol_df = symbol_df.head(limit)
            
            # Convert to list of dictionaries
            return symbol_df.to_dict('records')
            
        except Exception as e:
            print(f"Error reading trading decisions from CSV: {str(e)}")
            return []
    
    def get_all_agent_decisions(self, symbol: str) -> List[Dict]:
        """Get the latest decision from each agent for a symbol"""
        try:
            if not os.path.exists(self.trading_decisions_file):
                return []
            
            df = pd.read_csv(self.trading_decisions_file)
            
            # Filter by symbol
            symbol_df = df[df['symbol'] == symbol].copy()
            if len(symbol_df) == 0:
                return []
            
            symbol_df['created_at'] = pd.to_datetime(symbol_df['created_at'])
            
            # Get the latest decision for each agent
            latest_decisions = symbol_df.sort_values('created_at', ascending=False).groupby('agent_name').first().reset_index()
            
            # Convert to list of dictionaries
            return latest_decisions.to_dict('records')
            
        except Exception as e:
            print(f"Error reading agent decisions from CSV: {str(e)}")
            return []
    
    def get_trading_decisions(self, symbol: str = None) -> List[Dict]:
        """Get trading decisions, optionally filtered by symbol"""
        try:
            if not os.path.exists(self.trading_decisions_file):
                return []
            
            df = pd.read_csv(self.trading_decisions_file)
            
            # Filter by symbol if provided
            if symbol:
                df = df[df['symbol'] == symbol].copy()
            
            if len(df) == 0:
                return []
            
            # Sort by created_at (most recent first)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at', ascending=False)
            
            # Convert to list of dictionaries
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Error reading trading decisions from CSV: {str(e)}")
            return []
    
    def get_decisions_summary(self) -> Dict[str, Any]:
        """Get summary of all trading decisions across all symbols"""
        return self.get_all_decisions_summary()
    
    def upsert_screened_stock(self, symbol: str, company_name: str, current_price: float, average_volume: int):
        """Add or update a screened stock in CSV"""
        try:
            # Read existing data
            if os.path.exists(self.screened_stocks_file):
                df = pd.read_csv(self.screened_stocks_file)
            else:
                df = pd.DataFrame(columns=['id', 'symbol', 'company_name', 'current_price', 'average_volume', 'last_updated'])
            
            # Check if symbol already exists
            existing_row = df[df['symbol'] == symbol]
            
            if len(existing_row) > 0:
                # Update existing row
                df.loc[df['symbol'] == symbol, 'company_name'] = company_name
                df.loc[df['symbol'] == symbol, 'current_price'] = current_price
                df.loc[df['symbol'] == symbol, 'average_volume'] = average_volume
                df.loc[df['symbol'] == symbol, 'last_updated'] = datetime.now().isoformat()
            else:
                # Add new row
                new_id = len(df) + 1
                new_row = {
                    'id': new_id,
                    'symbol': symbol,
                    'company_name': company_name,
                    'current_price': current_price,
                    'average_volume': average_volume,
                    'last_updated': datetime.now().isoformat()
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save
            df.to_csv(self.screened_stocks_file, index=False)
            
        except Exception as e:
            print(f"Error saving screened stock to CSV: {str(e)}")
    
    def get_screened_stocks(self) -> List[Dict]:
        """Get all screened stocks"""
        try:
            if not os.path.exists(self.screened_stocks_file):
                return []
            
            df = pd.read_csv(self.screened_stocks_file)
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Error reading screened stocks from CSV: {str(e)}")
            return []
    
    def clear_old_screened_stocks(self, hours: int = 24):
        """Clear old screened stocks from CSV"""
        try:
            if not os.path.exists(self.screened_stocks_file):
                return
            
            df = pd.read_csv(self.screened_stocks_file)
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            
            # Keep only recent entries
            cutoff_time = datetime.now() - pd.Timedelta(hours=hours)
            df = df[df['last_updated'] >= cutoff_time]
            
            # Save
            df.to_csv(self.screened_stocks_file, index=False)
            
        except Exception as e:
            print(f"Error clearing old screened stocks from CSV: {str(e)}")
    
    def get_all_decisions_summary(self) -> Dict:
        """Get a summary of all decisions for dashboard display"""
        try:
            if not os.path.exists(self.trading_decisions_file):
                return {"total_decisions": 0, "agents": [], "symbols": []}
            
            df = pd.read_csv(self.trading_decisions_file)
            
            summary = {
                "total_decisions": len(df),
                "agents": df['agent_name'].unique().tolist() if len(df) > 0 else [],
                "symbols": df['symbol'].unique().tolist() if len(df) > 0 else [],
                "latest_decisions": df.tail(5).to_dict('records') if len(df) > 0 else []
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting decisions summary from CSV: {str(e)}")
            return {"total_decisions": 0, "agents": [], "symbols": []}
    
    def save_audit_entry(self, symbol, decision_type, action, confidence, rationale, 
                        compliance_status=None, risk_level=None, position_size=None, blocked_trades=None):
        """Save detailed audit entry for supervisor and regulatory decisions"""
        try:
            # Read existing data
            if os.path.exists(self.audit_trail_file):
                df = pd.read_csv(self.audit_trail_file)
            else:
                df = pd.DataFrame(columns=[
                    'id', 'symbol', 'timestamp', 'decision_type', 'action', 'confidence', 
                    'rationale', 'compliance_status', 'risk_level', 'position_size', 'blocked_trades'
                ])
            
            # Create new audit entry
            new_id = len(df) + 1
            new_entry = {
                'id': new_id,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'decision_type': decision_type,  # 'SUPERVISOR' or 'REGULATORY'
                'action': action,
                'confidence': confidence,
                'rationale': rationale if rationale else '',  # Keep full rationale
                'compliance_status': compliance_status or '',
                'risk_level': risk_level or '',
                'position_size': position_size or '',
                'blocked_trades': blocked_trades or ''
            }
            
            # Add entry and save
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(self.audit_trail_file, index=False)
            
        except Exception as e:
            print(f"Error saving audit entry to CSV: {str(e)}")
    
    def get_audit_trail(self, symbol=None, limit=50):
        """Get audit trail entries, optionally filtered by symbol"""
        try:
            if not os.path.exists(self.audit_trail_file):
                return []
            
            df = pd.read_csv(self.audit_trail_file)
            
            if symbol:
                df = df[df['symbol'] == symbol]
            
            # Sort by timestamp (most recent first)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
            
            # Limit results
            df = df.head(limit)
            
            # Convert to list of dictionaries and handle NaN values
            records = df.to_dict('records')
            
            # Clean up NaN values
            for record in records:
                for key, value in record.items():
                    if pd.isna(value) or str(value).lower() == 'nan':
                        record[key] = ''
            
            return records
            
        except Exception as e:
            print(f"Error reading audit trail from CSV: {str(e)}")
            return []
    
    def get_audit_summary(self):
        """Get summary of audit trail for dashboard"""
        try:
            if not os.path.exists(self.audit_trail_file):
                return {"total_entries": 0, "supervisor_decisions": 0, "regulatory_decisions": 0, "symbols": []}
            
            df = pd.read_csv(self.audit_trail_file)
            
            summary = {
                "total_entries": len(df),
                "supervisor_decisions": len(df[df['decision_type'] == 'SUPERVISOR']),
                "regulatory_decisions": len(df[df['decision_type'] == 'REGULATORY']),
                "symbols": df['symbol'].unique().tolist() if len(df) > 0 else [],
                "latest_entries": df.tail(10).to_dict('records') if len(df) > 0 else []
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting audit summary from CSV: {str(e)}")
            return {"total_entries": 0, "supervisor_decisions": 0, "regulatory_decisions": 0, "symbols": []}