import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import datetime
from fpdf import FPDF
import os

# Configure Streamlit
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")
st.title("📊 Live Stock Market Dashboard")
st.markdown("View real-time stock prices, closing trends, and trading volume.")

# Sidebar Inputs
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT", "GOOGL"]
)
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Fetch data if symbols selected
if symbols:
    all_data = yf.download(symbols, start=start_date, end=end_date)
    all_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in all_data.columns]
    all_data.reset_index(inplace=True)

    st.subheader("📅 Raw Data Preview")
    st.dataframe(all_data.head(), use_container_width=True)

    # Plot closing price
    st.subheader("📈 Closing Price Trend")
    fig1 = px.line()
    for symbol in symbols:
        fig1.add_scatter(x=all_data["Date"], y=all_data[f"Close_{symbol}"], mode='lines', name=symbol)
    fig1.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Plot volume
    st.subheader("📊 Volume Traded")
    fig2 = px.area()
    for symbol in symbols:
        fig2.add_scatter(x=all_data["Date"], y=all_data[f"Volume_{symbol}"], mode='lines', stackgroup='one', name=symbol)
    fig2.update_layout(title="Daily Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Latest Stats
    latest = all_data.iloc[-1]
    stats_data = []
    for symbol in symbols:
        stats_data.append({
            "Symbol": symbol,
            "Latest Close": latest.get(f"Close_{symbol}", float('nan')),
            "Day High": latest.get(f"High_{symbol}", float('nan')),
            "Day Low": latest.get(f"Low_{symbol}", float('nan')),
            "Volume": latest.get(f"Volume_{symbol}", float('nan'))
        })
    stats_df = pd.DataFrame(stats_data)
    st.subheader("📊 Latest Stock Statistics")
    st.dataframe(stats_df, use_container_width=True)

    # Save charts as images
    chart1_path = "closing_trend.png"
    chart2_path = "volume_traded.png"
    fig1.write_image(chart1_path)
    fig2.write_image(chart2_path)

    # Create PDF Report
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "📈 Stock Market Summary Report", ln=1, align="C")
            self.ln(5)

        def add_charts(self, chart_paths):
            for path in chart_paths:
                self.image(path, w=180)
                self.ln(10)

        def add_stock_stats(self, stats):
            self.set_font("Arial", size=12)
            self.ln(5)
            for _, row in stats.iterrows():
                try:
                    symbol = str(row.get("Symbol", "N/A"))
                    close = row.get("Latest Close", None)
                    high = row.get("Day High", None)
                    low = row.get("Day Low", None)
                    volume = row.get("Volume", None)

                    close_str = f"${float(close):.2f}" if pd.notna(close) else "N/A"
                    high_str = f"${float(high):.2f}" if pd.notna(high) else "N/A"
                    low_str = f"${float(low):.2f}" if pd.notna(low) else "N/A"
                    volume_str = f"{int(volume):,}" if pd.notna(volume) else "N/A"

                    line = f"{symbol} - Close: {close_str}, High: {high_str}, Low: {low_str}, Volume: {volume_str}"
                    self.cell(0, 10, line, ln=1)
                except Exception:
                    self.cell(0, 10, f"⚠️ Error parsing stats for {row.get('Symbol', 'N/A')}", ln=1)

    pdf = PDF()
    pdf.add_page()
    pdf.add_charts([chart1_path, chart2_path])
    pdf.add_stock_stats(stats_df)
    pdf_path = "Stock_Report.pdf"
    pdf.output(pdf_path)

    # Download Button
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Download PDF Report", f, file_name="Stock_Report.pdf", mime="application/pdf")

    # Cleanup
    os.remove(chart1_path)
    os.remove(chart2_path)
    os.remove(pdf_path)

else:
    st.warning("👈 Please select at least one stock symbol to view data.")










