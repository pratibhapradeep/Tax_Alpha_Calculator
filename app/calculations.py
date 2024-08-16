import requests
import os
import numpy as np
from flask import session

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')


def fetch_stock_data(symbol):
    """
    Fetches the daily time series data for a given stock symbol from Alpha Vantage API.

    Args:
        symbol (str): Stock symbol to fetch data for.

    Returns:
        dict: A dictionary containing time series data or an error message.
    """
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
    """
    Fetches the current prices for the securities in the portfolio.

    Args:
        portfolio (list): List of dictionaries containing 'symbol', 'purchase_price', and 'shares' for each security.

    Returns:
        list: Updated portfolio with current prices included.
    """
    updated_portfolio = []
    for security in portfolio:
        symbol = security['symbol']
        stock_data = fetch_stock_data(symbol)

        if isinstance(stock_data, dict) and "error" not in stock_data:
            recent_date = sorted(stock_data.keys(), reverse=True)[0]
            current_price = float(stock_data[recent_date]['4. close'])
            security['current_price'] = current_price
        else:
            security['current_price'] = None

        updated_portfolio.append(security)

    # Store the updated portfolio in the session
    session['portfolio'] = updated_portfolio

    return updated_portfolio


def monte_carlo_simulation_multi(portfolio, num_simulations=1000, time_horizon=252):
    """
    Runs a Monte Carlo simulation to predict future portfolio returns.

    Args:
        portfolio (list): List of securities with their historical price data.
        num_simulations (int): Number of simulations to run. Default is 1000.
        time_horizon (int): Number of days to simulate. Default is 252 (1 trading year).

    Returns:
        np.ndarray: A 3D numpy array containing the simulation results.
    """
    closing_prices = []
    for stock in portfolio:
        symbol = stock['symbol']
        stock_data = fetch_stock_data(symbol)
        if isinstance(stock_data, dict) and "error" not in stock_data:
            prices = [float(value['4. close']) for date, value in stock_data.items()]
            closing_prices.append(prices)
        else:
            print(f"Invalid stock data for {symbol}, skipping.")
            continue

    if not closing_prices:
        raise ValueError("No valid stock data found for the portfolio.")

    # Convert to numpy array for easier manipulation
    closing_prices = np.array(closing_prices)

    # Calculate log returns
    log_returns = np.diff(np.log(closing_prices), axis=1)

    mean_returns = np.mean(log_returns, axis=1)
    covariance_matrix = np.cov(log_returns)

    # Run Monte Carlo simulations
    simulations = np.zeros((len(portfolio), num_simulations, time_horizon))

    for i in range(num_simulations):
        random_shocks = np.random.multivariate_normal(mean_returns, covariance_matrix, time_horizon)
        for j in range(len(portfolio)):
            simulations[j, i, :] = np.exp(random_shocks[:, j])

    return simulations


def calculate_taxes(data):
    """
    Calculates taxes based on the user's income, investment gains, and losses.

    Args:
        data (dict): Dictionary containing 'income', 'tax_bracket', 'investment_gains', 'investment_losses', and 'cost_basis'.

    Returns:
        dict: Dictionary containing the tax owed and an explanation.
    """
    income = data.get('income', 0)
    tax_bracket = data.get('tax_bracket', 0.2)
    investment_gains = data.get('investment_gains', 0)
    investment_losses = data.get('investment_losses', 0)
    cost_basis = data.get('cost_basis', 0)

    net_investment = investment_gains - investment_losses - cost_basis
    total_taxable_income = income + net_investment
    tax_owed = total_taxable_income * tax_bracket

    explanation = (f"Your income of ${income} and net investment of ${net_investment} "
                   f"result in a total taxable income of ${total_taxable_income}. "
                   f"At a tax bracket of {tax_bracket * 100}%, your tax owed is ${tax_owed}.")

    return {
        "income": income,
        "tax_bracket": tax_bracket,
        "investment_gains": investment_gains,
        "investment_losses": investment_losses,
        "cost_basis": cost_basis,
        "net_investment": net_investment,
        "tax_owed": tax_owed,
        "explanation": explanation
    }


from scipy.optimize import minimize


def optimize_portfolio(portfolio):
    """
    Optimizes the portfolio allocation to maximize returns and minimize risk.

    Args:
        portfolio (list): List of securities in the portfolio.

    Returns:
        tuple: Optimal weights for each security, expected portfolio return, portfolio risk, and Sharpe ratio.
    """
    num_stocks = len(portfolio)
    simulations = monte_carlo_simulation_multi(portfolio)

    # Expected returns and covariance matrix
    expected_returns = simulations.mean(axis=2).mean(axis=1)
    covariance_matrix = np.cov(simulations.mean(axis=2))

    # Objective function: Minimize negative Sharpe ratio
    def negative_sharpe_ratio(weights, expected_returns, covariance_matrix, risk_free_rate=0.01):
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
        return -sharpe_ratio

    # Constraints and bounds for weights
    constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    bounds = tuple((0, 1) for _ in range(num_stocks))

    # Initial guess for weights
    initial_weights = num_stocks * [1. / num_stocks]

    # Optimization
    optimized_result = minimize(negative_sharpe_ratio, initial_weights,
                                args=(expected_returns, covariance_matrix),
                                method='SLSQP', bounds=bounds, constraints=constraints)

    optimal_weights = optimized_result.x
    portfolio_return = np.dot(optimal_weights, expected_returns)
    portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights)))
    sharpe_ratio = (portfolio_return - 0.01) / portfolio_risk

    # Map stock symbols to their optimal weights
    optimal_weights_dict = {portfolio[i]['symbol']: optimal_weights[i] for i in range(num_stocks)}

    return optimal_weights_dict, portfolio_return, portfolio_risk, sharpe_ratio


def enhanced_tax_loss_harvesting(portfolio, tax_bracket=0.2):
    """
    Performs tax loss harvesting to minimize tax liabilities.

    Args:
        portfolio (list): List of securities in the portfolio.
        tax_bracket (float): The user's tax bracket.

    Returns:
        tuple: Recommended sales, total losses, and tax savings.
    """
    # Assume the portfolio contains user-provided current prices
    recommended_sales = []
    total_losses = 0

    # Calculate losses based on purchase prices and user-provided current prices
    for security in portfolio:
        symbol = security.get('symbol')
        purchase_price = security.get('purchase_price')
        current_price = security.get('current_price',
                                     purchase_price)  # Fall back to purchase price if no current price is provided
        shares = security.get('shares')

        loss = (purchase_price - current_price) * shares
        if loss > 0:
            recommended_sales.append({
                "symbol": symbol,
                "loss": loss,
                "shares": shares
            })
            total_losses += loss

    tax_savings = total_losses * tax_bracket

    return recommended_sales, total_losses, tax_savings
