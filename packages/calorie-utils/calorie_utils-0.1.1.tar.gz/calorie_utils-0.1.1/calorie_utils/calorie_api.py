import requests

__version__ = "0.1.0"


def fetch_calorie_data(food_item, quantity_grams):
    """Fetch calorie and macronutrient data dynamically from USDA FoodData Central."""
    API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
    API_KEY = "0glhCUFnJF0DCfy53vfAfBQnbQx6GhxpmFrfofrM"  # Replace with your actual API key

    params = {
        "query": food_item,
        "pageSize": 1,
        "api_key": API_KEY
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "foods" in data and len(data["foods"]) > 0:
            food = data["foods"][0]
            nutrients = {n["nutrientName"].lower(): n["value"] for n in food["foodNutrients"]}

            calories = nutrients.get("energy", 0) * (quantity_grams / 100)
            protein = nutrients.get("protein", 0) * (quantity_grams / 100)
            carbs = nutrients.get("carbohydrate, by difference", 0) * (quantity_grams / 100)
            fats = nutrients.get("total lipid (fat)", 0) * (quantity_grams / 100)

            return {
                "food_item": food_item,
                "quantity": quantity_grams,
                "calories": round(calories, 2),
                "protein": round(protein, 2),
                "carbs": round(carbs, 2),
                "fats": round(fats, 2)
            }

    return {"error": "Food item not found or API request failed"}


# Package metadata for setuptools
__all__ = ["fetch_calorie_data"]
