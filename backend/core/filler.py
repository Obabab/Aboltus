import os
import sys
import django

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

import random
from django.db import transaction
from django.contrib.auth.models import User as DjangoUser
from core.models import User, MealPlans, Meals, Ingredients, Favorites, MealPlanMeal, MealIngredient
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from faker import Faker
from faker_food import FoodProvider

fake = Faker()
fake.add_provider(FoodProvider)


def create_users(count=10):
    users = []
    for _ in range(count):
        username = fake.unique.user_name()[:150]
        email = fake.unique.email()
        password = fake.password(length=6, special_chars=True, digits=True, upper_case=True, lower_case=True)
        django_user = DjangoUser.objects.create_user(username=username, email=email, password=password)
        user = User.objects.create(
            django_user=django_user,
            username=username,
            weight=Decimal(str(round(random.uniform(50, 120), 1))),
            height=Decimal(str(round(random.uniform(150, 200), 1))),
            age=random.randint(18, 65),
        )
        users.append(user)
        print(f"Создан пользователь: {username}, пароль: {password}")
    return users

def create_ingredients(count=30):
    ingredients = []
    for _ in range(count):
        name = fake.unique.word().capitalize() + ' ' + fake.ingredient()
        calories_per_unit = round(random.uniform(0.1, 20.0), 2)
        unit = random.choice(['g', 'ml', 'piece', 'tbsp'])
        store_name = fake.company() if random.random() > 0.3 else None
        ingredient = Ingredients.objects.create(
            name=name[:255],
            calories_per_unit=Decimal(str(calories_per_unit)),
            unit=unit,
            store_name=store_name,
            valid_from=timezone.now()
        )
        ingredients.append(ingredient)
    return ingredients

def create_meals(count=300):
    meals = []
    for _ in range(count):
        name = fake.dish()[:255]
        # description = fake.text(max_nb_chars=300)
        description = FoodProvider.dish_description(fake)
        calories = Decimal(str(round(random.uniform(100, 800), 2)))
        meal = Meals.objects.create(
            name=name,
            description=description,
            calories=calories,
            type=random.choice([1, 2, 3]),
            image_path= random.choice(['admin/img/dish1.jpg', 'admin/img/dish2.jpg', 'admin/img/dish3.jpg', 'admin/img/dish4.jpg', 'admin/img/dish5.jpg', 'admin/img/dish6.jpg']),
        )
        meals.append(meal)
    return meals

def link_meals_ingredients(meals, ingredients):
    for meal in meals:
        for ingredient in random.sample(ingredients, random.randint(2, 6)):
            MealIngredient.objects.create(
                meal=meal,
                ingredient=ingredient,
                quantity=Decimal(str(round(random.uniform(0.1, 3.0), 2)))
            )

def create_meal_plans(users_list, count=15):
    """Создаёт планы питания, используя уже существующие блюда из базы."""
    meal_plans_list = []

    if not users_list:
        print("Нет пользователей для создания планов.")
        return meal_plans_list

    # Получаем уже существующие блюда по типам
    breakfasts = list(Meals.objects.filter(type=1))
    lunches    = list(Meals.objects.filter(type=2))
    dinners    = list(Meals.objects.filter(type=3))

    if not (breakfasts and lunches and dinners):
        print("Недостаточно блюд по типам (1-завтрак, 2-обед, 3-ужин).")
        return meal_plans_list

    for _ in range(count):
        user = random.choice(users_list)
        duration_days = random.randint(3, 14)
        total_plan_calories = Decimal('0.00')

        meal_plan = MealPlans.objects.create(
            user=user,
            duration=duration_days,
            total_calories=Decimal('0.00')  # временно, обновим позже
        )

        # Количество блюд в плане должно быть кратно 3
        num_meals = random.choice([3, 6, 9])

        for i in range(num_meals):
            meal_type = (i % 3) + 1

            if meal_type == 1:
                meal = random.choice(breakfasts)
            elif meal_type == 2:
                meal = random.choice(lunches)
            else:
                meal = random.choice(dinners)

            # Привязываем блюдо к плану
            MealPlanMeal.objects.create(plan=meal_plan, meal=meal)
            total_plan_calories += Decimal(str(meal.calories))

        # Обновляем total_calories
        meal_plan.total_calories = total_plan_calories
        meal_plan.save()

        meal_plans_list.append(meal_plan)

    return meal_plans_list



def create_favorites(users, meals, count=20):
    created = 0
    attempts = 0
    while created < count and attempts < count * 3:
        user = random.choice(users)
        meal = random.choice(meals)
        if not Favorites.objects.filter(user=user, meal=meal).exists():
            Favorites.objects.create(user=user, meal=meal)
            created += 1
        attempts += 1

@transaction.atomic
def populate():
    print("Создание пользователей...")
    users = create_users()

    print("Создание ингредиентов...")
    ingredients = create_ingredients()

    print("Создание блюд...")
    meals = create_meals()

    print("Связываем блюда с ингредиентами...")
    link_meals_ingredients(meals, ingredients)

    print("Создание планов питания...")
    create_meal_plans(users, 15)

    print("Создание избранного...")
    create_favorites(users, meals)

    print("Готово!")

if __name__ == "__main__":
    populate()
