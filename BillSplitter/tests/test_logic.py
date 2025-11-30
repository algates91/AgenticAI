import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.split_calculator import SplitCalculatorAgent

class TestSplitCalculator(unittest.TestCase):
    def setUp(self):
        self.agent = SplitCalculatorAgent()

    def test_basic_split(self):
        bill_data = {
            "total_amount": 100.0,
            "shared_costs": [{"description": "Base Plan", "amount": 20.0, "category": "Plan"}],
            "user_charges": [
                {"name": "Alice", "total": 30.0, "items": []},
                {"name": "Bob", "total": 50.0, "items": []}
            ]
        }
        
        result = self.agent.calculate_split(bill_data)
        
        # Shared cost is 20.0 / 2 = 10.0 per person
        # Alice: 30 + 10 = 40
        # Bob: 50 + 10 = 60
        
        self.assertEqual(result.user_splits["Alice"], 40.0)
        self.assertEqual(result.user_splits["Bob"], 60.0)
        self.assertEqual(result.total_bill, 100.0)

    def test_no_shared_costs(self):
        bill_data = {
            "total_amount": 80.0,
            "shared_costs": [],
            "user_charges": [
                {"name": "Alice", "total": 30.0, "items": []},
                {"name": "Bob", "total": 50.0, "items": []}
            ]
        }
        
        result = self.agent.calculate_split(bill_data)
        
        self.assertEqual(result.user_splits["Alice"], 30.0)
        self.assertEqual(result.user_splits["Bob"], 50.0)

if __name__ == '__main__':
    unittest.main()
