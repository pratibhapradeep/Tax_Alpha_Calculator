import unittest
from unittest.mock import patch
from flask import Flask
from app.routes import routes
import numpy as np

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mock_secret_key'  # Mock secret key
        self.client = self.app.test_client()

        with self.app.app_context():
            self.app.register_blueprint(routes)

    @patch('app.calculations.fetch_stock_data')
    def test_calculate_taxes(self, mock_fetch_stock_data):
        mock_fetch_stock_data.return_value = {
            "2024-08-15": {
                "4. close": "200.00"
            }
        }

        self.client.post('/input-portfolio', json={
            "portfolio": [
                {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
                {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
            ],
            "income": 100000,
            "tax_bracket": 0.3,
            "investment_gains": 20000,
            "investment_losses": 5000,
            "cost_basis": 15000
        })

        response = self.client.post('/calculate-taxes')
        self.assertEqual(response.status_code, 200)

    @patch('app.routes.optimize_portfolio')
    def test_optimize_portfolio(self, mock_optimize_portfolio):
        # Mock the response of optimize_portfolio
        mock_optimize_portfolio.return_value = (
            {'AAPL': 0.5, 'MSFT': 0.5},  # optimal_weights
            0.1,  # expected_portfolio_return
            0.05,  # portfolio_risk
            1.2  # sharpe_ratio
        )

        # Input portfolio data into session
        self.client.post('/input-portfolio', json={
            "portfolio": [
                {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
                {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
            ],
            "income": 100000,
            "tax_bracket": 0.3,
            "investment_gains": 20000,
            "investment_losses": 5000,
            "cost_basis": 15000
        })

        # Test the optimize-portfolio route
        response = self.client.post('/optimize-portfolio')
        self.assertEqual(response.status_code, 200)

    @patch('app.routes.monte_carlo_simulation_multi')
    def test_monte_carlo(self, mock_monte_carlo_simulation_multi):
        # Mock the response of monte_carlo_simulation_multi
        mock_monte_carlo_simulation_multi.return_value = np.array(
            [[[1.1, 1.2], [1.1, 1.2]], [[1.05, 1.06], [1.05, 1.06]]])

        # Input portfolio data into session
        self.client.post('/input-portfolio', json={
            "portfolio": [
                {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
                {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
            ],
            "income": 100000,
            "tax_bracket": 0.3,
            "investment_gains": 20000,
            "investment_losses": 5000,
            "cost_basis": 15000
        })

        # Test the monte-carlo route
        response = self.client.post('/monte-carlo')
        self.assertEqual(response.status_code, 200)

    @patch('app.calculations.fetch_stock_data')
    def test_tax_loss_harvesting(self, mock_fetch_stock_data):
        mock_fetch_stock_data.return_value = {
            "2024-08-15": {
                "4. close": "200.00"
            }
        }

        self.client.post('/input-portfolio', json={
            "portfolio": [
                {"symbol": "AAPL", "purchase_price": 300, "shares": 10},
                {"symbol": "MSFT", "purchase_price": 500, "shares": 5}
            ],
            "income": 100000,
            "tax_bracket": 0.3,
            "investment_gains": 20000,
            "investment_losses": 5000,
            "cost_basis": 15000
        })

        response = self.client.post('/tax-loss-harvesting')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
