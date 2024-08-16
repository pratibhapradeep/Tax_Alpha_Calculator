Tax Alpha Calculator API


Overview
The Tax Alpha Calculator API provides backend services for tax calculation, portfolio optimization, Monte Carlo simulations, and enhanced tax loss harvesting. The API is designed to integrate financial data fetched from the Alpha Vantage API and provide insightful financial planning and tax-saving strategies.


Table of Contents
1. Setup
2. API Endpoints
  - Input Portfolio
  - Calculate Taxes
  - Optimize Portfolio
  - Monte Carlo Simulation
  - Tax Loss Harvesting
3. Session Management
4. Testing


Setup
Prerequisites (add to requirements.txt)
1. Python 3.6+
2. Flask
3. Alpha Vantage API Key


Installation

1. Clone the Repository:
git clone https://github.com/your-username/tax-alpha-calculator.git
cd tax-alpha-calculator

2. Set up a Virtual Environment:
python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies:
pip install -r requirements.txt

4. Set Environment Variables:
In venv:
ALPHA_VANTAGE_API_KEY=your_api_key_here
FLASK_SECRET_KEY='your_secret_key_here'

5.Run the Application:
flask run


API Endpoints
1. Input Portfolio (POST)
URL: /input-portfolio
Description: Stores the user's portfolio in the session for subsequent API calls.
Request Body:
{
  "portfolio": [
    {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
    {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
  ]
}
Response:
{
  "message": "Your portfolio has been recorded with 2 securities."
}
Example using curl:
curl -c cookies.txt -X POST http://127.0.0.1:5000/input-portfolio -H "Content-Type: application/json" -d '{
  "portfolio": [
    {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
    {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
  ]
}'

2. Calculate Taxes (POST)
URL: /calculate-taxes
Description: Calculates taxes based on provided financial information.
Request Body:
{
  "income": 50000,
  "tax_bracket": 0.2,
  "investment_gains": 10000,
  "investment_losses": 2000,
  "cost_basis": 5000
}
Response:
{
  "message": "Your income of $50000 and net investment of $3000 result in a total taxable income of $53000. At a tax bracket of 20.0%, your tax owed is $10600.0."
}
Example using curl:
curl -b cookies.txt -X POST http://127.0.0.1:5000/calculate-taxes -H "Content-Type: application/json" -d '{
  "income": 50000,
  "tax_bracket": 0.2,
  "investment_gains": 10000,
  "investment_losses": 2000,
  "cost_basis": 5000
}'

3. Optimize Portfolio (POST)
URL: /optimize-portfolio
Description: Optimizes the portfolio stored in the session for maximum returns and minimal risk.
Request Body: No additional data required; uses the portfolio stored in the session.
Response:
{
  "message": "After analyzing your portfolio, the optimal allocation to maximize returns while minimizing risk is: AAPL: 60.00%, MSFT: 40.00%. The expected return of the optimized portfolio is 8.00%, with a risk (standard deviation) of 12.00%. The Sharpe ratio, which indicates the risk-adjusted return, is 0.67."
}
Example using curl:
curl -b cookies.txt -X POST http://127.0.0.1:5000/optimize-portfolio

4. Monte Carlo Simulation (POST)
URL: /monte-carlo
Description: Performs Monte Carlo simulation to predict future portfolio performance.
Request Body: No additional data required; uses the portfolio stored in the session.
Response:
{
  "message": "The Monte Carlo simulation for your portfolio was successful. Here is a summary of the expected performance for your portfolio: For AAPL: 1. Expected annual return: 8.00%. 2. Expected risk (standard deviation): 12.00%. This means that while you can expect an average return of 8.00% over the year, the value of AAPL could fluctuate by approximately 12.00%."
}
Example using curl:
curl -b cookies.txt -X POST http://127.0.0.1:5000/monte-carlo

5. Tax Loss Harvesting (POST)
URL: /tax-loss-harvesting
Description: Recommends which securities to sell to realize losses and reduce taxes.
Request Body: No additional data required; uses the portfolio stored in the session.
Response:
{
  "message": "Tax Loss Harvesting Summary: You can sell 1 security to realize a total loss of $500.00. This could save you approximately $100.00 in taxes based on your tax bracket of 20.0%."
}
Example using curl:
curl -b cookies.txt -X POST http://127.0.0.1:5000/tax-loss-harvesting


Session Management
The application uses Flask sessions to store the user’s portfolio between requests. This allows for a more seamless and stateful interaction with the API. The portfolio is stored server-side, and session cookies are used to maintain continuity between API calls.

Managing Sessions with curl
To manage sessions across multiple API calls using curl, use the -c option to store cookies and the -b option to send stored cookies:

Store Cookies:
curl -c cookies.txt -X POST http://127.0.0.1:5000/input-portfolio -H "Content-Type: application/json" -d '{
  "portfolio": [
    {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
    {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
  ]
}'

Send Stored Cookies:
curl -b cookies.txt -X POST http://127.0.0.1:5000/optimize-portfolio


Testing
To run the unit tests, execute:
python -m unittest discover


License
This project is licensed under the MIT License.