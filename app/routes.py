from flask import Blueprint, request, jsonify
import requests
import os

routes = Blueprint('routes', __name__)

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Time Series (Daily)" in data:
            return data["Time Series (Daily)"]
        else:
            return {"error": "Invalid symbol or data not available"}
    else:
        return {"error": "Failed to fetch data from Alpha Vantage"}

@routes.route('/calculate-taxes', methods=['POST'])
def calculate_taxes():
    data = request.json
    # Implement your tax calculation logic here
    return jsonify({"message": "Tax calculation logic here"})

@routes.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio():
    data = request.json
    symbol = data.get("symbol")
    stock_data = fetch_stock_data(symbol)
    # Implement your portfolio optimization logic here
    return jsonify({"stock_data": stock_data})
