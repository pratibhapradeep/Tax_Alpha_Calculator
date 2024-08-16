import numpy as np
import os
import requests
from flask import Blueprint, request, jsonify, session

from .calculations import (
    calculate_taxes,
    optimize_portfolio,
    fetch_current_prices,
    monte_carlo_simulation_multi,
    enhanced_tax_loss_harvesting
)

routes = Blueprint('routes', __name__)


@routes.route('/calculate-taxes', methods=['POST'])
def calculate_taxes_route():
    """
    Calculate taxes based on the provided income and investment data.

    Expected JSON data:
    {
        "income": float,
        "tax_bracket": float,
        "investment_gains": float,
        "investment_losses": float,
        "cost_basis": float
    }

    Returns:
        JSON response with a message explaining the tax calculation.
    """
    try:
        data = request.json
        result = calculate_taxes(data)
        response_text = result['explanation']
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@routes.route('/input-portfolio', methods=['POST'])
def input_portfolio_route():
    """
    Record the user's portfolio data and store it in the session.

    Expected JSON data:
    {
        "portfolio": [
            {"symbol": "str", "purchase_price": float, "shares": int}
        ]
    }

    Returns:
        JSON response confirming that the portfolio has been recorded.
    """
    try:
        portfolio = request.json.get('portfolio', [])
        session['portfolio'] = portfolio  # Store portfolio in session
        print(f"Stored portfolio: {session['portfolio']}")  # Debugging
        response_text = f"Your portfolio has been recorded with {len(portfolio)} securities."
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@routes.route('/optimize-portfolio', methods=['POST'])
def optimize_portfolio_route():
    """
    Optimize the user's portfolio to maximize returns while minimizing risk.

    Uses the portfolio data stored in the session.

    Returns:
        JSON response with the optimized portfolio allocation and performance metrics.
    """
    try:
        portfolio = session.get('portfolio')  # Retrieve portfolio from session
        print(f"Retrieved portfolio: {portfolio}")  # Debugging
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
    """
    Perform a Monte Carlo simulation to predict the future performance of the portfolio.

    Uses the portfolio data stored in the session.

    Returns:
        JSON response with the results of the Monte Carlo simulation.
    """
    try:
        portfolio = session.get("portfolio", [])  # Retrieve from session

        # Perform Monte Carlo simulation for the entire portfolio
        simulations = monte_carlo_simulation_multi(portfolio)

        # Calculate summary statistics
        portfolio_expected_returns = simulations.mean(axis=2).mean(axis=1)
        portfolio_risk = np.std(simulations.mean(axis=2), axis=1)

        # Generate a user-friendly summary
        response_text = "The Monte Carlo simulation for your portfolio was successful."
        response_text += "Here is a summary of the expected performance for your portfolio:"

        for i, security in enumerate(portfolio):
            symbol = security.get('symbol')
            expected_return = portfolio_expected_returns[i] * 100  # Convert to percentage
            risk = portfolio_risk[i] * 100  # Convert to percentage

            response_text += (
                f"For {symbol}:"
                f"1. Expected annual return: {expected_return:.2f}%."
                f"2. Expected risk (standard deviation): {risk:.2f}%."
                f"This means that while you can expect an average return of {expected_return:.2f}% over the year, "
                f"the value of {symbol} could fluctuate by approximately {risk:.2f}%."
            )

        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@routes.route('/tax-loss-harvesting', methods=['POST'])
def tax_loss_harvesting_route():
    """
    Perform tax loss harvesting on the user's portfolio to minimize tax liabilities.

    Uses the portfolio data stored in the session.

    Returns:
        JSON response with a summary of the tax loss harvesting results.
    """
    try:
        portfolio = session.get('portfolio', [])  # Retrieve from session
        tax_bracket = request.json.get('tax_bracket', 0.2)

        # Use the enhanced tax loss harvesting logic
        recommended_sales, total_losses, tax_savings = enhanced_tax_loss_harvesting(portfolio, tax_bracket)

        if recommended_sales:
            response_text = (
                f"Tax Loss Harvesting Summary: You can sell {len(recommended_sales)} securities to realize a total loss of ${total_losses:.2f}. "
                f"This could save you approximately ${tax_savings:.2f} in taxes based on your tax bracket of {tax_bracket * 100}%.")
        else:
            response_text = "Tax Loss Harvesting Summary: No securities meet the criteria for tax loss harvesting."

        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


