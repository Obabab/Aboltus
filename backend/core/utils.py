from core.models import MealPlans, Meals, MealPlanMeal
from decimal import Decimal

def create_personal_mealplan(user, total_calories, duration_days):
    plan = MealPlans.objects.create(
        user=user,
        duration=duration_days,
        total_calories=Decimal(str(round(total_calories, 2)))
    )

    kcal_targets = {
        1: total_calories * 0.3,
        2: total_calories * 0.5,
        3: total_calories * 0.2,
    }

    for _ in range(duration_days):
        for meal_type, target in kcal_targets.items():
            meals = Meals.objects.filter(
                type=meal_type,
                calories__gte=target - 50,
                calories__lte=target + 50
            ).order_by('?')
            if meals.exists():
                meal = meals.first()
                MealPlanMeal.objects.create(plan=plan, meal=meal)
            else:
                print(f"Нет подходящих блюд на {meal_type} с {target} ±50 ккал")

    return plan

