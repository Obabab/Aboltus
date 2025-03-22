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

# Создание экземпляра Faker
fake = Faker()

def populate_database():
    try:
        # Создание тестовых типов диет
        diet_types = [
            DietTypes(name="Vegetarian", description="No meat products", is_restricted=0),
            DietTypes(name="Keto", description="Low carb, high fat diet", is_restricted=1),
            DietTypes(name="Vegan", description="No animal products", is_restricted=1)
        ]
        session.add_all(diet_types)
        session.commit()

        # Получаем все diet_type_id
        diet_type_ids = [diet.diet_type_id for diet in session.query(DietTypes).all()]
        
        # Создание тестовых пользователей
        users = []
        for _ in range(10):
            user = User(
                username=fake.user_name(),
                password_hash=generate_password_hash("password123"),
                weight=fake.random_int(min=50, max=100),
                height=fake.random_int(min=150, max=200),
                age=fake.random_int(min=18, max=80),
                email=fake.email(),
                diet_type_id=fake.random_element(diet_type_ids)
            )
            users.append(user)
        session.add_all(users)
        session.commit()

        # Получаем всех пользователей
        user_ids = [user.user_id for user in session.query(User).all()]
        
        # Создание тестовых планов питания
        meal_plans = []
        for _ in range(10):
            meal_plan = MealPlans(
                user_id=fake.random_element(user_ids),
                duration=fake.random_int(min=7, max=30),
                total_price=fake.random_int(min=50, max=500)
            )
            meal_plans.append(meal_plan)
        session.add_all(meal_plans)
        session.commit()
        
        # Создание тестовых блюд
        meals = []
        for _ in range(15):
            meal = Meals(
                name=fake.word(),
                description=fake.text(),
                price=fake.random_int(min=5, max=50),
                diet_type_id=fake.random_element(diet_type_ids)
            )
            meals.append(meal)
        session.add_all(meals)
        session.commit()
        
        # Получаем все meal_id
        meal_ids = [meal.meal_id for meal in session.query(Meals).all()]
        
        # Создание тестовых избранных блюд
        favorites = []
        for _ in range(10):
            favorite = Favorites(
                user_id=fake.random_element(user_ids),
                meal_id=fake.random_element(meal_ids)
            )
            favorites.append(favorite)
        session.add_all(favorites)
        session.commit()

        print("База данных успешно заполнена тестовыми данными!")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при заполнении базы данных: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_database()
