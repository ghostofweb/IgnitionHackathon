import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from stock_analyzer import StockAnalyzer

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# App layout
app.layout = dbc.Container([
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

@app.callback(
    [Output("stock-chart", "figure"),
     Output("indicators-output", "children")],
    [Input("analyze-button", "n_clicks")],
    [State("stock-input", "value")]
)
def update_chart(n_clicks, symbol):
    if not symbol or not n_clicks:
        return dash.no_update, dash.no_update
    
    try:
        # Create StockAnalyzer instance
        analyzer = StockAnalyzer(symbol)
        analyzer.calculate_indicators()
        
        # Get the plot
        fig = analyzer.plot_stock_data()
        
        # Create indicators summary
        latest_data = analyzer.data.iloc[-1]
        indicators_summary = dbc.Card([
            dbc.CardBody([
                html.H4("Technical Indicators", className="card-title"),
                html.P(f"RSI (14): {latest_data['RSI']:.2f}"),
                html.P(f"MACD: {latest_data['MACD']:.2f}"),
                html.P(f"MACD Signal: {latest_data['MACD_Signal']:.2f}"),
                html.P(f"20-day SMA: ${latest_data['SMA_20']:.2f}"),
                html.P(f"50-day SMA: ${latest_data['SMA_50']:.2f}")
            ])
        ], className="mt-4")
        
        return fig, indicators_summary
    
    except Exception as e:
        return dash.no_update, html.Div(f"Error: {str(e)}")

if __name__ == '__main__':
    app.run_server(debug=True)