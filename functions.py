from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, Meal_PlanMeal, Meal_Ingredient, User, MealPlans, Favorites, Meals, Ingredients, DietTypes
from werkzeug.security import generate_password_hash

# Подключение к базе данных
DATABASE_URL = 'postgresql://postgres:laygon@localhost:5432/mydatabase'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def set_meal_price():
    meal_ids = [meal.meal_id for meal in session.query(Meals).all()] 
            
    for meal_idd in meal_ids:
        meal_ingrs = session.query(Meal_Ingredient.c.ingredient_id).filter(Meal_Ingredient.c.meal_id == meal_idd).all()
        #print('Meal ', meal_idd)
        price = 0
        # Преобразуем результат в плоский список ingredient_id 
        ingredient_ids = [row.ingredient_id for row in meal_ingrs]

        for ingr_id in ingredient_ids:
            ingr_price = session.query(Ingredients.price_per_unit).filter(Ingredients.ingredient_id == ingr_id).scalar()

            quant = session.query(Meal_Ingredient.c.quantity).filter(
            Meal_Ingredient.c.meal_id == meal_idd,
            Meal_Ingredient.c.ingredient_id == ingr_id).scalar()

            price += ingr_price*quant
        #print(price)
        meal = session.query(Meals).filter_by(meal_id=meal_idd).first()
        meal.price = price


#Рассчёт цен планов питания
def set_mealplan_prices():
    # Получаем все планы питания
    meal_plans = session.query(MealPlans).all()

    for plan in meal_plans:
        # Рассчитываем общую стоимость плана питания
        total_price = sum(meal.price for meal in plan.meals)

        # Устанавливаем стоимость плана питания
        plan.total_price = total_price
        session.commit()

    print("Стоимость всех планов питания успешно обновлена.")



#Вывод планов питания и их стоимость у конкретного пользователя
def get_user_meals(username):
    # Находим пользователя по username
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print(f"Пользователь с username '{username}' не найден.")
        return

    # Получаем все планы питания пользователя
    meal_plans = session.query(MealPlans).filter_by(user_id=user.user_id).all()

    if not meal_plans:
        print(f"У пользователя '{username}' нет планов питания.")
        return

    print(f"Планы питания пользователя '{username}':")
    for plan in meal_plans:
        print(f"- План ID: {plan.plan_id}, Длительность: {plan.duration} дней, Стоимость: {plan.total_price}")





#set_mealplan_prices()

get_user_meals('davidreed')

#set_meal_price()        
session.commit()

