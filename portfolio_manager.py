import yfinance as yf
import pandas as pd
from typing import List, Dict
import datetime

class PortfolioManager:
    def __init__(self):
        self.portfolio = {}
        self.historical_data = {}

    def add_stock(self, ticker: str, shares: float = 0) -> bool:
        """
        Add a stock to the portfolio
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if info:
                self.portfolio[ticker] = {
                    'shares': shares,
                    'info': info
                }
                return True
        except Exception as e:
            print(f"Error adding stock {ticker}: {str(e)}")
            return False
        return False

    def remove_stock(self, ticker: str) -> bool:
        """
        Remove a stock from the portfolio
        """
        if ticker in self.portfolio:
            del self.portfolio[ticker]
            return True
        return False

    def update_stock_data(self) -> None:
        """
        Update historical data for all stocks in portfolio
        """
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        
        for ticker in self.portfolio.keys():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                self.historical_data[ticker] = hist
            except Exception as e:
                print(f"Error updating data for {ticker}: {str(e)}")

    def get_portfolio_summary(self) -> Dict:
        """
        Get summary of the current portfolio
        """
        summary = {
            'total_stocks': len(self.portfolio),
            'stocks': []
        }
        
        for ticker, data in self.portfolio.items():
            stock_info = {
                'ticker': ticker,
                'shares': data['shares'],
                'current_price': data['info'].get('currentPrice', 0),
                'market_cap': data['info'].get('marketCap', 0),
                'sector': data['info'].get('sector', 'N/A')
            }
            summary['stocks'].append(stock_info)
        
        return summary

    def get_stock_performance(self, ticker: str) -> pd.DataFrame:
        """
        Get historical performance data for a specific stock
        """
        if ticker in self.historical_data:
            return self.historical_data[ticker]
        return pd.DataFrame() 