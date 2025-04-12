from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Replace with your Alpha Vantage API Key
API_KEY = "your_api_key_here"
BASE_URL = "https://www.alphavantage.co/query"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    stock_symbol = request.form.get("stock_symbol")
    if not stock_symbol:
        return "Please provide a stock symbol.", 400

    # Fetch stock data
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": stock_symbol,
        "interval": "5min",
        "apikey": API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Time Series (5min)" not in data:
        return f"Error fetching data for {stock_symbol}: {data.get('Note', 'Invalid API response')}", 400

    # Parse stock data
    time_series = data["Time Series (5min)"]
    latest_time = list(time_series.keys())[0]
    latest_data = time_series[latest_time]
    stock_info = {
        "symbol": stock_symbol.upper(),
        "latest_time": latest_time,
        "open": latest_data["1. open"],
        "high": latest_data["2. high"],
        "low": latest_data["3. low"],
        "close": latest_data["4. close"],
        "volume": latest_data["5. volume"],
    }

    return render_template('analysis.html', stock_info=stock_info)

if __name__ == '__main__':
    app.run(debug=True)
