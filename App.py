import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# Set page configuration
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")

st.title("📊 Live Stock Market Dashboard")
st.markdown("View real-time stock prices, closing trends, and trading volume.")

# Sidebar input
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT", "GOOGL"]
)

start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Fetch and display data
if symbols:
    all_data = yf.download(symbols, start=start_date, end=end_date)

    # Flatten multi-index columns
    all_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in all_data.columns]
    all_data.reset_index(inplace=True)

    st.subheader("📅 Raw Data Preview")
    st.dataframe(all_data.head(), use_container_width=True)

    # Closing Price Trend
    st.subheader("📈 Closing Price Trend")
    fig1 = px.line()
    for symbol in symbols:
        fig1.add_scatter(
            x=all_data['Date'],
            y=all_data[f'Close_{symbol}'],
            mode='lines',
            name=symbol
        )
    fig1.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Volume Traded
    st.subheader("📊 Volume Traded")
    fig2 = px.area()
    for symbol in symbols:
        fig2.add_scatter(
            x=all_data['Date'],
            y=all_data[f'Volume_{symbol}'],
            mode='lines',
            stackgroup='one',
            name=symbol
        )
    fig2.update_layout(title="Daily Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Key Stats Table (latest available values)
    st.subheader("📌 Latest Stock Statistics")
    stats_data = []
    for symbol in symbols:
        latest = all_data.iloc[-1]
        stats_data.append({
            "Symbol": symbol,
            "Latest Close": latest[f"Close_{symbol}"],
            "Day High": latest[f"High_{symbol}"],
            "Day Low": latest[f"Low_{symbol}"],
            "Volume": latest[f"Volume_{symbol}"]
        })
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True)

    # Moving Averages
    st.subheader("📉 Moving Averages (SMA 20 & 50)")
    for symbol in symbols:
        df = all_data[["Date", f"Close_{symbol}"]].copy()
        df["SMA20"] = df[f"Close_{symbol}"].rolling(window=20).mean()
        df["SMA50"] = df[f"Close_{symbol}"].rolling(window=50).mean()

        fig_ma = px.line(df, x="Date", y=[f"Close_{symbol}", "SMA20", "SMA50"],
                         labels={"value": "Price", "variable": "Type"},
                         title=f"{symbol} - Moving Averages")
        st.plotly_chart(fig_ma, use_container_width=True)

    # Candlestick Charts
    st.subheader("🕯️ Candlestick Charts")
    for symbol in symbols:
        df_candle = yf.download(symbol, start=start_date, end=end_date)
        fig_candle = go.Figure(data=[go.Candlestick(
            x=df_candle.index,
            open=df_candle['Open'],
            high=df_candle['High'],
            low=df_candle['Low'],
            close=df_candle['Close']
        )])
        fig_candle.update_layout(title=f'{symbol} Candlestick Chart', xaxis_title='Date', yaxis_title='Price (USD)')
        st.plotly_chart(fig_candle, use_container_width=True)

    # Option to download data
    st.subheader("📥 Download Data")
    csv = all_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Combined Data as CSV",
        data=csv,
        file_name='stock_data.csv',
        mime='text/csv',
    )

else:
    st.warning("👈 Please select at least one stock symbol to view data.")







