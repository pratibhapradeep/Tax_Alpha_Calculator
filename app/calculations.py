import requests
import os
import numpy as np

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

        if "Time Series (Daily)" in data:
            recent_date = sorted(data["Time Series (Daily)"].keys(), reverse=True)[0]
            current_price = float(data["Time Series (Daily)"][recent_date]['4. close'])
            security['current_price'] = current_price
        else:
            security['current_price'] = None

        updated_portfolio.append(security)
    return updated_portfolio

def monte_carlo_simulation(closing_prices, num_simulations=1000, time_horizon=252):
    closing_prices = np.array(closing_prices)
    log_returns = np.diff(np.log(closing_prices))

    mean = log_returns.mean()
    variance = log_returns.var()
    drift = mean - (0.5 * variance)
    stddev = log_returns.std()

    simulations = np.zeros((time_horizon, num_simulations))
    simulations[0] = closing_prices[-1]
    for t in range(1, time_horizon):
        random_shocks = np.random.normal(drift, stddev, num_simulations)
        simulations[t] = simulations[t - 1] * np.exp(random_shocks)

    return simulations

def calculate_taxes(data):
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

def optimize_portfolio(data):
    symbol = data.get("symbol")
    stock_data = fetch_stock_data(symbol)

    if "error" in stock_data:
        return stock_data

    closing_prices = [float(value['4. close']) for date, value in stock_data.items()]
    if not closing_prices:
        return {"error": "No closing prices available for Monte Carlo simulation"}

    simulations = monte_carlo_simulation(closing_prices)
    expected_returns = simulations.mean(axis=0)
    risk = simulations.std(axis=0)
    optimal_index = np.argmax(expected_returns / risk)

    summary = {
        "symbol": symbol,
        "optimal_price": expected_returns[optimal_index],
        "expected_return_mean": np.mean(expected_returns),
        "expected_return_std": np.std(expected_returns),
        "risk_mean": np.mean(risk),
        "risk_std": np.std(risk),
        "sample_simulation": simulations[:, optimal_index][:10].tolist()
    }

    return summary
