from rest_framework import serializers
from .models import User, MealPlans, Meals, Ingredients, DietTypes, Favorites
from .functions import UserManager

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)  
    diet_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DietTypes.objects.all(),
        source='diet_type',
        allow_null=True,
        required=False
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'weight', 'height', 'age', 'diet_type_id']

    def create(self, validated_data):
        diet_type_instance = validated_data.pop('diet_type', None)
        diet_type_id_val = diet_type_instance.id if diet_type_instance else None
        password = validated_data.pop('password', None)
        username = validated_data['username']
        email = validated_data['email']
        user = UserManager.create_user(
            username=username,
            password=password,
            email=email,
            weight=validated_data.get('weight'),
            height=validated_data.get('height'),
            age=validated_data.get('age'),
            diet_type_id=diet_type_id_val
        )
        user.username = username
        user.save()
        user.django_user.is_active = True
        user.django_user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            UserManager.update_password(instance, validated_data.pop('password'))

        django_user = instance.django_user

        # Обновляем имя, email и username в django_user
        if 'username' in validated_data:
            username = validated_data.pop('username')
            django_user.username = username
            instance.username = username
        if 'email' in validated_data:
            django_user.email = validated_data.pop('email')
        if 'first_name' in validated_data:
            django_user.first_name = validated_data.pop('first_name')

        django_user.save()

        # Обработка diet_type (сейчас не используется)
        diet_type_instance = validated_data.pop('diet_type', None)
        if diet_type_instance is not None:
            instance.diet_type = diet_type_instance
        elif 'diet_type_id' in self.fields and 'diet_type' not in validated_data and self.partial:
            pass
        elif validated_data.get('diet_type_id') is None and 'diet_type_id' in validated_data:
            instance.diet_type = None

        # Остальные поля в instance (вес, рост, возраст)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# --- DietType Serializer (исходный) ---
class DietTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietTypes
        fields = ['id', 'name', 'description', 'is_restricted']

# --- Ingredient Serializers  ---
class IngredientSerializer(serializers.ModelSerializer): # Полный сериализатор для CRUD ингредиентов
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'calories_per_unit', 'unit', 'store_name', 'valid_from']

class IngredientSerializerForNesting(serializers.ModelSerializer): # Для вложения в MealSerializer
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'calories_per_unit', 'unit']

# --- Meal Serializers (исходный MealSerializerForNesting и измененный MealSerializer) ---
class MealSerializerForNesting(serializers.ModelSerializer): # Базовый сериализатор для вложенности в MealPlan
    class Meta:
        model = Meals
        fields = ['id', 'name', 'description', 'calories', 'type', 'image_path']

class MealSerializer(serializers.ModelSerializer):
    diet_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DietTypes.objects.all(),
        source='diet_type',
        allow_null=True,
        required=False,
        write_only=True,
    )
    diet_type = DietTypeSerializer(read_only=True) # Для чтения типа диеты
    type = serializers.IntegerField()
    # Поле для чтения ингредиентов (вложенные объекты)
    # Предполагается, что у модели Meals есть ManyToManyField 'ingredients' к модели Ingredients
    ingredients = IngredientSerializerForNesting(many=True, read_only=True)
    # Поле для записи ID ингредиентов
    ingredient_ids = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredients',  # Связываем с атрибутом 'ingredients' модели Meals
        many=True,
        write_only=True,
        required=False,      # Ингредиенты не обязательны для блюда
        allow_empty=True     # Можно передать пустой список
    )

    class Meta:
        model = Meals
        fields = [
            'id', 'name', 'description', 'calories',
            'diet_type_id', 'diet_type',        # Для типа диеты
            'ingredients', 'ingredient_ids',    # Для ингредиентов
            'type',   # для типа приема пищи (завтрак/обед/ужин)
            'image_path'
        ]

    def create(self, validated_data):
        # validated_data['ingredients'] будет содержать список экземпляров Ingredient
        # из-за source='ingredients' в поле ingredient_ids
        ingredients_list = validated_data.pop('ingredients', [])
        meal = super().create(validated_data)
        if ingredients_list:
            meal.ingredients.set(ingredients_list)
        return meal

    def update(self, instance, validated_data):
        ingredients_list = validated_data.pop('ingredients', None)
        meal = super().update(instance, validated_data)
        if ingredients_list is not None: # Позволяет очистить, передав []
            instance.ingredients.set(ingredients_list)
        return meal

# --- MealPlan Serializer (измененный) ---
class MealPlanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Для чтения деталей пользователя

    # Поле для чтения блюд (вложенные объекты)
    # Предполагается, что у модели MealPlans есть ManyToManyField 'meals' к модели Meals
    meals = MealSerializerForNesting(many=True, read_only=True)
    # Поле для записи ID блюд
    meal_ids = serializers.PrimaryKeyRelatedField(
        queryset=Meals.objects.all(),
        source='meals',  # Связываем с атрибутом 'meals' модели MealPlans
        many=True,
        write_only=True,
        required=False,  # Блюда не обязательны для плана
        allow_empty=True # Можно передать пустой список
    )
    class Meta:
        model = MealPlans
        # Убираем 'user_id' из fields, так как 'user' устанавливается во ViewSet'е,
        # а для чтения уже есть 'user'.
        fields = ['id', 'user', 'duration', 'total_calories', 'meals', 'meal_ids']

    def create(self, validated_data):
        # validated_data['user'] будет установлен viewset'ом
        # validated_data['meals'] будет содержать список экземпляров Meal
        # из-за source='meals' в поле meal_ids
        meals_list = validated_data.pop('meals', [])
        meal_plan = super().create(validated_data)
        if meals_list:
            meal_plan.meals.set(meals_list)
        return meal_plan

    def update(self, instance, validated_data):
        meals_list = validated_data.pop('meals', None)
        meal_plan = super().update(instance, validated_data)
        if meals_list is not None: # Позволяет очистить, передав []
            instance.meals.set(meals_list)
        return meal_plan

# --- Favorite Serializer (исходный, с удаленным user_id для записи) ---
class FavoriteSerializer(serializers.ModelSerializer):
    # user_id убран, так как user устанавливается автоматически в perform_create во ViewSet
    user = UserSerializer(read_only=True) # Для чтения деталей пользователя
    meal_id = serializers.PrimaryKeyRelatedField(queryset=Meals.objects.all(), source='meal', write_only=True)
    meal = MealSerializerForNesting(read_only=True) # Для чтения деталей блюда

    class Meta:
        model = Favorites
        fields = ['id', 'user', 'meal', 'meal_id']