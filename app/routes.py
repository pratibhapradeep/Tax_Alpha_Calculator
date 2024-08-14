from flask import Blueprint, request, jsonify
import requests
import os
import numpy as np

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


def monte_carlo_simulation(closing_prices, num_simulations=1000, time_horizon=252):
    # Convert closing_prices to a numpy array
    closing_prices = np.array(closing_prices)

    # Calculate log returns using numpy
    log_returns = np.diff(np.log(closing_prices))

    mean = log_returns.mean()
    variance = log_returns.var()
    drift = mean - (0.5 * variance)
    stddev = log_returns.std()

    # Create an array to store the simulations
    simulations = np.zeros((time_horizon, num_simulations))
    simulations[0] = closing_prices[-1]
    for t in range(1, time_horizon):
        random_shocks = np.random.normal(drift, stddev, num_simulations)
        simulations[t] = simulations[t - 1] * np.exp(random_shocks)

    return simulations


@routes.route('/calculate-taxes', methods=['POST'])
def calculate_taxes():
    if request.method == 'POST':
        data = request.json
        income = data.get('income', 0)
        investment_gains = data.get('investment_gains', 0)
        investment_losses = data.get('investment_losses', 0)

        # Placeholder tax calculation logic
        # Example: Basic flat tax rate for simplicity
        tax_rate = 0.2
        total_taxable_income = income + investment_gains - investment_losses
        tax_owed = total_taxable_income * tax_rate

        return jsonify({
            "income": income,
            "investment_gains": investment_gains,
            "investment_losses": investment_losses,
            "tax_owed": tax_owed
        }), 200
    else:
        return jsonify({"error": "Invalid request method"}), 405


@routes.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio():
    try:
        if request.method == 'POST':
            data = request.json
            symbol = data.get("symbol")

            # Fetch stock data
            stock_data = fetch_stock_data(symbol)

            if "error" in stock_data:
                return jsonify(stock_data), 400

            closing_prices = []
            for date, value in stock_data.items():
                try:
                    closing_price = float(value['4. close'])
                    closing_prices.append(closing_price)
                except KeyError as e:
                    print(f"KeyError: {e} - Skipping this entry")

            if closing_prices:
                average_price = sum(closing_prices) / len(closing_prices)
            else:
                average_price = None

            return jsonify({
                "symbol": symbol,
                "average_price": average_price,
                "stock_data": stock_data
            }), 200
        else:
            return jsonify({"error": "Invalid request method"}), 405
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@routes.route('/monte-carlo', methods=['POST'])
def monte_carlo():
    try:
        if request.method == 'POST':
            data = request.json
            symbol = data.get("symbol")

            # Fetch stock data
            stock_data = fetch_stock_data(symbol)
            closing_prices = [float(value['4. close']) for key, value in stock_data.items()]

            # Run Monte Carlo simulation
            simulations = monte_carlo_simulation(closing_prices)

            return jsonify({"simulations": simulations.tolist()}), 200
        else:
            return jsonify({"error": "Invalid request method"}), 405
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500
