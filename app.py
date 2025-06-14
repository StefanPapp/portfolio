import streamlit as st
import plotly.graph_objects as go
from portfolio_manager import PortfolioManager
from swot_analyzer import SWOTAnalyzer
import pandas as pd

# Initialize session state
if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()
if 'swot_analyzer' not in st.session_state:
    st.session_state.swot_analyzer = SWOTAnalyzer()

def main():
    st.title("Investment Portfolio Analysis Platform")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Portfolio Management", "SWOT Analysis"]
    )
    
    if page == "Portfolio Management":
        show_portfolio_management()
    else:
        show_swot_analysis()

def show_portfolio_management():
    st.header("Portfolio Management")
    
    # Add new stock
    col1, col2 = st.columns(2)
    with col1:
        new_ticker = st.text_input("Enter Stock Ticker", "").upper()
    with col2:
        shares = st.number_input("Number of Shares", min_value=0.0, value=0.0)
    
    if st.button("Add Stock"):
        if new_ticker:
            if st.session_state.portfolio_manager.add_stock(new_ticker, shares):
                st.success(f"Added {new_ticker} to portfolio")
            else:
                st.error(f"Failed to add {new_ticker}")
    
    # Display portfolio
    st.subheader("Current Portfolio")
    portfolio_summary = st.session_state.portfolio_manager.get_portfolio_summary()
    
    if portfolio_summary['total_stocks'] > 0:
        df = pd.DataFrame(portfolio_summary['stocks'])
        st.dataframe(df)
        
        # Update stock data
        if st.button("Update Stock Data"):
            st.session_state.portfolio_manager.update_stock_data()
            st.success("Portfolio data updated")
    else:
        st.info("No stocks in portfolio. Add some stocks to get started.")

def show_swot_analysis():
    st.header("SWOT Analysis")
    
    # Get portfolio stocks
    portfolio_summary = st.session_state.portfolio_manager.get_portfolio_summary()
    
    if portfolio_summary['total_stocks'] > 0:
        # Select stock for analysis
        tickers = [stock['ticker'] for stock in portfolio_summary['stocks']]
        selected_ticker = st.selectbox("Select Stock for Analysis", tickers)
        
        if st.button("Run SWOT Analysis"):
            with st.spinner("Analyzing..."):
                swot_results = st.session_state.swot_analyzer.analyze_stock(selected_ticker)
                
                # Display SWOT results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Strengths")
                    for strength in swot_results.get('Strengths', []):
                        st.write(f"✅ {strength}")
                    
                    st.subheader("Weaknesses")
                    for weakness in swot_results.get('Weaknesses', []):
                        st.write(f"❌ {weakness}")
                
                with col2:
                    st.subheader("Opportunities")
                    for opportunity in swot_results.get('Opportunities', []):
                        st.write(f"🔍 {opportunity}")
                    
                    st.subheader("Threats")
                    for threat in swot_results.get('Threats', []):
                        st.write(f"⚠️ {threat}")
    else:
        st.info("Add stocks to your portfolio first to perform SWOT analysis.")

if __name__ == "__main__":
    main() 