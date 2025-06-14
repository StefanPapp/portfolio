import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import datetime
import plotly.graph_objects as go
from database_manager import DatabaseManager

class PortfolioManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.portfolio = self.db_manager.load_stocks()
        self.historical_data = {}
        self._load_historical_data()

    def _load_historical_data(self):
        """Load historical data for all stocks in portfolio"""
        for ticker in self.portfolio.keys():
            hist_data = self.db_manager.load_historical_data(ticker)
            if hist_data:
                self.historical_data[ticker] = pd.DataFrame.from_dict(hist_data, orient='index')

    def create_portfolio(self, name: str, description: str = "") -> Optional[int]:
        """Create a new portfolio"""
        return self.db_manager.create_portfolio(name, description)

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio"""
        return self.db_manager.delete_portfolio(portfolio_id)

    def add_stock_to_portfolio(self, portfolio_id: int, ticker: str, allocation: float = 1.0) -> bool:
        """Add a stock to a portfolio"""
        return self.db_manager.add_stock_to_portfolio(portfolio_id, ticker, allocation)

    def remove_stock_from_portfolio(self, portfolio_id: int, ticker: str) -> bool:
        """Remove a stock from a portfolio"""
        return self.db_manager.remove_stock_from_portfolio(portfolio_id, ticker)

    def get_portfolios(self) -> List[Dict]:
        """Get all portfolios"""
        return self.db_manager.get_portfolios()

    def get_portfolio(self, portfolio_id: int) -> Optional[Dict]:
        """Get a specific portfolio"""
        return self.db_manager.get_portfolio(portfolio_id)

    def get_portfolio_performance(self, portfolio_id: int) -> Optional[Dict]:
        """Calculate performance metrics for a portfolio"""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return None

        try:
            performance = {
                'total_value': 0,
                'stocks': [],
                'daily_returns': pd.Series(),
                'metrics': {},
                'sector_allocation': {},
                'risk_metrics': {}
            }

            # Calculate individual stock values and portfolio metrics
            for stock in portfolio['stocks']:
                ticker = stock['ticker']
                allocation = stock['allocation']
                
                if ticker in self.portfolio:
                    stock_info = self.portfolio[ticker]
                    current_price = stock_info['info'].get('currentPrice', 0)
                    shares = stock_info['shares']
                    value = current_price * shares * allocation
                    sector = stock_info['info'].get('sector', 'Unknown')
                    
                    # Update sector allocation
                    if sector in performance['sector_allocation']:
                        performance['sector_allocation'][sector] += value
                    else:
                        performance['sector_allocation'][sector] = value
                    
                    performance['stocks'].append({
                        'ticker': ticker,
                        'value': value,
                        'allocation': allocation,
                        'current_price': current_price,
                        'shares': shares,
                        'sector': sector
                    })
                    
                    performance['total_value'] += value

                    # Get historical data for returns calculation
                    if ticker in self.historical_data:
                        hist_data = self.historical_data[ticker]
                        if not performance['daily_returns'].empty:
                            performance['daily_returns'] = performance['daily_returns'].add(
                                hist_data['Close'].pct_change() * allocation, fill_value=0
                            )
                        else:
                            performance['daily_returns'] = hist_data['Close'].pct_change() * allocation

            # Calculate portfolio metrics
            if not performance['daily_returns'].empty:
                returns = performance['daily_returns']
                annualized_return = returns.mean() * 252
                annualized_volatility = returns.std() * np.sqrt(252)
                sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0
                
                # Calculate drawdown
                cumulative_returns = (1 + returns).cumprod()
                rolling_max = cumulative_returns.expanding().max()
                drawdowns = (cumulative_returns - rolling_max) / rolling_max
                max_drawdown = drawdowns.min()
                
                # Calculate additional metrics
                performance['metrics'] = {
                    'total_return': (returns + 1).prod() - 1,
                    'annualized_return': annualized_return,
                    'volatility': annualized_volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'sortino_ratio': self._calculate_sortino_ratio(returns),
                    'calmar_ratio': self._calculate_calmar_ratio(annualized_return, max_drawdown),
                    'beta': self._calculate_beta(returns),
                    'alpha': self._calculate_alpha(returns, annualized_return)
                }
                
                # Calculate risk metrics
                performance['risk_metrics'] = {
                    'var_95': self._calculate_var(returns, 0.95),
                    'var_99': self._calculate_var(returns, 0.99),
                    'cvar_95': self._calculate_cvar(returns, 0.95),
                    'cvar_99': self._calculate_cvar(returns, 0.99),
                    'tracking_error': self._calculate_tracking_error(returns)
                }

            return performance

        except Exception as e:
            print(f"Error calculating portfolio performance: {str(e)}")
            return None

    def compare_portfolios(self, portfolio_ids: List[int]) -> Optional[Dict]:
        """Compare multiple portfolios"""
        try:
            comparison = {
                'portfolios': [],
                'metrics': pd.DataFrame(),
                'correlation_matrix': pd.DataFrame(),
                'returns_plot': None
            }
            
            # Get performance data for each portfolio
            for portfolio_id in portfolio_ids:
                portfolio = self.get_portfolio(portfolio_id)
                if portfolio:
                    performance = self.get_portfolio_performance(portfolio_id)
                    if performance:
                        comparison['portfolios'].append({
                            'id': portfolio_id,
                            'name': portfolio['name'],
                            'performance': performance
                        })
            
            if not comparison['portfolios']:
                return None
            
            # Create comparison metrics DataFrame
            metrics_data = []
            for p in comparison['portfolios']:
                metrics = p['performance']['metrics']
                metrics_data.append({
                    'Portfolio': p['name'],
                    'Total Return': metrics['total_return'],
                    'Annualized Return': metrics['annualized_return'],
                    'Volatility': metrics['volatility'],
                    'Sharpe Ratio': metrics['sharpe_ratio'],
                    'Max Drawdown': metrics['max_drawdown'],
                    'Sortino Ratio': metrics['sortino_ratio'],
                    'Calmar Ratio': metrics['calmar_ratio'],
                    'Beta': metrics['beta'],
                    'Alpha': metrics['alpha']
                })
            
            comparison['metrics'] = pd.DataFrame(metrics_data)
            
            # Calculate correlation matrix
            returns_data = {}
            for p in comparison['portfolios']:
                returns_data[p['name']] = p['performance']['daily_returns']
            
            comparison['correlation_matrix'] = pd.DataFrame(returns_data).corr()
            
            # Create returns plot
            fig = go.Figure()
            for p in comparison['portfolios']:
                cumulative_returns = (1 + p['performance']['daily_returns']).cumprod()
                fig.add_trace(go.Scatter(
                    x=cumulative_returns.index,
                    y=cumulative_returns.values,
                    mode='lines',
                    name=p['name']
                ))
            
            fig.update_layout(
                title='Portfolio Returns Comparison',
                xaxis_title='Date',
                yaxis_title='Cumulative Returns',
                hovermode='x unified'
            )
            
            comparison['returns_plot'] = fig
            
            return comparison
            
        except Exception as e:
            print(f"Error comparing portfolios: {str(e)}")
            return None

    def rebalance_portfolio(self, portfolio_id: int, target_allocations: Dict[str, float]) -> bool:
        """Rebalance a portfolio to target allocations"""
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                return False
            
            # Validate target allocations
            if not self._validate_allocations(target_allocations):
                return False
            
            # Update allocations in database
            for ticker, allocation in target_allocations.items():
                if not self.db_manager.add_stock_to_portfolio(portfolio_id, ticker, allocation):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error rebalancing portfolio: {str(e)}")
            return False

    def export_portfolio(self, portfolio_id: int, format: str = 'csv') -> Optional[str]:
        """Export portfolio data to file"""
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                return None
            
            performance = self.get_portfolio_performance(portfolio_id)
            if not performance:
                return None
            
            if format.lower() == 'csv':
                # Create CSV data
                data = []
                for stock in performance['stocks']:
                    data.append({
                        'Ticker': stock['ticker'],
                        'Shares': stock['shares'],
                        'Current Price': stock['current_price'],
                        'Value': stock['value'],
                        'Allocation': stock['allocation'],
                        'Sector': stock['sector']
                    })
                
                df = pd.DataFrame(data)
                filename = f"portfolio_{portfolio['name']}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False)
                return filename
            
            return None
            
        except Exception as e:
            print(f"Error exporting portfolio: {str(e)}")
            return None

    def import_portfolio(self, filename: str, portfolio_name: str) -> Optional[int]:
        """Import portfolio from file"""
        try:
            # Read CSV file
            df = pd.read_csv(filename)
            
            # Create new portfolio
            portfolio_id = self.create_portfolio(portfolio_name)
            if not portfolio_id:
                return None
            
            # Add stocks to portfolio
            for _, row in df.iterrows():
                ticker = row['Ticker']
                allocation = row['Allocation']
                
                # Add stock if it doesn't exist
                if ticker not in self.portfolio:
                    self.add_stock(ticker)
                
                # Add to portfolio
                self.add_stock_to_portfolio(portfolio_id, ticker, allocation)
            
            return portfolio_id
            
        except Exception as e:
            print(f"Error importing portfolio: {str(e)}")
            return None

    # Helper methods for performance calculations
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0
        downside_std = np.sqrt(np.mean(downside_returns**2))
        if downside_std == 0:
            return 0
        return (returns.mean() * 252) / (downside_std * np.sqrt(252))

    def _calculate_calmar_ratio(self, annualized_return: float, max_drawdown: float) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown == 0:
            return 0
        return annualized_return / abs(max_drawdown)

    def _calculate_beta(self, returns: pd.Series) -> float:
        """Calculate portfolio beta"""
        try:
            # Get S&P 500 data for comparison
            spy = yf.Ticker("^GSPC")
            spy_returns = spy.history(period="1y")['Close'].pct_change()
            common_dates = returns.index.intersection(spy_returns.index)
            covariance = returns[common_dates].cov(spy_returns[common_dates])
            variance = spy_returns[common_dates].var()
            return covariance / variance if variance != 0 else 0
        except:
            return 0

    def _calculate_alpha(self, returns: pd.Series, portfolio_return: float) -> float:
        """Calculate portfolio alpha"""
        try:
            # Get risk-free rate (using 10-year Treasury yield as proxy)
            treasury = yf.Ticker("^TNX")
            risk_free_rate = treasury.history(period="1d")['Close'].iloc[-1] / 100
            beta = self._calculate_beta(returns)
            market_return = 0.1  # Assuming 10% market return
            return portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        except:
            return 0

    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)

    def _calculate_cvar(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    def _calculate_tracking_error(self, returns: pd.Series) -> float:
        """Calculate tracking error"""
        try:
            spy = yf.Ticker("^GSPC")
            spy_returns = spy.history(period="1y")['Close'].pct_change()
            common_dates = returns.index.intersection(spy_returns.index)
            return (returns[common_dates] - spy_returns[common_dates]).std() * np.sqrt(252)
        except:
            return 0

    def _validate_allocations(self, allocations: Dict[str, float]) -> bool:
        """Validate that allocations sum to 1.0"""
        return abs(sum(allocations.values()) - 1.0) < 1e-6

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
                # Save to database
                self.db_manager.save_stock(ticker, shares, info)
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
            if ticker in self.historical_data:
                del self.historical_data[ticker]
            # Remove from database
            return self.db_manager.delete_stock(ticker)
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
                # Save to database
                self.db_manager.save_historical_data(ticker, hist.to_dict('index'))
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

    def calculate_trade_ratio(self, stock1_ticker: str, stock2_ticker: str, period: str = "1y") -> tuple:
        """
        Calculate the trade ratio between two stocks based on their closing prices.
        Returns the ratio and a plotly figure.
        """
        try:
            # Get historical data for both stocks
            stock1 = yf.Ticker(stock1_ticker)
            stock2 = yf.Ticker(stock2_ticker)
            
            hist1 = stock1.history(period=period)
            hist2 = stock2.history(period=period)
            
            # Ensure both datasets have the same dates
            common_dates = hist1.index.intersection(hist2.index)
            hist1 = hist1.loc[common_dates]
            hist2 = hist2.loc[common_dates]
            
            # Calculate the trade ratio (how many shares of stock2 you get for 1 share of stock1)
            trade_ratio = hist1['Close'] / hist2['Close']
            
            # Create the plot
            fig = go.Figure()
            
            # Add trade ratio line
            fig.add_trace(go.Scatter(
                x=trade_ratio.index,
                y=trade_ratio.values,
                mode='lines',
                name=f'{stock1_ticker}/{stock2_ticker} Ratio',
                line=dict(color='blue')
            ))
            
            # Add 20-day moving average
            ma20 = trade_ratio.rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=ma20.index,
                y=ma20.values,
                mode='lines',
                name='20-day MA',
                line=dict(color='red', dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                title=f'Trade Ratio: {stock1_ticker} to {stock2_ticker}',
                xaxis_title='Date',
                yaxis_title=f'Ratio ({stock1_ticker}/{stock2_ticker})',
                hovermode='x unified',
                showlegend=True
            )
            
            # Calculate current ratio
            current_ratio = trade_ratio.iloc[-1]
            
            return current_ratio, fig
            
        except Exception as e:
            print(f"Error calculating trade ratio: {str(e)}")
            return None, None 