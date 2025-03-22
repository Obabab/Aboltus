from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, ForeignKey, Table, TIMESTAMP, CheckConstraint, \
    MetaData
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# Создаем объект Metadata
metadata = MetaData()

# Создаем базовый класс с использованием этого объекта Metadata
Base = declarative_base(metadata=metadata)


# Связующая таблица План питания ↔ Блюда 
Meal_PlanMeal = Table(
    'Meal_PlanMeal', Base.metadata,
    Column('meal_id', Integer, ForeignKey('Meals.meal_id'), primary_key=True),
    Column('plan_id', Integer, ForeignKey('MealPlans.plan_id'), primary_key=True)
)

# Связующая таблица Блюда ↔ Ингредиенты 
Meal_Ingredient = Table(
    'Meal_Ingredient', Base.metadata,
    Column('meal_id', Integer, ForeignKey('Meals.meal_id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('Ingredients.ingredient_id'), primary_key=True),
    Column('quantity', Numeric(5, 2), nullable=False)  # Количество ингредиента
)


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(64), nullable=False, unique=True)
    weight = Column(Numeric(4, 1), nullable=True)
    height = Column(Numeric(4, 1), nullable=True)
    age = Column(Numeric(3, 0), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    diet_type_id = Column(Integer, ForeignKey('Diet_types.diet_type_id'), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    
    meal_plans = relationship("MealPlans", back_populates="user")  
    favorites = relationship("Favorites", back_populates="user")  
    diet_type = relationship("DietTypes", back_populates="users")  


class MealPlans(Base):
    __tablename__ = 'MealPlans'

    plan_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    duration = Column(Integer, nullable=False)
    total_price = Column(Numeric(12, 1), nullable=True)

    
    user = relationship("User", back_populates="meal_plans")  
    meals = relationship("Meals", secondary=Meal_PlanMeal, back_populates="meal_plans")  


class Favorites(Base):
    __tablename__ = 'Favorites'

    favorite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    meal_id = Column(Integer, ForeignKey('Meals.meal_id'), nullable=False)

    
    user = relationship("User", back_populates="favorites")  
    meal = relationship("Meals", back_populates="favorites")  


class Meals(Base):
    __tablename__ = 'Meals'

    meal_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    diet_type_id = Column(Integer, ForeignKey('Diet_types.diet_type_id'), nullable=True)

    
    favorites = relationship("Favorites", back_populates="meal")  
    meal_plans = relationship("MealPlans", secondary=Meal_PlanMeal, back_populates="meals")  
    ingredients = relationship("Ingredients", secondary=Meal_Ingredient, back_populates="meals")  
    diet_type = relationship("DietTypes", back_populates="meals")  


class Ingredients(Base):
    __tablename__ = 'Ingredients'

    ingredient_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False) #величина, например килограммы или литры
    store_name = Column(Text, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    
    meals = relationship("Meals", secondary=Meal_Ingredient, back_populates="ingredients")  


class DietTypes(Base):
    __tablename__ = 'Diet_types'

    diet_type_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_restricted = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    
    users = relationship("User", back_populates="diet_type")  
    meals = relationship("Meals", back_populates="diet_type")  