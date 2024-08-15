import numpy as np
from flask import Blueprint, request, jsonify
from .calculations import calculate_taxes, optimize_portfolio, fetch_current_prices, fetch_stock_data, monte_carlo_simulation_multi

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
        portfolio = data.get('portfolio')
        if not portfolio:
            return jsonify({"error": "No portfolio data provided"}), 400

        # Perform portfolio optimization
        optimal_weights, expected_portfolio_return, portfolio_risk, sharpe_ratio = optimize_portfolio(portfolio)

        # Create a user-friendly explanation
        response_text = (
            f"After analyzing your portfolio, the optimal allocation to maximize returns while minimizing risk is:"
            f"{', '.join([f'{symbol}: {weight:.2%}' for symbol, weight in optimal_weights.items()])}."
            f"The expected return of the optimized portfolio is {expected_portfolio_return:.2%}, "
            f"with a risk (standard deviation) of {portfolio_risk:.2%}."
            f"The Sharpe ratio, which indicates the risk-adjusted return, is {sharpe_ratio:.2f}."
        )

        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@routes.route('/monte-carlo', methods=['POST'])
def monte_carlo_route():
    try:
        data = request.json
        portfolio = data.get("portfolio", [])

        # Perform Monte Carlo simulation for the entire portfolio
        simulations = monte_carlo_simulation_multi(portfolio)

        # Calculate some summary statistics to return
        portfolio_expected_returns = simulations.mean(axis=2).mean(axis=1)
        portfolio_risk = np.std(simulations.mean(axis=2), axis=1)

        # Generate a user-friendly summary
        response_text = (f"The Monte Carlo simulation for your portfolio was successful. "
                         f"Expected returns for your portfolio stocks are approximately {portfolio_expected_returns.tolist()}, "
                         f"with associated risks (standard deviation) of {portfolio_risk.tolist()}.")

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
