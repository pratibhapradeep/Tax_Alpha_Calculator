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
    try:
        if request.method == 'POST':
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

            # Debugging output
            print(f"Income: {income}")
            print(f"Tax Bracket: {tax_bracket}")
            print(f"Investment Gains: {investment_gains}")
            print(f"Investment Losses: {investment_losses}")
            print(f"Cost Basis: {cost_basis}")
            print(f"Net Investment: {net_investment}")
            print(f"Tax Owed: {tax_owed}")

            return jsonify({
                "income": income,
                "tax_bracket": tax_bracket,
                "investment_gains": investment_gains,
                "investment_losses": investment_losses,
                "cost_basis": cost_basis,
                "net_investment": net_investment,
                "tax_owed": tax_owed
            }), 200
        else:
            return jsonify({"error": "Invalid request method"}), 405
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500




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

@routes.route('/input-portfolio', methods=['POST'])
def input_portfolio():
    try:
        if request.method == 'POST':
            portfolio = request.json.get('portfolio', [])
            # Here we would typically save the portfolio to a database or session
            # For now, we'll just return it as is for testing purposes
            return jsonify({"portfolio": portfolio}), 200
        else:
            return jsonify({"error": "Invalid request method"}), 405
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@routes.route('/tax-loss-harvesting', methods=['POST'])
def tax_loss_harvesting():
    try:
        data = request.json
        portfolio = data.get('portfolio', [])
        tax_bracket = data.get('tax_bracket', 0.2)

        portfolio = fetch_current_prices(portfolio)

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

        return jsonify({
            "recommended_sales": recommended_sales,
            "total_losses": total_losses,
            "tax_savings": tax_savings
        }), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500