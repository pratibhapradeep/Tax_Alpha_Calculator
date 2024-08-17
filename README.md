# Tax Alpha Calculator

## Overview

The Tax Alpha Calculator is a Python-based Flask application designed to optimize an investment portfolio, calculate taxes, perform Monte Carlo simulations, and execute tax loss harvesting strategies. This application allows users to input their portfolio, optimize it to maximize returns while minimizing risk, and perform tax loss harvesting to minimize tax liabilities. The backend relies on data fetched from the Alpha Vantage API for stock price information.

## Features

- **Input Portfolio:** Record your portfolio, including stock symbols, purchase prices, and the number of shares.
- **Tax Calculation:** Calculate your taxes based on income, investment gains, losses, and cost basis.
- **Portfolio Optimization:** Optimize your portfolio allocation to achieve the best risk-adjusted returns.
- **Monte Carlo Simulation:** Simulate the future performance of your portfolio using the Monte Carlo method.
- **Tax Loss Harvesting:** Identify opportunities to sell securities at a loss to minimize tax liabilities.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Requests
- Numpy
- SciPy

### Installation

1. Clone the repository:
   git clone https://github.com/your-username/tax-alpha-calculator.git
   cd tax-alpha-calculator

2. Set up a virtual environment and install dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

3. Set up the Alpha Vantage API key as an environment variable:
   export ALPHA_VANTAGE_API_KEY="your_api_key_here"

4. Set up the Flask secret key:
   export FLASK_SECRET_KEY="your_secret_key_here"


### Running the Application

1. Start the Flask server:
   flask run

2. The application will be accessible at http://127.0.0.1:5000.


### API Limitations

The Alpha Vantage API allows for a maximum of 25 requests per minute. If you exceed this limit, you may encounter errors such as "No valid stock data found for the portfolio" or "Invalid stock data for [symbol], skipping." These errors indicate that the API did not return the expected data due to the rate limit being exceeded or due to an invalid stock symbol. If this happens, wait a minute before making additional requests or verify the stock symbols you are using.

### API Endpoints

1. POST /input-portfolio:
   1. Input your portfolio and tax-related data. This route stores your portfolio and tax information in the session, so it can be used across multiple routes.
   2. Example:
      curl -b cookies.txt -X POST http://127.0.0.1:5000/input-portfolio -H "Content-Type: application/json" -d '{
      "portfolio": [
       {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
       {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
      ],
      "income": 100000,
      "tax_bracket": 0.2,
      "investment_gains": 10000,
      "investment_losses": 5000,
      "cost_basis": 2000
      }'

2. POST /calculate-taxes:
   1. Calculate taxes based on the provided income and investment data. This route does not require additional inputs if the data has already been provided via /input-portfolio.
   2. Example:
   curl -b cookies.txt -X POST http://127.0.0.1:5000/calculate-taxes

3. POST /optimize-portfolio:
   1. Optimize your portfolio allocation. This route uses the portfolio data stored in the session.
   2. Example:
   curl -b cookies.txt -X POST http://127.0.0.1:5000/optimize-portfolio

4. POST /monte-carlo
   1. Perform a Monte Carlo simulation to predict the future performance of the portfolio. This route uses the portfolio data stored in the session.
   2. Example:
   curl -b cookies.txt -X POST http://127.0.0.1:5000/monte-carlo

5. POST /tax-loss-harvesting
   1. Perform tax loss harvesting on the user's portfolio to minimize tax liabilities. This route uses the portfolio data and tax bracket stored in the session.
   2. Example:
   curl -b cookies.txt -X POST http://127.0.0.1:5000/tax-loss-harvesting


### Code Structure

1. app/: Contains the Flask application code, including routes and calculations.

2. tests/: Contains unit tests to ensure the functionality of the application.

3. requirements.txt: Lists the dependencies required to run the application.

4. .env: Environment variables configuration file.


### Using .gitignore

A .gitignore file is included to prevent sensitive and unnecessary files from being pushed to the repository. This includes:

1. .env: Contains sensitive environment variables like API keys and secret keys.

2. __pycache__/: Python cache files that are generated during execution.

3. .venv/: Virtual environment directory, which contains dependencies and should not be committed.



### Contributing

If you'd like to contribute to the project, please fork the repository, create a new branch, and submit a pull request. Make sure your code follows clean coding principles, including DRY (Don't Repeat Yourself), meaningful variable names, and comprehensive documentation.

