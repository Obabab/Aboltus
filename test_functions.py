from sqlalchemy.orm import Session
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, Meal_PlanMeal, Meal_Ingredient, User, MealPlans, Favorites, Meals, Ingredients, DietTypes

# Подключение к базе данных
DATABASE_URL = 'postgresql://postgres:laygon@localhost:5432/mydatabase'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Функции для User
def create_user(session, username: str, password_hash: str, email: str, 
                weight: float = None, height: float = None, age: int = None, diet_type_id: int = None):
    user = User(
        username=username,
        password_hash=password_hash,
        email=email,
        weight=weight,
        height=height,
        age=age,
        diet_type_id=diet_type_id
    )
    session.add(user)
    session.commit()
    return user

def get_all_users(session):
    return session.query(User).all()

def get_user_by_id(session, user_id: int):
    return session.get(User, user_id)

def delete_user(session, user_id: int):
    user = get_user_by_id(session, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


# Функции для MealPlans
def create_meal_plan(session, user_id: int, duration: int, total_price: float = None):
    meal_plan = MealPlans(
        user_id=user_id,
        duration=duration,
        total_price=total_price
    )
    session.add(meal_plan)
    session.commit()
    return meal_plan

def get_all_meal_plans(session):
    return session.query(MealPlans).all()

def get_meal_plan_by_id(session, plan_id: int):
    return session.get(MealPlans, plan_id)

def delete_meal_plan(session, plan_id: int):
    meal_plan = get_meal_plan_by_id(session, plan_id)
    if meal_plan:
        session.delete(meal_plan)
        session.commit()
        return True
    return False


# Функции для Favorites
def create_favorite(session, user_id: int, meal_id: int):
    favorite = Favorites(
        user_id=user_id,
        meal_id=meal_id
    )
    session.add(favorite)
    session.commit()
    return favorite

def get_all_favorites(session):
    return session.query(Favorites).all()

def get_favorite_by_id(session, favorite_id: int):
    return session.get(Favorites, favorite_id)

def delete_favorite(session, favorite_id: int):
    favorite = get_favorite_by_id(session, favorite_id)
    if favorite:
        session.delete(favorite)
        session.commit()
        return True
    return False


# Функции для Meals
def create_meal(session, name: str, price: float, description: str = None, diet_type_id: int = None):
    meal = Meals(
        name=name,
        description=description,
        price=price,
        diet_type_id=diet_type_id
    )
    session.add(meal)
    session.commit()
    return meal

def get_all_meals(session):
    return session.query(Meals).all()

def get_meal_by_id(session, meal_id: int):
    return session.get(Meals, meal_id)

def delete_meal(session, meal_id: int):
    meal = get_meal_by_id(session, meal_id)
    if meal:
        session.delete(meal)
        session.commit()
        return True
    return False


# Функции для Ingredients
def create_ingredient(session, name: str, price_per_unit: float, unit: str,
                      store_name: str = None, valid_from: str = None):
    ingredient = Ingredients(
        name=name,
        price_per_unit=price_per_unit,
        unit=unit,
        store_name=store_name,
        valid_from=valid_from
    )
    session.add(ingredient)
    session.commit()
    return ingredient

def get_all_ingredients(session):
    return session.query(Ingredients).all()

def get_ingredient_by_id(session, ingredient_id: int):
    return session.get(Ingredients, ingredient_id)

def delete_ingredient(session, ingredient_id: int):
    ingredient = get_ingredient_by_id(session, ingredient_id)
    if ingredient:
        session.delete(ingredient)
        session.commit()
        return True
    return False


# Функции для DietTypes
def create_diet_type(session, name: str, is_restricted: int, description: str = None):
    diet_type = DietTypes(
        name=name,
        description=description,
        is_restricted=is_restricted
    )
    session.add(diet_type)
    session.commit()
    return diet_type

def get_all_diet_types(session):
    return session.query(DietTypes).all()

def get_diet_type_by_id(session, diet_type_id: int):
    return session.get(DietTypes, diet_type_id)

def delete_diet_type(session, diet_type_id: int):
    diet_type = get_diet_type_by_id(session, diet_type_id)
    if diet_type:
        session.delete(diet_type)
        session.commit()
        return True
    return False


def test_users():
    print("Тестирование таблицы Users:")
    
    # Создание
    user = create_user(
        session,
        username="test_user",
        password_hash="test_hash",
        email="test@example.com",
        weight=70.5,
        height=175.0,
        age=30
    )
    print(f"Создан пользователь: {user.username} (ID: {user.user_id})")
    
    # Чтение
    print("\nВсе пользователи:")
    for u in get_all_users(session):
        print(f"ID: {u.user_id}, Username: {u.username}, Email: {u.email}")
    
    # Удаление
    delete_user(session, user.user_id)
    print(f"\nПользователь ID {user.user_id} удален")

def test_diet_types():
    print("\nТестирование таблицы DietTypes:")
    
    # Создание
    diet_type = create_diet_type(
        session,
        name="Test Diet",
        is_restricted=1,
        description="Test diet description"
    )
    print(f"Создан тип диеты: {diet_type.name} (ID: {diet_type.diet_type_id})")
    
    # Чтение
    print("\nВсе типы диет:")
    for dt in get_all_diet_types(session):
        print(f"ID: {dt.diet_type_id}, Name: {dt.name}, Restricted: {dt.is_restricted}")
    
    # Удаление
    delete_diet_type(session, diet_type.diet_type_id)
    print(f"\nТип диеты ID {diet_type.diet_type_id} удален")

def test_meals():
    print("\nТестирование таблицы Meals:")
    
    # Создание
    meal = create_meal(
        session,
        name="Test Meal",
        price=15.99,
        description="Test meal description"
    )
    print(f"Создано блюдо: {meal.name} (ID: {meal.meal_id})")
    
    # Чтение
    print("\nВсе блюда:")
    for m in get_all_meals(session):
        print(f"ID: {m.meal_id}, Name: {m.name}, Price: {m.price}")
    
    # Удаление
    delete_meal(session, meal.meal_id)
    print(f"\nБлюдо ID {meal.meal_id} удалено")

def test_ingredients():
    print("\nТестирование таблицы Ingredients:")
    
    # Создание
    ingredient = create_ingredient(
        session,
        name="Test Ingredient",
        price_per_unit=2.99,
        unit="kg"
    )
    print(f"Создан ингредиент: {ingredient.name} (ID: {ingredient.ingredient_id})")
    
    # Чтение
    print("\nВсе ингредиенты:")
    for i in get_all_ingredients(session):
        print(f"ID: {i.ingredient_id}, Name: {i.name}, Price: {i.price_per_unit}")
    
    # Удаление
    delete_ingredient(session, ingredient.ingredient_id)
    print(f"\nИнгредиент ID {ingredient.ingredient_id} удален")

def test_meal_plans():
    print("\nТестирование таблицы MealPlans:")
    
    # Создаем тестового пользователя
    user = create_user(
        session,
        username="test_plan_user",
        password_hash="test_hash",
        email="test_plan@example.com"
    )
    
    # Создание
    meal_plan = create_meal_plan(
        session,
        user_id=user.user_id,
        duration=7,
        total_price=100.00
    )
    print(f"Создан план питания: ID {meal_plan.plan_id} для пользователя {user.username}")
    
    # Чтение
    print("\nВсе планы питания:")
    for mp in get_all_meal_plans(session):
        print(f"ID: {mp.plan_id}, User ID: {mp.user_id}, Duration: {mp.duration}")
    
    # Удаление
    delete_meal_plan(session, meal_plan.plan_id)
    delete_user(session, user.user_id)
    print(f"\nПлан питания ID {meal_plan.plan_id} и пользователь ID {user.user_id} удалены")



if __name__ == "__main__":
    # Запуск тестов
    test_users()
    test_diet_types()
    test_meals()
    test_ingredients()
    test_meal_plans()
    
    session.close()