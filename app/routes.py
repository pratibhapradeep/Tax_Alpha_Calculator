import numpy as np
from flask import Blueprint, request, jsonify
from .calculations import calculate_taxes, optimize_portfolio, fetch_current_prices, fetch_stock_data, monte_carlo_simulation

routes = Blueprint('routes', __name__)

@routes.route('/calculate-taxes', methods=['POST'])
def calculate_taxes_route():
    try:
        data = request.json
        result = calculate_taxes(data)
        response_text = result['explanation']
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@routes.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio_route():
    try:
        data = request.json
        result = optimize_portfolio(data)
        if "error" in result:
            return jsonify(result), 400
        response_text = (f"For the stock symbol '{result['symbol']}', the optimal price based on the Monte Carlo simulation "
                         f"is approximately ${result['optimal_price']:.2f}. The expected return mean is ${result['expected_return_mean']:.2f} "
                         f"with a standard deviation of ${result['expected_return_std']:.2f}.")
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@routes.route('/monte-carlo', methods=['POST'])
def monte_carlo_route():
    try:
        data = request.json
        symbol = data.get("symbol")
        stock_data = fetch_stock_data(symbol)

        if "error" in stock_data:
            return jsonify(stock_data), 400

        closing_prices = [float(value['4. close']) for date, value in stock_data.items()]
        simulations = monte_carlo_simulation(closing_prices)

        # Provide a summary of the Monte Carlo simulation
        mean_simulated_price = np.mean(simulations[-1])
        stddev_simulated_price = np.std(simulations[-1])

        response_text = (f"The Monte Carlo simulation for '{symbol}' was successful. "
                         f"After simulating 1000 potential outcomes over a year, "
                         f"the average simulated end price is approximately ${mean_simulated_price:.2f} "
                         f"with a standard deviation of ${stddev_simulated_price:.2f}.")

        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500



@routes.route('/input-portfolio', methods=['POST'])
def input_portfolio_route():
    try:
        portfolio = request.json.get('portfolio', [])
        response_text = f"Your portfolio has been recorded with {len(portfolio)} securities."
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@routes.route('/tax-loss-harvesting', methods=['POST'])
def tax_loss_harvesting_route():
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

        if recommended_sales:
            response_text = (f"Tax Loss Harvesting Summary: You can sell {len(recommended_sales)} securities to realize a total loss of ${total_losses:.2f}. "
                             f"This could save you approximately ${tax_savings:.2f} in taxes based on your tax bracket of {tax_bracket * 100}%.")
        else:
            response_text = "Tax Loss Harvesting Summary: No securities meet the criteria for tax loss harvesting."

        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500
