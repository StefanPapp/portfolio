import sqlite3
from typing import Dict, List, Optional
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "portfolio.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create portfolios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create portfolio_stocks table (junction table)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_stocks (
                    portfolio_id INTEGER,
                    ticker TEXT,
                    allocation REAL DEFAULT 1.0,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id) ON DELETE CASCADE,
                    FOREIGN KEY (ticker) REFERENCES stocks (ticker) ON DELETE CASCADE,
                    PRIMARY KEY (portfolio_id, ticker)
                )
            ''')
            
            # Create stocks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    ticker TEXT PRIMARY KEY,
                    shares REAL,
                    info TEXT,
                    last_updated TIMESTAMP
                )
            ''')
            
            # Create historical_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_data (
                    ticker TEXT,
                    date TIMESTAMP,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (ticker, date)
                )
            ''')
            
            conn.commit()

    def create_portfolio(self, name: str, description: str = "") -> Optional[int]:
        """Create a new portfolio and return its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO portfolios (name, description)
                    VALUES (?, ?)
                ''', (name, description))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Portfolio with name '{name}' already exists")
            return None
        except Exception as e:
            print(f"Error creating portfolio: {str(e)}")
            return None

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio and its stock assignments"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM portfolios WHERE id = ?', (portfolio_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting portfolio: {str(e)}")
            return False

    def add_stock_to_portfolio(self, portfolio_id: int, ticker: str, allocation: float = 1.0) -> bool:
        """Add a stock to a portfolio with optional allocation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio_stocks (portfolio_id, ticker, allocation)
                    VALUES (?, ?, ?)
                ''', (portfolio_id, ticker, allocation))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding stock to portfolio: {str(e)}")
            return False

    def remove_stock_from_portfolio(self, portfolio_id: int, ticker: str) -> bool:
        """Remove a stock from a portfolio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM portfolio_stocks 
                    WHERE portfolio_id = ? AND ticker = ?
                ''', (portfolio_id, ticker))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error removing stock from portfolio: {str(e)}")
            return False

    def get_portfolios(self) -> List[Dict]:
        """Get all portfolios with their stocks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.name, p.description, p.created_at,
                           GROUP_CONCAT(ps.ticker) as tickers,
                           GROUP_CONCAT(ps.allocation) as allocations
                    FROM portfolios p
                    LEFT JOIN portfolio_stocks ps ON p.id = ps.portfolio_id
                    GROUP BY p.id
                ''')
                rows = cursor.fetchall()
                
                portfolios = []
                for row in rows:
                    portfolio = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'stocks': []
                    }
                    
                    if row[4]:  # If there are stocks
                        tickers = row[4].split(',')
                        allocations = [float(a) for a in row[5].split(',')]
                        for ticker, allocation in zip(tickers, allocations):
                            portfolio['stocks'].append({
                                'ticker': ticker,
                                'allocation': allocation
                            })
                    
                    portfolios.append(portfolio)
                return portfolios
        except Exception as e:
            print(f"Error getting portfolios: {str(e)}")
            return []

    def get_portfolio(self, portfolio_id: int) -> Optional[Dict]:
        """Get a specific portfolio with its stocks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.name, p.description, p.created_at,
                           GROUP_CONCAT(ps.ticker) as tickers,
                           GROUP_CONCAT(ps.allocation) as allocations
                    FROM portfolios p
                    LEFT JOIN portfolio_stocks ps ON p.id = ps.portfolio_id
                    WHERE p.id = ?
                    GROUP BY p.id
                ''', (portfolio_id,))
                row = cursor.fetchone()
                
                if row:
                    portfolio = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'stocks': []
                    }
                    
                    if row[4]:  # If there are stocks
                        tickers = row[4].split(',')
                        allocations = [float(a) for a in row[5].split(',')]
                        for ticker, allocation in zip(tickers, allocations):
                            portfolio['stocks'].append({
                                'ticker': ticker,
                                'allocation': allocation
                            })
                    
                    return portfolio
                return None
        except Exception as e:
            print(f"Error getting portfolio: {str(e)}")
            return None

    def save_stock(self, ticker: str, shares: float, info: Dict) -> bool:
        """Save or update stock information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stocks (ticker, shares, info, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (ticker, shares, json.dumps(info), datetime.now()))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving stock {ticker}: {str(e)}")
            return False

    def save_historical_data(self, ticker: str, historical_data: Dict) -> bool:
        """Save historical data for a stock"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert historical data to list of tuples
                data_tuples = [
                    (ticker, date, row['Open'], row['High'], row['Low'], 
                     row['Close'], row['Volume'])
                    for date, row in historical_data.items()
                ]
                
                # Insert or replace historical data
                cursor.executemany('''
                    INSERT OR REPLACE INTO historical_data 
                    (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', data_tuples)
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving historical data for {ticker}: {str(e)}")
            return False

    def load_stocks(self) -> Dict:
        """Load all stocks from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT ticker, shares, info FROM stocks')
                rows = cursor.fetchall()
                
                portfolio = {}
                for row in rows:
                    ticker, shares, info_json = row
                    portfolio[ticker] = {
                        'shares': shares,
                        'info': json.loads(info_json)
                    }
                return portfolio
        except Exception as e:
            print(f"Error loading stocks: {str(e)}")
            return {}

    def load_historical_data(self, ticker: str) -> Optional[Dict]:
        """Load historical data for a specific stock"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT date, open, high, low, close, volume 
                    FROM historical_data 
                    WHERE ticker = ?
                    ORDER BY date
                ''', (ticker,))
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Convert rows to DataFrame-like dictionary
                historical_data = {}
                for row in rows:
                    date, open_price, high, low, close, volume = row
                    historical_data[date] = {
                        'Open': open_price,
                        'High': high,
                        'Low': low,
                        'Close': close,
                        'Volume': volume
                    }
                return historical_data
        except Exception as e:
            print(f"Error loading historical data for {ticker}: {str(e)}")
            return None

    def delete_stock(self, ticker: str) -> bool:
        """Delete a stock and its historical data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM stocks WHERE ticker = ?', (ticker,))
                cursor.execute('DELETE FROM historical_data WHERE ticker = ?', (ticker,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting stock {ticker}: {str(e)}")
            return False 