import pandas as pd
import requests
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import io
import base64

class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.api_key = "HTS6MW8HZHVH04MK"
        self.base_url = "https://www.alphavantage.co/query"
        self.data = None

    def fetch_data(self):
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": self.symbol,
            "outputsize": "compact",
            "apikey": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        raw_data = response.json()

        if "Time Series (Daily)" not in raw_data:
            raise Exception("API Error or invalid symbol.")

        df = pd.DataFrame(raw_data["Time Series (Daily)"]).T
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        }, inplace=True)

        self.data = df

    def calculate_indicators(self):
        self.fetch_data()
        df = self.data
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = exp1 - exp2
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        self.data = df

    def plot_stock_data(self):
        df = self.data
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name="Close Price", line=dict(color="cyan")
        ))

        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_20"], mode="lines", name="SMA 20", line=dict(dash="dash", color="yellow")
        ))

        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_50"], mode="lines", name="SMA 50", line=dict(dash="dot", color="orange")
        ))

        fig.update_layout(
            title=f"{self.symbol} Stock Analysis",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark"
        )

        return fig
