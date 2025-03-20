import unittest
from calorie_utils.calorie_api import fetch_calorie_data

class TestCalorieUtils(unittest.TestCase):
    def test_fetch_calorie_data(self):
        result = fetch_calorie_data("oatmeal", 100)
        self.assertIn("calories", result)
        self.assertIn("protein", result)
        self.assertIn("carbs", result)
        self.assertIn("fats", result)

if __name__ == '__main__':
    unittest.main()
