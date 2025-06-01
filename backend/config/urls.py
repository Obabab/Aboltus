from django.contrib import admin
from django.urls import path, include
from core.views import index, login_view, register_view, dashboard, favorites, Meals_list, MealPlan_list, create_meal_plan, settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet, MealPlanViewSet, MealViewSet,
    IngredientViewSet, DietTypeViewSet, FavoriteViewSet,
    LogoutView
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('meal-plans', MealPlanViewSet, basename='meal-plan')
router.register('meals', MealViewSet, basename='meal')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('diet-types', DietTypeViewSet, basename='diet-type')
router.register('favorites', FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('',             index,         name='home'),
    path('login/',       login_view,    name='login'),
    path('register/',    register_view, name='register'),
    path('dashboard/',   dashboard,     name='dashboard'),
    path('favorites/',   favorites,     name='favorites'),
    path('Meals_list/',   Meals_list,     name='Meals_list'),
    path('MealPlan_list/',   MealPlan_list,     name='MealPlan_list'),
    path('api/create_meal_plan/', create_meal_plan, name='create_meal_plan'),
    path('settings/',   settings,      name='settings'),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/logout/', LogoutView.as_view(), name='auth_logout'),
]
