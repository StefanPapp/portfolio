import yfinance as yf
import pandas as pd
from typing import Dict, List
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class SWOTAnalyzer:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def analyze_stock(self, ticker: str) -> Dict:
        """
        Perform SWOT analysis on a given stock
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data
            hist = stock.history(period="1y")
            
            # Calculate technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            
            # Calculate volatility
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)
            
            # Perform SWOT analysis
            swot = {
                'Strengths': self._analyze_strengths(info, hist),
                'Weaknesses': self._analyze_weaknesses(info, hist),
                'Opportunities': self._analyze_opportunities(info),
                'Threats': self._analyze_threats(info, volatility)
            }
            
            return swot
            
        except Exception as e:
            print(f"Error analyzing stock {ticker}: {str(e)}")
            return {}

    def _analyze_strengths(self, info: Dict, hist: pd.DataFrame) -> List[str]:
        strengths = []
        
        # Market position
        if info.get('marketCap', 0) > 1e10:  # Large cap
            strengths.append("Strong market position (Large cap company)")
        
        # Profitability
        if info.get('profitMargins', 0) > 0.15:
            strengths.append("High profit margins")
        
        # Growth
        if info.get('revenueGrowth', 0) > 0.1:
            strengths.append("Strong revenue growth")
        
        # Technical strength
        if hist['Close'].iloc[-1] > hist['SMA_20'].iloc[-1] > hist['SMA_50'].iloc[-1]:
            strengths.append("Positive technical trend")
        
        return strengths

    def _analyze_weaknesses(self, info: Dict, hist: pd.DataFrame) -> List[str]:
        weaknesses = []
        
        # Debt
        if info.get('debtToEquity', 0) > 1:
            weaknesses.append("High debt-to-equity ratio")
        
        # Profitability
        if info.get('profitMargins', 0) < 0:
            weaknesses.append("Negative profit margins")
        
        # Technical weakness
        if hist['Close'].iloc[-1] < hist['SMA_20'].iloc[-1] < hist['SMA_50'].iloc[-1]:
            weaknesses.append("Negative technical trend")
        
        return weaknesses

    def _analyze_opportunities(self, info: Dict) -> List[str]:
        opportunities = []
        
        # Industry growth
        if info.get('industry', '').lower() in ['technology', 'healthcare', 'renewable energy']:
            opportunities.append("Operating in high-growth industry")
        
        # Market expansion
        if info.get('country', '') != 'US':
            opportunities.append("International market presence")
        
        return opportunities

    def _analyze_threats(self, info: Dict, volatility: float) -> List[str]:
        threats = []
        
        # Market volatility
        if volatility > 0.3:
            threats.append("High market volatility")
        
        # Competition
        if info.get('sector', '') in ['Technology', 'Consumer Cyclical']:
            threats.append("High competitive pressure")
        
        # Regulatory
        if info.get('sector', '') in ['Healthcare', 'Financial Services']:
            threats.append("Regulatory risks")
        
        return threats 