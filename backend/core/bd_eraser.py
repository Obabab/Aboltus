import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User as DjangoUser
from core.models import (
    DietTypes, User, MealPlans, Meals, Ingredients, 
    Favorites, MealPlanMeal, MealIngredient, Profile
)

def clear_database():
    try:
        with transaction.atomic():
            print("Начинаем очистку базы данных...")

            print("Удаляем связи между блюдами и ингредиентами...")
            MealIngredient.objects.all().delete()

            print("Удаляем связи между планами и блюдами...")
            MealPlanMeal.objects.all().delete()

            print("Удаляем избранные блюда...")
            Favorites.objects.all().delete()

            print("Удаляем планы питания...")
            MealPlans.objects.all().delete()

            print("Удаляем блюда...")
            Meals.objects.all().delete()

            print("Удаляем ингредиенты...")
            Ingredients.objects.all().delete()

            print("Удаляем профили...")
            Profile.objects.all().delete()

            print("Удаляем пользователей сайта...")
            User.objects.all().delete()

            print("Удаляем пользователей Django...")
            DjangoUser.objects.all().delete()

            print("Удаляем типы диет...")
            DietTypes.objects.all().delete()

        print("\nБаза данных успешно очищена!")
        print("Все таблицы были очищены в правильном порядке с учетом зависимостей.")
    except Exception as e:
        print(f"\nОшибка при очистке базы данных: {e}")
        raise

if __name__ == "__main__":
    clear_database()
