from flask import Flask, render_template, request, redirect
import requests
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from analyser import StockAnalyzer  # Your custom class for calculating indicators

# Create the Flask server instance.
# Since your HTML files are in the root, set template_folder and static_folder to "."
server = Flask(__name__, template_folder=".", static_folder=".")

# Constant for Alpha Vantage API
BASE_URL = "https://www.alphavantage.co/query"

# ---------------------------------------------
# Flask Routes for HTML Pages
# ---------------------------------------------

@server.route('/')
def home():
    # Renders the landing page (index.html)
    return render_template('index.html')


@server.route('/analysis', methods=['POST'])
def analyze():
    stock_symbol = request.form.get("stock_symbol")
    if not stock_symbol:
        return "Please provide a stock symbol.", 400

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": stock_symbol,
        "interval": "5min",
        "apikey": "HTS6MW8HZHVH04MK",
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Time Series (5min)" not in data:
        err = data.get("Note", data.get("Error Message", "Invalid API response"))
        return f"Error fetching data: {err}", 400

    ts = data["Time Series (5min)"]
    latest_time = list(ts.keys())[0]
    latest_data = ts[latest_time]
    stock_info = {
        "symbol": stock_symbol.upper(),
        "latest_time": latest_time,
        "open": latest_data["1. open"],
        "high": latest_data["2. high"],
        "low": latest_data["3. low"],
        "close": latest_data["4. close"],
        "volume": latest_data["5. volume"]
    }

    return render_template('analysis.html', stock_info=stock_info)


@server.route('/goto-dashboard')
def goto_dashboard():
    # Redirect to the interactive Dash dashboard
    return redirect('/dashboard/')

# ---------------------------------------------
# Dash App Configuration (Mounted at /dashboard/)
# ---------------------------------------------
dash_app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dashboard/',
    external_stylesheets=[dbc.themes.DARKLY]
)

dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Stock Market Analyzer", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="stock-input", placeholder="Enter stock symbol (e.g., AAPL)", type="text"),
            dbc.Button("Analyze", id="analyze-button", color="primary", className="mt-2")
        ], width={"size": 6, "offset": 3})
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="stock-chart"),
            html.Div(id="indicators-output")
        ], width=12)
    ])
], fluid=True)

@dash_app.callback(
    [Output("stock-chart", "figure"),
     Output("indicators-output", "children")],
    [Input("analyze-button", "n_clicks")],
    [State("stock-input", "value")]
)
def update_chart(n_clicks, symbol):
    if not symbol or not n_clicks:
        return dash.no_update, dash.no_update
    try:
        analyzer = StockAnalyzer(symbol)
        analyzer.calculate_indicators()
        fig = analyzer.plot_stock_data()
        latest = analyzer.data.iloc[-1]
        indicators = dbc.Card([
            dbc.CardBody([
                html.H4("Technical Indicators"),
                html.P(f"RSI (14): {latest['RSI']:.2f}"),
                html.P(f"MACD: {latest['MACD']:.2f}"),
                html.P(f"MACD Signal: {latest['MACD_Signal']:.2f}"),
                html.P(f"20-day SMA: ${latest['SMA_20']:.2f}"),
                html.P(f"50-day SMA: ${latest['SMA_50']:.2f}")
            ])
        ], className="mt-4")
        return fig, indicators
    except Exception as e:
        return dash.no_update, html.Div(f"Error: {str(e)}")

# ---------------------------------------------
# Run the App
# ---------------------------------------------
if __name__ == '__main__':
    server.run(debug=True)
