from django.contrib import admin
from .models import (
    User,
    Profile,
    MealPlans,
    Meals,
    Ingredients,
    DietTypes,
    Favorites,
    MealPlanMeal,
    MealIngredient
)

# --------------------
# Пользователь
# --------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для кастомной модели пользователя."""
    list_display = ('id', 'username', 'email', 'weight', 'height', 'age', 'diet_type', 'created_at')
    search_fields = ('username', 'email', 'diet_type__name')
    list_filter = ('diet_type', 'created_at', 'age')
    ordering = ('-created_at',)


# --------------------
# Профиль
# --------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Профили пользователей (если используются отдельно)."""
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)


# --------------------
# План питания
# --------------------
@admin.register(MealPlans)
class MealPlanAdmin(admin.ModelAdmin):
    """Планы питания пользователя."""
    list_display = ('id', 'user', 'duration', 'total_calories', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('duration', 'created_at')
    date_hierarchy = 'created_at'


# --------------------
# Блюда
# --------------------
@admin.register(Meals)
class MealsAdmin(admin.ModelAdmin):
    """Блюда, отображаемые в базе."""
    list_display = ('id', 'name', 'calories', 'type', 'diet_type', 'created_at')
    search_fields = ('name', 'description', 'diet_type__name')
    list_filter = ('type', 'diet_type', 'created_at')
    ordering = ('-created_at',)


# --------------------
# Ингредиенты
# --------------------
@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Ингредиенты, используемые в блюдах."""
    list_display = ('id', 'name', 'calories_per_unit', 'unit', 'store_name', 'valid_from', 'created_at')
    search_fields = ('name', 'store_name')
    list_filter = ('unit', 'created_at', 'valid_from')
    date_hierarchy = 'valid_from'


# --------------------
# Типы диет
# --------------------
@admin.register(DietTypes)
class DietTypeAdmin(admin.ModelAdmin):
    """Типы диет, к которым могут относиться блюда и пользователи."""
    list_display = ('id', 'name', 'is_restricted')
    search_fields = ('name',)
    list_filter = ('is_restricted',)


# --------------------
# Избранные блюда
# --------------------
@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Избранные блюда пользователя."""
    list_display = ('id', 'user', 'meal')
    search_fields = ('user__username', 'meal__name')
    list_filter = ('user',)


# --------------------
# Промежуточная модель MealPlanMeal
# --------------------
@admin.register(MealPlanMeal)
class MealPlanMealAdmin(admin.ModelAdmin):
    """Связь блюд с планами питания."""
    list_display = ('id', 'plan', 'meal')
    search_fields = ('plan__user__username', 'meal__name')


# --------------------
# Промежуточная модель MealIngredient
# --------------------
@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    """Связь ингредиентов с блюдами и их количество."""
    list_display = ('id', 'meal', 'ingredient', 'quantity')
    search_fields = ('meal__name', 'ingredient__name')
    list_filter = ('ingredient',)
