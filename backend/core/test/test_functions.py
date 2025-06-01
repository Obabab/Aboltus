import os
import sys

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from core.models import DietTypes, User, MealPlans, Meals, Ingredients, Favorites, MealPlanMeal, MealIngredient
from core.functions import (
    UserManager, MealPlanManager, MealManager,
    IngredientManager, DietTypeManager, FavoriteManager
)

class TestUserFunctions(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'weight': 70.5,
            'height': 175.0,
            'age': 30
        }

    def test_create_user(self):
        user = UserManager.create_user(**self.user_data)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.weight, self.user_data['weight'])
        self.assertEqual(user.height, self.user_data['height'])
        self.assertEqual(user.age, self.user_data['age'])

    def test_get_user(self):
        user = UserManager.create_user(**self.user_data)
        retrieved_user = UserManager.get_user_by_id(user.id)
        self.assertEqual(retrieved_user, user)

    def test_delete_user(self):
        user = UserManager.create_user(**self.user_data)
        self.assertTrue(UserManager.delete_user(user.id))
        self.assertIsNone(UserManager.get_user_by_id(user.id))

    def test_verify_password(self):
        user = UserManager.create_user(**self.user_data)
        self.assertTrue(UserManager.verify_password(user, self.user_data['password']))
        self.assertFalse(UserManager.verify_password(user, 'wrongpassword'))


class TestMealPlanFunctions(TestCase):
    def setUp(self):
        self.user = UserManager.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.meal_plan_data = {
            'user_id': self.user.id,
            'duration': 7,
            'total_price': 100.00
        }

    def test_create_meal_plan(self):
        meal_plan = MealPlanManager.create_meal_plan(**self.meal_plan_data)
        self.assertIsNotNone(meal_plan)
        self.assertEqual(meal_plan.duration, self.meal_plan_data['duration'])
        self.assertEqual(meal_plan.total_price, self.meal_plan_data['total_price'])

    def test_get_meal_plan(self):
        meal_plan = MealPlanManager.create_meal_plan(**self.meal_plan_data)
        retrieved_plan = MealPlanManager.get_meal_plan_by_id(meal_plan.id)
        self.assertEqual(retrieved_plan, meal_plan)

    def test_delete_meal_plan(self):
        meal_plan = MealPlanManager.create_meal_plan(**self.meal_plan_data)
        self.assertTrue(MealPlanManager.delete_meal_plan(meal_plan.id))
        self.assertIsNone(MealPlanManager.get_meal_plan_by_id(meal_plan.id))


class TestMealFunctions(TestCase):
    def setUp(self):
        self.diet_type = DietTypeManager.create_diet_type(
            name='Test Diet',
            is_restricted=False,
            description='Test diet description'
        )
        self.meal_data = {
            'name': 'Test Meal',
            'price': 15.99,
            'description': 'Test meal description',
            'diet_type_id': self.diet_type.id
        }

    def test_create_meal(self):
        meal = MealManager.create_meal(**self.meal_data)
        self.assertIsNotNone(meal)
        self.assertEqual(meal.name, self.meal_data['name'])
        self.assertEqual(meal.price, self.meal_data['price'])
        self.assertEqual(meal.description, self.meal_data['description'])

    def test_get_meal(self):
        meal = MealManager.create_meal(**self.meal_data)
        retrieved_meal = MealManager.get_meal_by_id(meal.id)
        self.assertEqual(retrieved_meal, meal)

    def test_delete_meal(self):
        meal = MealManager.create_meal(**self.meal_data)
        self.assertTrue(MealManager.delete_meal(meal.id))
        self.assertIsNone(MealManager.get_meal_by_id(meal.id))


class TestIngredientFunctions(TestCase):
    def setUp(self):
        self.ingredient_data = {
            'name': 'Test Ingredient',
            'price_per_unit': 2.99,
            'unit': 'kg',
            'store_name': 'Test Store'
        }

    def test_create_ingredient(self):
        ingredient = IngredientManager.create_ingredient(**self.ingredient_data)
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, self.ingredient_data['name'])
        self.assertEqual(ingredient.price_per_unit, self.ingredient_data['price_per_unit'])
        self.assertEqual(ingredient.unit, self.ingredient_data['unit'])

    def test_get_ingredient(self):
        ingredient = IngredientManager.create_ingredient(**self.ingredient_data)
        retrieved_ingredient = IngredientManager.get_ingredient_by_id(ingredient.id)
        self.assertEqual(retrieved_ingredient, ingredient)

    def test_delete_ingredient(self):
        ingredient = IngredientManager.create_ingredient(**self.ingredient_data)
        self.assertTrue(IngredientManager.delete_ingredient(ingredient.id))
        self.assertIsNone(IngredientManager.get_ingredient_by_id(ingredient.id))


class TestDietTypeFunctions(TestCase):
    def setUp(self):
        self.diet_type_data = {
            'name': 'Test Diet',
            'is_restricted': True,
            'description': 'Test diet description'
        }

    def test_create_diet_type(self):
        diet_type = DietTypeManager.create_diet_type(**self.diet_type_data)
        self.assertIsNotNone(diet_type)
        self.assertEqual(diet_type.name, self.diet_type_data['name'])
        self.assertEqual(diet_type.is_restricted, self.diet_type_data['is_restricted'])

    def test_get_diet_type(self):
        diet_type = DietTypeManager.create_diet_type(**self.diet_type_data)
        retrieved_diet_type = DietTypeManager.get_diet_type_by_id(diet_type.id)
        self.assertEqual(retrieved_diet_type, diet_type)

    def test_delete_diet_type(self):
        diet_type = DietTypeManager.create_diet_type(**self.diet_type_data)
        self.assertTrue(DietTypeManager.delete_diet_type(diet_type.id))
        self.assertIsNone(DietTypeManager.get_diet_type_by_id(diet_type.id))