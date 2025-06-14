import streamlit as st
import plotly.graph_objects as go
from portfolio_manager import PortfolioManager
from swot_analyzer import SWOTAnalyzer
import pandas as pd
import json
import base64
from PIL import Image
import io

# King Midas logo and decorative elements
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Custom CSS for King Midas theme with enhanced visuals
st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: #FFD700;
        background-image: linear-gradient(45deg, #1E1E1E 25%, #2D2D2D 25%, #2D2D2D 50%, #1E1E1E 50%, #1E1E1E 75%, #2D2D2D 75%, #2D2D2D 100%);
        background-size: 56.57px 56.57px;
    }
    .stButton>button {
        background-color: #FFD700;
        color: #1E1E1E;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFC800;
        color: #1E1E1E;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(255, 215, 0, 0.3);
    }
    .stSelectbox {
        background-color: #2D2D2D;
        color: #FFD700;
        border: 1px solid #FFD700;
        border-radius: 5px;
    }
    .stMetric {
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #FFD700;
        box-shadow: 0 4px 6px rgba(255, 215, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(255, 215, 0, 0.2);
    }
    .stMetric label {
        color: #FFD700;
        font-size: 1.2em;
    }
    .stMetric div {
        color: #FFD700;
        font-size: 1.5em;
        font-weight: bold;
    }
    .stSubheader {
        color: #FFD700;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stHeader {
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stDataFrame {
        background-color: #2D2D2D;
        color: #FFD700;
        border: 1px solid #FFD700;
        border-radius: 10px;
        padding: 10px;
    }
    .stSuccess {
        background-color: #2D2D2D;
        color: #00FF00;
        border: 1px solid #00FF00;
        border-radius: 5px;
        padding: 10px;
    }
    .stError {
        background-color: #2D2D2D;
        color: #FF0000;
        border: 1px solid #FF0000;
        border-radius: 5px;
        padding: 10px;
    }
    .gold-container {
        background-color: #2D2D2D;
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(255, 215, 0, 0.1);
    }
    .gold-title {
        color: #FFD700;
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .gold-text {
        color: #FFD700;
        text-align: center;
        font-size: 1.1em;
    }
    .trend-up {
        color: #00FF00;
    }
    .trend-down {
        color: #FF0000;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()
if 'swot_analyzer' not in st.session_state:
    st.session_state.swot_analyzer = SWOTAnalyzer()

def create_gold_metric(value, label, trend=None):
    trend_icon = ""
    trend_class = ""
    if trend is not None:
        if trend > 0:
            trend_icon = "↑"
            trend_class = "trend-up"
        elif trend < 0:
            trend_icon = "↓"
            trend_class = "trend-down"
    
    return f"""
        <div class="stMetric">
            <div class="gold-text">{label}</div>
            <div class="gold-text">
                {value}
                <span class="{trend_class}">{trend_icon}</span>
            </div>
        </div>
    """

def main():
    # King Midas themed header with logo
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #FFD700; font-size: 48px; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);'>
                King Midas Portfolio Analysis
            </h1>
            <p style='color: #FFD700; font-size: 18px; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);'>
                Where Every Investment Turns to Gold
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation with themed styling
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <h2 style='color: #FFD700; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);'>Navigation</h2>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.selectbox(
        "",
        ["Portfolio Management", "Portfolio Groups", "Portfolio Analysis", "SWOT Analysis", "Trade Ratio Analysis"]
    )
    
    if page == "Portfolio Management":
        show_portfolio_management()
    elif page == "Portfolio Groups":
        show_portfolio_groups()
    elif page == "Portfolio Analysis":
        show_portfolio_analysis()
    elif page == "SWOT Analysis":
        show_swot_analysis()
    else:
        show_trade_ratio_analysis()

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

def show_portfolio_groups():
    st.header("Portfolio Groups")
    
    # Create new portfolio
    with st.expander("Create New Portfolio"):
        col1, col2 = st.columns(2)
        with col1:
            portfolio_name = st.text_input("Portfolio Name")
        with col2:
            portfolio_description = st.text_input("Portfolio Description")
        
        if st.button("Create Portfolio"):
            if portfolio_name:
                portfolio_id = st.session_state.portfolio_manager.create_portfolio(
                    portfolio_name, portfolio_description
                )
                if portfolio_id:
                    st.success(f"Created portfolio: {portfolio_name}")
                else:
                    st.error("Failed to create portfolio")
            else:
                st.warning("Please enter a portfolio name")

    # Display existing portfolios
    portfolios = st.session_state.portfolio_manager.get_portfolios()
    
    if portfolios:
        for portfolio in portfolios:
            with st.expander(f"{portfolio['name']} ({len(portfolio['stocks'])} stocks)"):
                st.write(portfolio['description'])
                
                # Add stocks to portfolio
                col1, col2 = st.columns(2)
                with col1:
                    available_stocks = [
                        ticker for ticker in st.session_state.portfolio_manager.portfolio.keys()
                        if not any(s['ticker'] == ticker for s in portfolio['stocks'])
                    ]
                    if available_stocks:
                        new_stock = st.selectbox(
                            f"Add stock to {portfolio['name']}",
                            available_stocks,
                            key=f"add_{portfolio['id']}"
                        )
                with col2:
                    allocation = st.number_input(
                        "Allocation",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        step=0.1,
                        key=f"alloc_{portfolio['id']}"
                    )
                
                if st.button("Add Stock", key=f"add_btn_{portfolio['id']}"):
                    if st.session_state.portfolio_manager.add_stock_to_portfolio(
                        portfolio['id'], new_stock, allocation
                    ):
                        st.success(f"Added {new_stock} to {portfolio['name']}")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add stock")
                
                # Display portfolio stocks
                if portfolio['stocks']:
                    st.subheader("Portfolio Stocks")
                    stock_data = []
                    for stock in portfolio['stocks']:
                        ticker = stock['ticker']
                        if ticker in st.session_state.portfolio_manager.portfolio:
                            stock_info = st.session_state.portfolio_manager.portfolio[ticker]
                            stock_data.append({
                                'Ticker': ticker,
                                'Shares': stock_info['shares'],
                                'Current Price': stock_info['info'].get('currentPrice', 0),
                                'Allocation': stock['allocation']
                            })
                    
                    if stock_data:
                        df = pd.DataFrame(stock_data)
                        st.dataframe(df)
                        
                        # Calculate and display portfolio performance
                        performance = st.session_state.portfolio_manager.get_portfolio_performance(portfolio['id'])
                        if performance and performance.get('metrics') and 'total_return' in performance['metrics']:
                            st.subheader("Portfolio Performance")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Value", f"${performance['total_value']:,.2f}")
                            with col2:
                                st.metric("Total Return", f"{performance['metrics']['total_return']*100:.2f}%")
                            with col3:
                                st.metric("Sharpe Ratio", f"{performance['metrics']['sharpe_ratio']:.2f}")
                        else:
                            st.info("Not enough data to calculate portfolio performance metrics yet.")
                        
                        # Remove stock from portfolio
                        stock_to_remove = st.selectbox(
                            "Remove stock",
                            [s['ticker'] for s in portfolio['stocks']],
                            key=f"remove_{portfolio['id']}"
                        )
                        if st.button("Remove Stock", key=f"remove_btn_{portfolio['id']}"):
                            if st.session_state.portfolio_manager.remove_stock_from_portfolio(
                                portfolio['id'], stock_to_remove
                            ):
                                st.success(f"Removed {stock_to_remove} from {portfolio['name']}")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to remove stock")
                
                # Delete portfolio
                if st.button("Delete Portfolio", key=f"delete_{portfolio['id']}"):
                    if st.session_state.portfolio_manager.delete_portfolio(portfolio['id']):
                        st.success(f"Deleted portfolio: {portfolio['name']}")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete portfolio")
    else:
        st.info("No portfolios created yet. Create a new portfolio to get started.")

def show_portfolio_analysis():
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='color: #FFD700; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);'>Portfolio Analysis</h2>
            <p style='color: #FFD700; font-size: 18px; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);'>
                Transform your investments into golden opportunities
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    portfolios = st.session_state.portfolio_manager.get_portfolios()
    
    if not portfolios:
        st.info("Create portfolios first to perform analysis")
        return
    
    # Portfolio comparison
    st.markdown("""
        <div class="gold-container">
            <div class="gold-title">Portfolio Comparison</div>
        </div>
    """, unsafe_allow_html=True)
    
    selected_portfolios = st.multiselect(
        "Select portfolios to compare",
        options=[(p['id'], p['name']) for p in portfolios],
        format_func=lambda x: x[1]
    )
    
    if len(selected_portfolios) >= 2:
        portfolio_ids = [p[0] for p in selected_portfolios]
        comparison = st.session_state.portfolio_manager.compare_portfolios(portfolio_ids)
        
        if comparison:
            # Display comparison metrics in a styled container
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Performance Metrics</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(comparison['metrics'].style.format({
                'Total Return': '{:.2%}',
                'Annualized Return': '{:.2%}',
                'Volatility': '{:.2%}',
                'Max Drawdown': '{:.2%}'
            }))
            
            # Display correlation matrix
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Correlation Matrix</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(comparison['correlation_matrix'].style.format('{:.2f}'))
            
            # Display returns plot
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Returns Comparison</div>
                </div>
            """, unsafe_allow_html=True)
            
            fig = comparison['returns_plot']
            fig.update_layout(
                paper_bgcolor='#2D2D2D',
                plot_bgcolor='#2D2D2D',
                font=dict(color='#FFD700'),
                xaxis=dict(gridcolor='#FFD700', zerolinecolor='#FFD700'),
                yaxis=dict(gridcolor='#FFD700', zerolinecolor='#FFD700')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Individual portfolio analysis
    st.markdown("""
        <div class="gold-container">
            <div class="gold-title">Individual Portfolio Analysis</div>
        </div>
    """, unsafe_allow_html=True)
    
    selected_portfolio = st.selectbox(
        "Select portfolio for detailed analysis",
        options=[(p['id'], p['name']) for p in portfolios],
        format_func=lambda x: x[1]
    )
    
    if selected_portfolio:
        portfolio_id = selected_portfolio[0]
        performance = st.session_state.portfolio_manager.get_portfolio_performance(portfolio_id)
        
        if performance and performance.get('metrics') and 'total_return' in performance['metrics']:
            # Display basic metrics in styled containers
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Portfolio Overview</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(create_gold_metric(
                    f"${performance['total_value']:,.2f}",
                    "Total Value",
                    performance['metrics']['total_return']
                ), unsafe_allow_html=True)
            with col2:
                st.markdown(create_gold_metric(
                    f"{performance['metrics']['total_return']*100:.2f}%",
                    "Total Return",
                    performance['metrics']['total_return']
                ), unsafe_allow_html=True)
            with col3:
                st.markdown(create_gold_metric(
                    f"{performance['metrics']['sharpe_ratio']:.2f}",
                    "Sharpe Ratio",
                    performance['metrics']['sharpe_ratio']
                ), unsafe_allow_html=True)
            
            # Display risk metrics
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Risk Metrics</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(create_gold_metric(
                    f"{performance['risk_metrics']['var_95']*100:.2f}%",
                    "VaR (95%)",
                    -performance['risk_metrics']['var_95']
                ), unsafe_allow_html=True)
            with col2:
                st.markdown(create_gold_metric(
                    f"{performance['risk_metrics']['cvar_95']*100:.2f}%",
                    "CVaR (95%)",
                    -performance['risk_metrics']['cvar_95']
                ), unsafe_allow_html=True)
            with col3:
                st.markdown(create_gold_metric(
                    f"{performance['metrics']['beta']:.2f}",
                    "Beta",
                    performance['metrics']['beta']
                ), unsafe_allow_html=True)
            with col4:
                st.markdown(create_gold_metric(
                    f"{performance['metrics']['alpha']*100:.2f}%",
                    "Alpha",
                    performance['metrics']['alpha']
                ), unsafe_allow_html=True)
            
            # Display sector allocation
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Sector Allocation</div>
                </div>
            """, unsafe_allow_html=True)
            
            sector_data = pd.DataFrame({
                'Sector': list(performance['sector_allocation'].keys()),
                'Value': list(performance['sector_allocation'].values())
            })
            sector_data['Percentage'] = sector_data['Value'] / sector_data['Value'].sum() * 100
            
            fig = go.Figure(data=[go.Pie(
                labels=sector_data['Sector'],
                values=sector_data['Value'],
                hole=.3,
                marker=dict(colors=['#FFD700', '#FFC800', '#FFB800', '#FFA800', '#FF9800'])
            )])
            fig.update_layout(
                title="Sector Allocation",
                paper_bgcolor='#2D2D2D',
                plot_bgcolor='#2D2D2D',
                font=dict(color='#FFD700')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio rebalancing
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Portfolio Rebalancing</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Show Rebalancing Interface"):
                current_allocations = {stock['ticker']: stock['allocation'] 
                                    for stock in performance['stocks']}
                
                new_allocations = {}
                for ticker, current_alloc in current_allocations.items():
                    new_alloc = st.number_input(
                        f"{ticker} allocation",
                        min_value=0.0,
                        max_value=1.0,
                        value=current_alloc,
                        step=0.01
                    )
                    new_allocations[ticker] = new_alloc
                
                if st.button("Rebalance Portfolio"):
                    if st.session_state.portfolio_manager.rebalance_portfolio(
                        portfolio_id, new_allocations
                    ):
                        st.success("Portfolio rebalanced successfully")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to rebalance portfolio")
            
            # Export/Import functionality
            st.markdown("""
                <div class="gold-container">
                    <div class="gold-title">Export/Import</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export Portfolio"):
                    filename = st.session_state.portfolio_manager.export_portfolio(portfolio_id)
                    if filename:
                        st.success(f"Portfolio exported to {filename}")
                    else:
                        st.error("Failed to export portfolio")
            
            with col2:
                uploaded_file = st.file_uploader("Import Portfolio", type=['csv'])
                if uploaded_file:
                    new_portfolio_name = st.text_input("New Portfolio Name")
                    if st.button("Import"):
                        if new_portfolio_name:
                            portfolio_id = st.session_state.portfolio_manager.import_portfolio(
                                uploaded_file.name, new_portfolio_name
                            )
                            if portfolio_id:
                                st.success("Portfolio imported successfully")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to import portfolio")
                        else:
                            st.warning("Please enter a portfolio name")
        else:
            st.info("Not enough data to calculate portfolio performance metrics yet.")

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

def show_trade_ratio_analysis():
    st.header("Trade Ratio Analysis")
    
    # Get portfolio stocks
    portfolio_summary = st.session_state.portfolio_manager.get_portfolio_summary()
    
    if portfolio_summary['total_stocks'] > 0:
        # Select stocks for comparison
        tickers = [stock['ticker'] for stock in portfolio_summary['stocks']]
        
        col1, col2 = st.columns(2)
        with col1:
            stock1 = st.selectbox("Select First Stock", tickers)
        with col2:
            stock2 = st.selectbox("Select Second Stock", [t for t in tickers if t != stock1])
        
        # Time period selection
        period = st.selectbox(
            "Select Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
        if st.button("Calculate Trade Ratio"):
            with st.spinner("Calculating trade ratio..."):
                current_ratio, fig = st.session_state.portfolio_manager.calculate_trade_ratio(
                    stock1, stock2, period
                )
                
                if current_ratio is not None and fig is not None:
                    st.subheader("Current Trade Ratio")
                    st.write(f"1 share of {stock1} = {current_ratio:.4f} shares of {stock2}")
                    
                    st.subheader("Trade Ratio History")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add interpretation
                    st.subheader("Interpretation")
                    st.write(f"""
                    - The blue line shows how many shares of {stock2} you would get for 1 share of {stock1}
                    - The red dashed line is the 20-day moving average
                    - When the ratio is high, {stock1} is relatively expensive compared to {stock2}
                    - When the ratio is low, {stock1} is relatively cheap compared to {stock2}
                    """)
                else:
                    st.error("Error calculating trade ratio. Please try again.")
    else:
        st.info("Add stocks to your portfolio first to perform trade ratio analysis.")

if __name__ == "__main__":
    main() 