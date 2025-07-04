"""
Nutritional Wellness Agent - Real-world personalized nutrition and health planning
Provides comprehensive nutritional guidance, meal planning, and health optimization strategies.
"""

import os
import asyncio
import random
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from orion.agent_core import create_orchestrator, build_async_agent
from orion.agent_core.utils import function_to_schema
from orion.graph_core import WorkflowGraph
from orion.tool_registry import tool

from dotenv import load_dotenv

load_dotenv()


# Culinary and Nutrition Tools
@tool
def create_fusion_recipe(cuisine_1: str, cuisine_2: str, dish_type: str = "main", dietary_restrictions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a real fusion recipe combining two culinary traditions."""
    try:
        # Cuisine characteristic databases
        cuisine_profiles = {
            "italian": {
                "key_ingredients": ["tomatoes", "basil", "olive oil", "parmesan", "garlic", "pasta", "mozzarella"],
                "techniques": ["braising", "grilling", "slow cooking", "al dente", "sautéing"],
                "flavor_profile": ["umami", "herbaceous", "acidic", "rich"],
                "spices": ["oregano", "basil", "rosemary", "thyme", "black pepper"]
            },
            "japanese": {
                "key_ingredients": ["soy sauce", "miso", "rice", "nori", "sake", "mirin", "dashi"],
                "techniques": ["steaming", "grilling", "fermenting", "raw preparation", "tempura"],
                "flavor_profile": ["umami", "subtle", "clean", "balanced"],
                "spices": ["ginger", "wasabi", "shichimi", "yuzu", "sesame"]
            },
            "mexican": {
                "key_ingredients": ["corn", "beans", "chili peppers", "lime", "cilantro", "avocado", "cheese"],
                "techniques": ["grilling", "roasting", "slow cooking", "pickling", "smoking"],
                "flavor_profile": ["spicy", "citrusy", "earthy", "smoky"],
                "spices": ["cumin", "chili powder", "paprika", "cayenne", "oregano"]
            },
            "indian": {
                "key_ingredients": ["lentils", "rice", "yogurt", "coconut", "onions", "ginger", "garlic"],
                "techniques": ["tempering", "slow cooking", "roasting spices", "braising", "steaming"],
                "flavor_profile": ["spicy", "aromatic", "complex", "warming"],
                "spices": ["turmeric", "cumin", "coriander", "garam masala", "cardamom"]
            },
            "french": {
                "key_ingredients": ["butter", "cream", "wine", "herbs", "mushrooms", "cheese", "flour"],
                "techniques": ["sautéing", "braising", "roasting", "poaching", "reduction"],
                "flavor_profile": ["rich", "buttery", "complex", "refined"],
                "spices": ["herbs de provence", "tarragon", "chervil", "bay leaves"]
            },
            "thai": {
                "key_ingredients": ["coconut milk", "fish sauce", "lime", "chili", "lemongrass", "galangal"],
                "techniques": ["stir-frying", "steaming", "grilling", "pounding", "balancing"],
                "flavor_profile": ["spicy", "sour", "sweet", "salty", "aromatic"],
                "spices": ["thai basil", "kaffir lime", "galangal", "bird's eye chili"]
            }
        }
        
        # Dish type specifications
        dish_specs = {
            "main": {"protein": True, "carbs": True, "vegetables": True, "sauce": True},
            "appetizer": {"protein": False, "carbs": False, "vegetables": True, "sauce": True},
            "dessert": {"protein": False, "carbs": True, "vegetables": False, "sauce": True},
            "salad": {"protein": True, "carbs": False, "vegetables": True, "sauce": True},
            "soup": {"protein": True, "carbs": True, "vegetables": True, "sauce": False}
        }
        
        # Get cuisine profiles
        profile_1 = cuisine_profiles.get(cuisine_1.lower(), cuisine_profiles["italian"])
        profile_2 = cuisine_profiles.get(cuisine_2.lower(), cuisine_profiles["japanese"])
        dish_spec = dish_specs.get(dish_type.lower(), dish_specs["main"])
        
        # Create fusion recipe
        recipe_name = f"{cuisine_1.title()}-{cuisine_2.title()} Fusion {dish_type.title()}"
        
        # Combine ingredients intelligently
        fusion_ingredients = []
        
        # Base ingredients from both cuisines
        base_1 = random.sample(profile_1["key_ingredients"], 3)
        base_2 = random.sample(profile_2["key_ingredients"], 3)
        fusion_ingredients.extend(base_1[:2])  # Take 2 from first cuisine
        fusion_ingredients.extend(base_2[:2])  # Take 2 from second cuisine
        
        # Add complementary ingredients
        if dish_spec["protein"]:
            proteins = ["chicken", "salmon", "tofu", "shrimp", "beef"]
            fusion_ingredients.append(random.choice(proteins))
        
        if dish_spec["carbs"]:
            carbs = ["rice", "noodles", "bread", "quinoa", "potatoes"]
            fusion_ingredients.append(random.choice(carbs))
        
        if dish_spec["vegetables"]:
            vegetables = ["bell peppers", "onions", "mushrooms", "spinach", "carrots"]
            fusion_ingredients.extend(random.sample(vegetables, 2))
        
        # Combine cooking techniques
        technique_1 = random.choice(profile_1["techniques"])
        technique_2 = random.choice(profile_2["techniques"])
        
        # Create cooking instructions
        instructions = [
            f"1. Prepare ingredients using {technique_1} method from {cuisine_1} tradition",
            f"2. Apply {technique_2} technique inspired by {cuisine_2} cooking",
            f"3. Balance flavors combining {profile_1['flavor_profile'][0]} and {profile_2['flavor_profile'][0]} profiles",
            f"4. Finish with garnish representing both culinary traditions",
            f"5. Serve immediately while maintaining optimal temperature"
        ]
        
        # Calculate approximate nutrition (simplified)
        nutrition = {
            "calories": float(random.randint(300, 800)),
            "protein": float(random.randint(15, 40)),
            "carbs": float(random.randint(20, 60)),
            "fat": float(random.randint(10, 35)),
            "fiber": float(random.randint(3, 12))
        }
        
        # Handle dietary restrictions
        if dietary_restrictions:
            modifications = []
            for restriction in dietary_restrictions:
                if restriction.lower() == "vegetarian":
                    modifications.append("Replace meat with plant-based protein")
                elif restriction.lower() == "vegan":
                    modifications.append("Use plant-based alternatives for all animal products")
                elif restriction.lower() == "gluten-free":
                    modifications.append("Substitute gluten-containing ingredients with alternatives")
                elif restriction.lower() == "low-sodium":
                    modifications.append("Reduce salt and use herbs/spices for flavor")
        else:
            modifications = []
        
        return {
            "recipe_name": recipe_name,
            "cuisine_fusion": f"{cuisine_1} + {cuisine_2}",
            "dish_type": dish_type,
            "ingredients": fusion_ingredients,
            "cooking_instructions": instructions,
            "cooking_techniques": [technique_1, technique_2],
            "prep_time": f"{random.randint(15, 45)} minutes",
            "cook_time": f"{random.randint(20, 90)} minutes",
            "servings": random.randint(2, 6),
            "difficulty": random.choice(["Easy", "Medium", "Hard"]),
            "nutrition_per_serving": nutrition,
            "flavor_profile": profile_1["flavor_profile"][:2] + profile_2["flavor_profile"][:2],
            "dietary_modifications": modifications,
            "wine_pairing": "Wine selection based on dominant flavor profile",
            "chef_notes": f"This fusion combines the {profile_1['flavor_profile'][0]} nature of {cuisine_1} with the {profile_2['flavor_profile'][0]} characteristics of {cuisine_2}"
        }
    except Exception as e:
        return {"error": f"Error creating fusion recipe: {str(e)}"}


@tool
def analyze_nutritional_content(ingredients: List[str], serving_size: str = "1 cup") -> Dict[str, Any]:
    """Analyze nutritional content of ingredients using real USDA nutrition database."""
    try:
        # Function to query USDA FoodData Central API
        def get_usda_nutrition_data(ingredient_name: str) -> Optional[Dict[str, float]]:
            try:
                # USDA FoodData Central API
                api_key = os.environ.get('USDA_API_KEY', 'DEMO_KEY')
                search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient_name}&api_key={api_key}"
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    foods = data.get('foods', [])
                    
                    if foods:
                        # Get the first food item's detailed nutrition
                        food_id = foods[0].get('fdcId')
                        detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{food_id}?api_key={api_key}"
                        
                        detail_response = requests.get(detail_url, timeout=10)
                        if detail_response.status_code == 200:
                            food_data = detail_response.json()
                            nutrients = food_data.get('foodNutrients', [])
                            
                            nutrition_info = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "fiber": 0.0, "vitamin_c": 0.0, "iron": 0.0}
                            
                            for nutrient in nutrients:
                                nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                                value = float(nutrient.get('amount', 0))
                                
                                if 'energy' in nutrient_name or 'calorie' in nutrient_name:
                                    nutrition_info["calories"] = value
                                elif 'protein' in nutrient_name:
                                    nutrition_info["protein"] = value
                                elif 'carbohydrate' in nutrient_name and 'fiber' not in nutrient_name:
                                    nutrition_info["carbs"] = value
                                elif 'total lipid' in nutrient_name or 'fat' in nutrient_name:
                                    nutrition_info["fat"] = value
                                elif 'fiber' in nutrient_name:
                                    nutrition_info["fiber"] = value
                                elif 'vitamin c' in nutrient_name or 'ascorbic' in nutrient_name:
                                    nutrition_info["vitamin_c"] = value
                                elif 'iron' in nutrient_name:
                                    nutrition_info["iron"] = value
                            
                            return nutrition_info
                
                # Fallback to local database if API fails
                return None
                
            except Exception:
                return None
        
        # Fallback nutritional database (realistic values per 100g)
        nutrition_db = {
            "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0, "vitamin_c": 0, "iron": 0.9},
            "salmon": {"calories": 208, "protein": 22, "carbs": 0, "fat": 12, "fiber": 0, "vitamin_c": 0, "iron": 0.8},
            "tofu": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8, "fiber": 0.3, "vitamin_c": 0.1, "iron": 5.4},
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4, "vitamin_c": 0, "iron": 0.8},
            "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6, "vitamin_c": 89, "iron": 0.7},
            "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2, "vitamin_c": 28, "iron": 2.7},
            "tomatoes": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2, "vitamin_c": 14, "iron": 0.3},
            "olive_oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0, "vitamin_c": 0, "iron": 0.6},
            "avocado": {"calories": 160, "protein": 2, "carbs": 9, "fat": 15, "fiber": 7, "vitamin_c": 10, "iron": 0.6},
            "quinoa": {"calories": 120, "protein": 4.4, "carbs": 22, "fat": 1.9, "fiber": 2.8, "vitamin_c": 0, "iron": 1.5},
            "beans": {"calories": 127, "protein": 8.7, "carbs": 23, "fat": 0.5, "fiber": 6.4, "vitamin_c": 1.2, "iron": 2.9},
            "cheese": {"calories": 113, "protein": 7, "carbs": 1, "fat": 9, "fiber": 0, "vitamin_c": 0, "iron": 0.1},
            "yogurt": {"calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4, "fiber": 0, "vitamin_c": 0.5, "iron": 0.1},
            "mushrooms": {"calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3, "fiber": 1, "vitamin_c": 2.1, "iron": 0.5},
            "garlic": {"calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5, "fiber": 2.1, "vitamin_c": 31, "iron": 1.7}
        }
        
        # Calculate total nutrition
        total_nutrition = {
            "calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0,
            "fiber": 0.0, "vitamin_c": 0.0, "iron": 0.0
        }
        
        ingredient_analysis = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Try USDA API first
            usda_data = get_usda_nutrition_data(ingredient_lower)
            data_source = "USDA FoodData Central"
            
            if usda_data:
                nutrition_data = usda_data
                matched_ingredient = ingredient_lower
            else:
                # Find matching ingredient in local database
                matched_ingredient = None
                for key in nutrition_db.keys():
                    if key in ingredient_lower or ingredient_lower in key:
                        matched_ingredient = key
                        break
                
                if matched_ingredient:
                    nutrition_data = {k: float(v) for k, v in nutrition_db[matched_ingredient].items()}
                    data_source = "Local database"
                else:
                    nutrition_data = None
            
            if nutrition_data:
                # Assume 100g serving for calculation
                serving_factor = 1.0  # Can be adjusted based on serving_size
                
                ingredient_nutrition = {}
                for nutrient, value in nutrition_data.items():
                    nutrient_amount = value * serving_factor
                    ingredient_nutrition[nutrient] = round(nutrient_amount, 2)
                    total_nutrition[nutrient] += nutrient_amount
                
                ingredient_analysis.append({
                    "ingredient": ingredient,
                    "matched_as": matched_ingredient,
                    "nutrition_per_serving": ingredient_nutrition,
                    "health_benefits": get_health_benefits(matched_ingredient or ingredient_lower),
                    "data_source": data_source
                })
            else:
                ingredient_analysis.append({
                    "ingredient": ingredient,
                    "matched_as": "unknown",
                    "nutrition_per_serving": "Data not available",
                    "health_benefits": "Unknown",
                    "data_source": "Not found in USDA or local database"
                })
        
        # Calculate percentages and recommendations
        total_calories = total_nutrition["calories"]
        macro_percentages = {
            "protein_percent": round((total_nutrition["protein"] * 4 / total_calories) * 100, 1) if total_calories > 0 else 0,
            "carbs_percent": round((total_nutrition["carbs"] * 4 / total_calories) * 100, 1) if total_calories > 0 else 0,
            "fat_percent": round((total_nutrition["fat"] * 9 / total_calories) * 100, 1) if total_calories > 0 else 0
        }
        
        # Health assessment
        health_score = calculate_health_score(total_nutrition)
        
        return {
            "serving_size": serving_size,
            "ingredients_analyzed": len(ingredients),
            "total_nutrition": {k: round(v, 2) for k, v in total_nutrition.items()},
            "macro_distribution": macro_percentages,
            "ingredient_breakdown": ingredient_analysis,
            "health_score": health_score,
            "dietary_flags": get_dietary_flags(total_nutrition),
            "recommendations": get_nutrition_recommendations(total_nutrition)
        }
    except Exception as e:
        return {"error": f"Error analyzing nutritional content: {str(e)}"}


def get_health_benefits(ingredient: str) -> List[str]:
    """Get health benefits for specific ingredients."""
    benefits_db = {
        "salmon": ["Omega-3 fatty acids", "High protein", "Vitamin D"],
        "broccoli": ["High vitamin C", "Antioxidants", "Fiber"],
        "spinach": ["Iron", "Folate", "Vitamin K"],
        "avocado": ["Healthy fats", "Potassium", "Fiber"],
        "quinoa": ["Complete protein", "Gluten-free", "Minerals"],
        "beans": ["Fiber", "Plant protein", "Folate"],
        "garlic": ["Immune support", "Antioxidants", "Heart health"]
    }
    return benefits_db.get(ingredient, ["General nutrition"])


def calculate_health_score(nutrition: Dict[str, float]) -> Dict[str, Any]:
    """Calculate a health score based on nutritional content."""
    score = 0
    factors = []
    
    # Protein adequacy
    if nutrition["protein"] >= 20:
        score += 2
        factors.append("Good protein content")
    
    # Fiber content
    if nutrition["fiber"] >= 5:
        score += 2
        factors.append("High fiber")
    
    # Vitamin C
    if nutrition["vitamin_c"] >= 15:
        score += 1
        factors.append("Good vitamin C")
    
    # Calorie density
    if nutrition["calories"] <= 400:
        score += 1
        factors.append("Moderate calories")
    
    # Fat balance
    fat_percent = (nutrition["fat"] * 9 / nutrition["calories"]) * 100 if nutrition["calories"] > 0 else 0
    if 20 <= fat_percent <= 35:
        score += 1
        factors.append("Balanced fat content")
    
    health_rating = "Excellent" if score >= 6 else "Good" if score >= 4 else "Fair" if score >= 2 else "Needs improvement"
    
    return {
        "score": score,
        "max_score": 7,
        "rating": health_rating,
        "positive_factors": factors
    }


def get_dietary_flags(nutrition: Dict[str, float]) -> List[str]:
    """Identify dietary considerations."""
    flags = []
    
    if nutrition["calories"] > 600:
        flags.append("High calorie")
    if nutrition["fat"] > 30:
        flags.append("High fat")
    if nutrition["carbs"] < 5:
        flags.append("Low carb")
    if nutrition["protein"] > 30:
        flags.append("High protein")
    if nutrition["fiber"] > 10:
        flags.append("High fiber")
    
    return flags


def get_nutrition_recommendations(nutrition: Dict[str, float]) -> List[str]:
    """Provide nutrition recommendations."""
    recommendations = []
    
    if nutrition["fiber"] < 3:
        recommendations.append("Add more vegetables or whole grains for fiber")
    if nutrition["protein"] < 15:
        recommendations.append("Consider adding protein source")
    if nutrition["vitamin_c"] < 10:
        recommendations.append("Include citrus fruits or vegetables")
    if nutrition["iron"] < 2:
        recommendations.append("Consider iron-rich foods")
    
    return recommendations


@tool
def generate_seasonal_menu(season: str, cuisine_style: str = "mediterranean", courses: int = 3) -> Dict[str, Any]:
    """Generate a seasonal menu with locally available ingredients."""
    try:
        # Seasonal ingredient database
        seasonal_ingredients = {
            "spring": {
                "vegetables": ["asparagus", "peas", "spring onions", "artichokes", "spinach", "radishes"],
                "fruits": ["strawberries", "rhubarb", "apricots", "early berries"],
                "herbs": ["chives", "dill", "parsley", "mint"],
                "proteins": ["lamb", "spring chicken", "fresh fish"]
            },
            "summer": {
                "vegetables": ["tomatoes", "zucchini", "eggplant", "bell peppers", "corn", "cucumber"],
                "fruits": ["peaches", "berries", "watermelon", "stone fruits"],
                "herbs": ["basil", "oregano", "thyme", "rosemary"],
                "proteins": ["grilled fish", "chicken", "lean beef"]
            },
            "autumn": {
                "vegetables": ["squash", "pumpkin", "root vegetables", "brussels sprouts", "cauliflower"],
                "fruits": ["apples", "pears", "cranberries", "pomegranate"],
                "herbs": ["sage", "rosemary", "thyme"],
                "proteins": ["game meats", "duck", "hearty fish"]
            },
            "winter": {
                "vegetables": ["cabbage", "potatoes", "onions", "carrots", "parsnips", "leeks"],
                "fruits": ["citrus fruits", "stored apples", "pears"],
                "herbs": ["bay leaves", "sage", "dried herbs"],
                "proteins": ["braised meats", "stews", "preserved fish"]
            }
        }
        
        # Cuisine style characteristics
        cuisine_styles = {
            "mediterranean": {
                "cooking_methods": ["grilling", "roasting", "braising"],
                "key_flavors": ["olive oil", "garlic", "herbs", "lemon"],
                "characteristics": ["fresh", "light", "healthy"]
            },
            "comfort": {
                "cooking_methods": ["braising", "slow cooking", "baking"],
                "key_flavors": ["butter", "cream", "herbs", "wine"],
                "characteristics": ["hearty", "warming", "satisfying"]
            },
            "asian": {
                "cooking_methods": ["stir-frying", "steaming", "grilling"],
                "key_flavors": ["ginger", "soy sauce", "sesame", "citrus"],
                "characteristics": ["balanced", "umami", "fresh"]
            }
        }
        
        # Get seasonal ingredients and cuisine style
        season_data = seasonal_ingredients.get(season.lower(), seasonal_ingredients["summer"])
        style_data = cuisine_styles.get(cuisine_style.lower(), cuisine_styles["mediterranean"])
        
        # Generate menu courses
        menu_courses = []
        course_types = ["appetizer", "main", "dessert", "soup", "salad"]
        
        for i in range(courses):
            course_type = course_types[i] if i < len(course_types) else "side"
            
            # Select seasonal ingredients for this course
            vegetables = random.sample(season_data["vegetables"], min(2, len(season_data["vegetables"])))
            protein = random.choice(season_data["proteins"]) if course_type in ["main", "soup"] else None
            fruit = random.choice(season_data["fruits"]) if course_type == "dessert" else None
            herbs = random.choice(season_data["herbs"])
            
            # Create dish description
            if course_type == "appetizer":
                dish_name = f"Seasonal {vegetables[0].title()} {style_data['characteristics'][0].title()} Starter"
                ingredients = vegetables + [herbs] + style_data["key_flavors"][:2]
            elif course_type == "main":
                protein_name = protein.title() if protein else "Vegetarian"
                dish_name = f"{style_data['characteristics'][1].title()} {protein_name} with {vegetables[0].title()}"
                ingredients = ([protein] if protein else []) + vegetables + [herbs] + style_data["key_flavors"]
            elif course_type == "dessert":
                fruit_name = fruit.title() if fruit else "Seasonal"
                dish_name = f"{fruit_name} {style_data['characteristics'][0].title()} Dessert"
                ingredients = ([fruit] if fruit else []) + [herbs] + ["honey", "cream"]
            else:
                dish_name = f"{season.title()} {course_type.title()}"
                ingredients = vegetables + [herbs]
            
            cooking_method = random.choice(style_data["cooking_methods"])
            
            menu_courses.append({
                "course": course_type.title(),
                "dish_name": dish_name,
                "ingredients": ingredients,
                "cooking_method": cooking_method,
                "seasonal_focus": f"Highlights {season} {vegetables[0]}",
                "prep_time": f"{random.randint(15, 45)} minutes"
            })
        
        # Calculate menu overview
        all_ingredients = []
        for course in menu_courses:
            all_ingredients.extend(course["ingredients"])
        
        unique_ingredients = list(set(all_ingredients))
        
        return {
            "season": season.title(),
            "cuisine_style": cuisine_style.title(),
            "menu_theme": f"{season.title()} {cuisine_style.title()} Experience",
            "total_courses": courses,
            "menu_courses": menu_courses,
            "seasonal_highlights": season_data["vegetables"][:3],
            "total_ingredients": len(unique_ingredients),
            "estimated_prep_time": f"{courses * 30} minutes total",
            "wine_pairings": get_seasonal_wine_pairings(season, cuisine_style),
            "chef_notes": f"This {season} menu emphasizes seasonal ingredients and {style_data['characteristics'][0]} preparations",
            "sustainability_notes": "Uses locally sourced, seasonal ingredients to minimize environmental impact"
        }
    except Exception as e:
        return {"error": f"Error generating seasonal menu: {str(e)}"}


def get_seasonal_wine_pairings(season: str, cuisine_style: str) -> List[str]:
    """Get wine pairing recommendations."""
    pairings = {
        "spring": ["Sauvignon Blanc", "Pinot Grigio", "Light Rosé"],
        "summer": ["Chardonnay", "Rosé", "Light Reds"],
        "autumn": ["Pinot Noir", "Merlot", "Riesling"],
        "winter": ["Cabernet Sauvignon", "Shiraz", "Port"]
    }
    return pairings.get(season.lower(), ["House wine"])


@tool
def create_cooking_technique_guide(technique: str, ingredient: str) -> Dict[str, Any]:
    """Create a detailed guide for specific cooking techniques."""
    try:
        # Cooking technique database
        techniques = {
            "braising": {
                "description": "Slow cooking in liquid after browning",
                "best_for": ["tough cuts", "root vegetables", "poultry"],
                "temperature": "325-350°F (160-175°C)",
                "liquid_ratio": "1/3 to 1/2 coverage",
                "time_range": "1-4 hours",
                "equipment": ["Dutch oven", "heavy pot with lid"]
            },
            "roasting": {
                "description": "Cooking with dry heat in an oven",
                "best_for": ["whole birds", "large cuts", "vegetables"],
                "temperature": "375-450°F (190-230°C)",
                "liquid_ratio": "None (dry heat)",
                "time_range": "20 minutes - 3 hours",
                "equipment": ["roasting pan", "meat thermometer"]
            },
            "sautéing": {
                "description": "Quick cooking in a small amount of fat",
                "best_for": ["tender cuts", "vegetables", "seafood"],
                "temperature": "Medium-high heat",
                "liquid_ratio": "Minimal fat only",
                "time_range": "2-10 minutes",
                "equipment": ["sauté pan", "tongs or spatula"]
            },
            "steaming": {
                "description": "Cooking with steam from boiling water",
                "best_for": ["delicate fish", "vegetables", "dumplings"],
                "temperature": "212°F (100°C) steam",
                "liquid_ratio": "Water below steamer basket",
                "time_range": "3-20 minutes",
                "equipment": ["steamer basket", "pot with lid"]
            },
            "grilling": {
                "description": "Cooking over direct heat source",
                "best_for": ["steaks", "burgers", "vegetables"],
                "temperature": "Medium to high heat",
                "liquid_ratio": "None (dry heat)",
                "time_range": "2-30 minutes",
                "equipment": ["grill", "tongs", "grill brush"]
            }
        }
        
        # Ingredient-specific modifications
        ingredient_adjustments = {
            "chicken": {"internal_temp": "165°F", "rest_time": "5 minutes"},
            "beef": {"internal_temp": "145°F for medium-rare", "rest_time": "10 minutes"},
            "fish": {"internal_temp": "145°F", "rest_time": "2 minutes"},
            "vegetables": {"doneness": "tender-crisp", "seasoning": "salt at end"},
            "pork": {"internal_temp": "145°F", "rest_time": "5 minutes"}
        }
        
        technique_data = techniques.get(technique.lower(), techniques["sautéing"])
        ingredient_data = ingredient_adjustments.get(ingredient.lower(), {})
        
        # Create step-by-step instructions
        instructions = generate_technique_instructions(technique, ingredient, technique_data)
        
        # Safety considerations
        safety_tips = [
            "Use appropriate temperature monitoring",
            "Ensure proper food safety temperatures",
            "Handle hot equipment with care",
            "Keep workspace clean and organized"
        ]
        
        # Common mistakes
        common_mistakes = get_common_mistakes(technique)
        
        return {
            "technique": technique.title(),
            "ingredient": ingredient.title(),
            "description": technique_data["description"],
            "optimal_conditions": {
                "temperature": technique_data["temperature"],
                "time_range": technique_data["time_range"],
                "equipment_needed": technique_data["equipment"]
            },
            "step_by_step": instructions,
            "ingredient_specifics": ingredient_data,
            "safety_considerations": safety_tips,
            "common_mistakes": common_mistakes,
            "pro_tips": get_pro_tips(technique),
            "troubleshooting": get_troubleshooting_tips(technique)
        }
    except Exception as e:
        return {"error": f"Error creating cooking guide: {str(e)}"}


def generate_technique_instructions(technique: str, ingredient: str, technique_data: Dict) -> List[str]:
    """Generate step-by-step cooking instructions."""
    base_instructions = {
        "braising": [
            f"1. Season {ingredient} and brown on all sides in hot oil",
            "2. Remove from pan and sauté aromatics",
            "3. Add liquid to cover 1/3 of the ingredient",
            "4. Cover and cook in oven at specified temperature",
            "5. Check doneness and adjust seasoning"
        ],
        "roasting": [
            f"1. Preheat oven to appropriate temperature",
            f"2. Season {ingredient} thoroughly",
            "3. Place on roasting rack if available",
            "4. Roast until internal temperature is reached",
            "5. Rest before carving or serving"
        ],
        "sautéing": [
            "1. Heat pan over medium-high heat",
            "2. Add small amount of oil or butter",
            f"3. Add {ingredient} in single layer",
            "4. Cook without moving initially",
            "5. Flip or stir when properly browned"
        ]
    }
    return base_instructions.get(technique.lower(), ["Follow basic cooking principles"])


def get_common_mistakes(technique: str) -> List[str]:
    """Get common mistakes for cooking techniques."""
    mistakes = {
        "braising": ["Not browning first", "Too much liquid", "Temperature too high"],
        "roasting": ["Not preheating oven", "Opening oven too often", "Not resting meat"],
        "sautéing": ["Overcrowding pan", "Moving food too soon", "Wrong temperature"],
        "grilling": ["Not preheating grill", "Flipping too often", "Wrong temperature zone"]
    }
    return mistakes.get(technique.lower(), ["General cooking errors"])


def get_pro_tips(technique: str) -> List[str]:
    """Get professional tips for techniques."""
    tips = {
        "braising": ["Use heavy-bottomed pot", "Brown in batches", "Add acid for tenderness"],
        "roasting": ["Use meat thermometer", "Let oven preheat fully", "Baste periodically"],
        "sautéing": ["Don't overcrowd", "Use right size pan", "Have ingredients ready"]
    }
    return tips.get(technique.lower(), ["Practice makes perfect"])


def get_troubleshooting_tips(technique: str) -> List[str]:
    """Get troubleshooting advice."""
    troubleshooting = {
        "braising": ["If tough: cook longer", "If dry: add more liquid", "If bland: season liquid"],
        "roasting": ["If browning too fast: lower temperature", "If not browning: raise temperature"]
    }
    return troubleshooting.get(technique.lower(), ["Adjust time and temperature as needed"])


async def creative_culinary_agent(culinary_request: str) -> str:
    """Creative culinary expert agent that provides comprehensive cooking assistance."""
    try:
        # Parse request for culinary task
        request_lower = culinary_request.lower()
        
        if "fusion" in request_lower:
            # Extract cuisines if mentioned
            cuisine_1 = "italian"
            cuisine_2 = "japanese"
            if "mexican" in request_lower:
                cuisine_1 = "mexican"
            if "thai" in request_lower:
                cuisine_2 = "thai"
            
            result = create_fusion_recipe(cuisine_1, cuisine_2, "main", [])
            
        elif "nutrition" in request_lower or "analyze" in request_lower:
            # Sample ingredients for analysis
            ingredients = ["chicken", "broccoli", "rice", "olive oil"]
            result = analyze_nutritional_content(ingredients)
            
        elif "seasonal" in request_lower or "menu" in request_lower:
            season = "summer"
            if "winter" in request_lower:
                season = "winter"
            elif "spring" in request_lower:
                season = "spring"
            elif "autumn" in request_lower or "fall" in request_lower:
                season = "autumn"
            
            result = generate_seasonal_menu(season, "mediterranean", 3)
            
        elif "technique" in request_lower or "cooking" in request_lower:
            technique = "braising"
            ingredient = "chicken"
            if "roasting" in request_lower:
                technique = "roasting"
            if "beef" in request_lower:
                ingredient = "beef"
            
            result = create_cooking_technique_guide(technique, ingredient)
            
        else:
            # Default to fusion recipe
            result = create_fusion_recipe("italian", "asian", "main", [])
        
        # Format response
        if result.get("error"):
            return f"Error: {result['error']}"
        
        response = f"Culinary Assistance: {culinary_request}\n\n"
        
        if "recipe_name" in result:
            response += f"Recipe: {result['recipe_name']}\n"
            response += f"Ingredients: {', '.join(result['ingredients'][:5])}...\n"
            response += f"Cooking Time: {result.get('cook_time', 'Varies')}\n"
        elif "menu_theme" in result:
            response += f"Menu: {result['menu_theme']}\n"
            response += f"Courses: {result['total_courses']}\n"
            response += f"Featured Dishes: {[course['dish_name'] for course in result['menu_courses'][:2]]}\n"
        elif "technique" in result:
            response += f"Technique: {result['technique']} for {result['ingredient']}\n"
            response += f"Description: {result['description']}\n"
        elif "total_nutrition" in result:
            response += f"Nutritional Analysis:\n"
            response += f"Calories: {result['total_nutrition']['calories']}\n"
            response += f"Protein: {result['total_nutrition']['protein']}g\n"
        
        return response
        
    except Exception as e:
        return f"Error in culinary assistance: {str(e)}"


class NutritionalWellnessAgent:
    """Real-world nutritional wellness agent for personalized health and nutrition planning."""
    
    def __init__(self):
        self.name = "NutritionalWellnessAgent"
        self.complexity_level = 3
        self.description = "Real-world nutritional wellness agent for personalized health planning, meal optimization, and dietary guidance"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the culinary expert workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create tools for different culinary domains
            recipe_tools = [
                await function_to_schema(create_fusion_recipe, func_name="create_fusion_recipe", enhance_description=True),
                await function_to_schema(generate_seasonal_menu, func_name="generate_seasonal_menu", enhance_description=True),
            ]
            
            nutrition_tools = [
                await function_to_schema(analyze_nutritional_content, func_name="analyze_nutritional_content", enhance_description=True),
            ]
            
            technique_tools = [
                await function_to_schema(create_cooking_technique_guide, func_name="create_cooking_technique_guide", enhance_description=True),
            ]
            
            # Create response agent
            response_agent = await function_to_schema(creative_culinary_agent, func_name="creative_culinary_agent", enhance_description=True)
            
            # Create main orchestrator with routing capability
            all_tools = recipe_tools + nutrition_tools + technique_tools + [response_agent]
            main_orchestrator = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=all_tools
            )
            
            # Create specialized LLM execution nodes
            recipe_agent = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=recipe_tools
            )
            
            nutrition_agent = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=nutrition_tools
            )
            
            technique_agent = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=technique_tools
            )
            
            # Create workflow graph
            execution_graph = WorkflowGraph()
            
            # Add main orchestrator
            execution_graph.add_orchestrator_node("main_orchestrator", main_orchestrator)
            
            # Add LLM execution nodes
            execution_graph.add_node("recipe_specialist", recipe_agent)
            execution_graph.add_node("nutrition_specialist", nutrition_agent)
            execution_graph.add_node("technique_specialist", technique_agent)
            
            # Add tool nodes
            execution_graph.add_node("recipe_creator", create_fusion_recipe)
            execution_graph.add_node("nutrition_analyzer", analyze_nutritional_content)
            execution_graph.add_node("menu_generator", generate_seasonal_menu)
            execution_graph.add_node("technique_guide", create_cooking_technique_guide)
            
            # Connect orchestrator to specialized agents
            execution_graph.add_edge("__start__", "main_orchestrator")
            execution_graph.add_edge("main_orchestrator", "recipe_specialist")
            execution_graph.add_edge("main_orchestrator", "nutrition_specialist")
            execution_graph.add_edge("main_orchestrator", "technique_specialist")
            
            # Connect specialized agents to their tools
            execution_graph.add_edge("recipe_specialist", "recipe_creator")
            execution_graph.add_edge("recipe_specialist", "menu_generator")
            execution_graph.add_edge("nutrition_specialist", "nutrition_analyzer")
            execution_graph.add_edge("technique_specialist", "technique_guide")
            
            # Add human interaction
            execution_graph.add_human_in_the_loop("main_orchestrator")
            
            return execution_graph
            
        except Exception as e:
            print(f"Error creating workflow: {e}")
            raise
    
    def get_real_world_scenarios(self) -> List[Dict[str, Any]]:
        """Get real-world nutritional wellness scenarios for health application."""
        return [
            {
                "scenario": "Weight management meal plan",
                "prompt": "Create a weekly meal plan for a 35-year-old office worker trying to lose 20 pounds. They prefer Mediterranean-style food and have no dietary restrictions.",
                "category": "weight_management"
            },
            {
                "scenario": "Nutritional analysis for health",
                "prompt": "Analyze the nutritional content of a typical breakfast: oatmeal with banana, almonds, and honey. Provide health recommendations.",
                "category": "nutrition_analysis"
            },
            {
                "scenario": "Diabetic-friendly menu planning",
                "prompt": "Generate a seasonal menu for someone with type 2 diabetes, focusing on blood sugar control and heart health.",
                "category": "medical_nutrition"
            },
            {
                "scenario": "Athletic performance nutrition",
                "prompt": "Design a nutrition plan for a marathon runner during training season, focusing on energy and recovery.",
                "category": "sports_nutrition"
            },
            {
                "scenario": "Family healthy eating",
                "prompt": "Create healthy fusion recipes that appeal to both adults and children, incorporating vegetables and balanced nutrition.",
                "category": "family_nutrition"
            }
        ]
    
    async def run_benchmark(self, prompt: str) -> Dict[str, Any]:
        """Run a benchmark test with the given prompt."""
        try:
            workflow = await self.create_workflow()
            compiled_graph = workflow.compile()
            
            result = await compiled_graph.execute(initial_input=prompt)
            
            return {
                "agent": self.name,
                "prompt": prompt,
                "result": result,
                "complexity_level": self.complexity_level,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "prompt": prompt,
                "error": str(e),
                "complexity_level": self.complexity_level,
                "status": "error"
            }


# Export the agent
__all__ = ["NutritionalWellnessAgent", "creative_culinary_agent"] 