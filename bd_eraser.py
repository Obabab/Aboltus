from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app import Base, Meal_PlanMeal, Meal_Ingredient, User, MealPlans, Favorites, Meals, Ingredients, DietTypes

# Подключение к базе данных
DATABASE_URL = 'postgresql://postgres:laygon@localhost:5432/mydatabase'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def clear_database():
    try:
        # Очистка связующих таблиц (многие ко многим)
        session.execute(Meal_PlanMeal.delete())
        session.execute(Meal_Ingredient.delete())

        # Очистка основных таблиц
        session.query(Favorites).delete()
        session.query(Meals).delete()
        session.query(Ingredients).delete()
        session.query(MealPlans).delete()
        session.query(User).delete()
        session.query(DietTypes).delete()

        # Фиксация изменений
        session.commit()
        print("База данных успешно очищена!")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при очистке базы данных: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_database()