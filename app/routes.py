from flask import Blueprint, request, jsonify
import requests
import os
import numpy as np

routes = Blueprint('routes', __name__)

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Global variable to store portfolio
stored_portfolio = None

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

def fetch_current_prices(portfolio):
    updated_portfolio = []
    for security in portfolio:
        symbol = security['symbol']
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        response = requests.get(url)
        data = response.json()

        # Get the most recent closing price
        if "Time Series (Daily)" in data:
            recent_date = sorted(data["Time Series (Daily)"].keys(), reverse=True)[0]
            current_price = float(data["Time Series (Daily)"][recent_date]['4. close'])
            security['current_price'] = current_price
        else:
            security['current_price'] = None  # Handle case where data is not available

        updated_portfolio.append(security)
    return updated_portfolio

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
    global stored_portfolio
    try:
        if not stored_portfolio:
            return jsonify({"message": "Please provide your portfolio first."}), 400

        data = request.json
        income = data.get('income', 0)
        tax_bracket = data.get('tax_bracket', 0.2)
        investment_gains = data.get('investment_gains', 0)
        investment_losses = data.get('investment_losses', 0)
        cost_basis = data.get('cost_basis', 0)

        # Calculate capital gains or losses
        net_investment = investment_gains - investment_losses - cost_basis

        # Calculate taxes owed
        total_taxable_income = income + net_investment
        tax_owed = total_taxable_income * tax_bracket

        message = (
            f"Based on your income of ${income}, tax bracket of {tax_bracket*100}%, "
            f"investment gains of ${investment_gains}, losses of ${investment_losses}, and cost basis of ${cost_basis}, "
            f"your total taxable income is ${total_taxable_income}, resulting in taxes owed of ${tax_owed}."
        )

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while calculating taxes.", "details": str(e)}), 500


@routes.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio():
    global stored_portfolio
    try:
        if not stored_portfolio:
            return jsonify({"message": "Please provide your portfolio first."}), 400

        data = request.json
        symbol = data.get("symbol")

        # Fetch stock data
        stock_data = fetch_stock_data(symbol)

        if "error" in stock_data:
            return jsonify({"message": stock_data["error"]}), 400

        # Get closing prices for Monte Carlo simulation
        closing_prices = [float(value['4. close']) for date, value in stock_data.items()]

        if not closing_prices:
            return jsonify({"message": "No closing prices available for Monte Carlo simulation."}), 400

        # Run Monte Carlo simulation to predict future prices
        simulations = monte_carlo_simulation(closing_prices)

        # Analyze simulations to determine optimal strategy
        expected_returns = simulations.mean(axis=0)
        risk = simulations.std(axis=0)

        # Example optimization logic: Maximize return while minimizing risk
        optimal_index = np.argmax(expected_returns / risk)

        optimal_price = expected_returns[optimal_index]

        message = (
            f"The optimal future price for {symbol} is approximately ${optimal_price:.2f}. "
            f"The expected return over time is around ${np.mean(expected_returns):.2f}, with an associated risk of ${np.mean(risk):.2f}."
        )

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while optimizing the portfolio.", "details": str(e)}), 500


@routes.route('/monte-carlo', methods=['POST'])
def monte_carlo():
    global stored_portfolio
    try:
        if not stored_portfolio:
            return jsonify({"message": "Please provide your portfolio first."}), 400

        data = request.json
        symbol = data.get("symbol")

        # Fetch stock data
        stock_data = fetch_stock_data(symbol)
        closing_prices = [float(value['4. close']) for key, value in stock_data.items()]

        # Run Monte Carlo simulation
        simulations = monte_carlo_simulation(closing_prices)

        message = f"Monte Carlo simulation for {symbol} has been successfully run, with the predicted prices varying over time based on historical data."

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while running Monte Carlo simulation.", "details": str(e)}), 500

@routes.route('/input-portfolio', methods=['POST'])
def input_portfolio():
    global stored_portfolio
    try:
        if request.method == 'POST':
            stored_portfolio = request.json.get('portfolio', [])
            return jsonify({"message": "Portfolio has been successfully stored."}), 200
        else:
            return jsonify({"message": "Invalid request method."}), 405
    except Exception as e:
        return jsonify({"message": "An error occurred while storing the portfolio.", "details": str(e)}), 500

@routes.route('/tax-loss-harvesting', methods=['POST'])
def tax_loss_harvesting():
    global stored_portfolio
    try:
        if not stored_portfolio:
            return jsonify({"message": "Please provide your portfolio first."}), 400

        data = request.json
        tax_bracket = data.get('tax_bracket', 0.2)

        portfolio = fetch_current_prices(stored_portfolio)

        recommended_sales = []
        total_losses = 0

        for security in portfolio:
            symbol = security.get('symbol')
            purchase_price = security.get('purchase_price')
            current_price = security.get('current_price')
            shares = security.get('shares')

            if current_price is not None:
                loss = (purchase_price - current_price) * shares
                if loss > 0:
                    recommended_sales.append({
                        "symbol": symbol,
                        "loss": loss,
                        "shares": shares
                    })
                    total_losses += loss

        tax_savings = total_losses * tax_bracket

        message = (
            f"Based on the current portfolio, you can harvest a total of ${total_losses} in losses, "
            f"which will save you approximately ${tax_savings} in taxes."
        )

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while performing tax-loss harvesting.", "details": str(e)}), 500
