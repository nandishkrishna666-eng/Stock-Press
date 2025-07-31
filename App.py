import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import datetime
from fpdf import FPDF
from io import BytesIO
import tempfile
import os
import matplotlib.pyplot as plt

# Set Streamlit config
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")
st.title("📊 Live Stock Market Dashboard")

# Sidebar filters
symbols = st.sidebar.multiselect(
    "Select Stocks",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT"]
)
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

if symbols:
    # Download stock data
    all_data = yf.download(symbols, start=start_date, end=end_date)

    # Flatten multi-index
    all_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in all_data.columns]
    all_data.reset_index(inplace=True)

    st.subheader("📅 Raw Data")
    st.dataframe(all_data.head(), use_container_width=True)

    # Closing Price Chart - Plotly
    st.subheader("📈 Closing Price Trend")
    fig1 = px.line()
    for symbol in symbols:
        fig1.add_scatter(x=all_data['Date'], y=all_data[f'Close_{symbol}'], mode='lines', name=symbol)
    fig1.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Volume Chart - Plotly
    st.subheader("📊 Volume Traded")
    fig2 = px.area()
    for symbol in symbols:
        fig2.add_scatter(x=all_data['Date'], y=all_data[f'Volume_{symbol}'], mode='lines', name=symbol, stackgroup='one')
    fig2.update_layout(title="Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Stats Table
    st.subheader("📌 Stock Statistics")
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

    # CSV Download
    csv = all_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="stock_data.csv", mime="text/csv")

    # PDF Download with Matplotlib
    st.subheader("📄 Download PDF Report with Charts")

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 14)
            self.cell(0, 10, "Stock Market Report", ln=1, align="C")

        def add_stats(self, stats):
         self.set_font("Arial", size=12)
         self.ln(5)
          for _, row in stats.iterrows():
            symbol = row.get("Symbol", "N/A")
            close = f"${row['Latest Close']:.2f}" if pd.notna(row['Latest Close']) else "N/A"
            high = f"${row['Day High']:.2f}" if pd.notna(row['Day High']) else "N/A"
            low = f"${row['Day Low']:.2f}" if pd.notna(row['Day Low']) else "N/A"
            volume = f"{int(row['Volume'])}" if pd.notna(row['Volume']) else "N/A"
            line = f"{symbol} - Close: {close}, High: {high}, Low: {low}, Volume: {volume}"
            self.cell(0, 10, line, ln=1)


    # Save plots with Matplotlib
    with tempfile.TemporaryDirectory() as tmpdir:
        chart1_path = os.path.join(tmpdir, "close_chart.png")
        chart2_path = os.path.join(tmpdir, "volume_chart.png")

        # Matplotlib Close Price
        plt.figure(figsize=(10, 5))
        for symbol in symbols:
            plt.plot(all_data['Date'], all_data[f'Close_{symbol}'], label=symbol)
        plt.title("Closing Price Over Time")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(chart1_path)
        plt.close()

        # Matplotlib Volume
        plt.figure(figsize=(10, 5))
        for symbol in symbols:
            plt.plot(all_data['Date'], all_data[f'Volume_{symbol}'], label=symbol)
        plt.title("Volume Traded")
        plt.xlabel("Date")
        plt.ylabel("Volume")
        plt.legend()
        plt.tight_layout()
        plt.savefig(chart2_path)
        plt.close()

        # Create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.add_stats(stats_df)

        pdf.ln(10)
        pdf.image(chart1_path, w=180)
        pdf.ln(10)
        pdf.image(chart2_path, w=180)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_file = BytesIO(pdf_bytes)

        # Download button
        st.download_button("📄 Download PDF with Charts", data=pdf_file, file_name="stock_report.pdf", mime="application/pdf")

else:
    st.warning("👈 Please select at least one stock to begin.")



