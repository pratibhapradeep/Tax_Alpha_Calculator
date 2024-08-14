import unittest
from app import create_app

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_calculate_taxes(self):
        response = self.client.post('/calculate-taxes', json={})
        self.assertEqual(response.status_code, 200)

    def test_optimize_portfolio(self):
        response = self.client.post('/optimize-portfolio', json={})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
