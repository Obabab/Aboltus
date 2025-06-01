from rest_framework import viewsets, status, serializers
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User as DjangoUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.db import models
from itertools import zip_longest
import json
import random
from django.http import JsonResponse
from decimal import Decimal, ROUND_DOWN, InvalidOperation



from .models import User, MealPlans, Meals, Ingredients, DietTypes, Favorites, MealPlanMeal, MealIngredient
from .functions import (
    UserManager, MealPlanManager, MealManager, IngredientManager, DietTypeManager, FavoriteManager, caloriesManager
)
from .serializers import (
    UserSerializer, MealPlanSerializer, MealSerializer,
    IngredientSerializer, DietTypeSerializer, FavoriteSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def check_object_permissions(self, request, obj):
        """
        Проверка, что текущий пользователь имеет доступ к объекту:
        - пользователь сам
        - или staff
        """
        if not (request.user.is_staff or (hasattr(obj, 'django_user') and obj.django_user == request.user)):
            raise PermissionDenied("You do not have permission to perform this action.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        django_user_to_delete = getattr(instance, 'django_user', None)
        if django_user_to_delete:
            try:
                django_user_to_delete.delete()
            except Exception as e:
                print(f"Error deleting DjangoUser: {e}")
        try:
            instance.delete()
        except Exception as e:
            print(f"Error deleting User instance: {e}")
            raise e

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_password(self, request, pk=None):
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid = UserManager.verify_password(user_instance, password)
        return Response({'is_valid': is_valid})



    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """
        Изменение пароля текущего пользователя (или любого, если is_staff).
        """
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        django_user = getattr(user_instance, 'django_user', None)

        if not django_user:
            return Response(
                {'error': 'Associated Django user not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка старого пароля
        if not django_user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

        # Установка нового пароля
        try:
            django_user.set_password(new_password)
            django_user.save()
            return Response({'detail': 'Password successfully changed'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_height(self, request, pk=None):
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        height = request.data.get('height')
        try:
            height = float(height)
            if height <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'error': 'Invalid height value.'}, status=status.HTTP_400_BAD_REQUEST)

        user_instance.height = height
        user_instance.save()
        return Response(self.get_serializer(user_instance).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_weight(self, request, pk=None):
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        weight = request.data.get('weight')
        try:
            weight = float(weight)
            if weight <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'error': 'Invalid weight value.'}, status=status.HTTP_400_BAD_REQUEST)

        user_instance.weight = weight
        user_instance.save()
        return Response(self.get_serializer(user_instance).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_age(self, request, pk=None):
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        age = request.data.get('age')
        try:
            age = int(age)
            if age <= 0 or age > 150:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'error': 'Invalid age value.'}, status=status.HTTP_400_BAD_REQUEST)

        user_instance.age = age
        user_instance.save()
        return Response(self.get_serializer(user_instance).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_username(self, request, pk=None):
        user_instance = self.get_object()
        self.check_object_permissions(request, user_instance)

        new_username = request.data.get('username')
        if not new_username:
            return Response({'error': 'New username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if DjangoUser.objects.filter(username=new_username).exclude(pk=user_instance.django_user.pk).exists():
            return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        django_user = user_instance.django_user
        django_user.username = new_username
        try:
            django_user.full_clean()
            django_user.save()
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(user_instance).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me_id(self, request):
        """
        Возвращает ID текущего пользователя (core.models.User), если найден.
        Только для авторизованных.
        """
        try:
            # Django user → связанный кастомный пользователь (core.User)
            user_instance = request.user.custom_user
            return Response({'id': user_instance.id})
        except AttributeError:
            return Response({'error': 'Профиль пользователя не найден.'}, status=404)



class MealPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления планами питания.
    Показывает и позволяет управлять ТОЛЬКО планами текущего пользователя.
    """
    serializer_class = MealPlanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список планов питания ТОЛЬКО для текущего
        аутентифицированного пользователя.
        """
        user = self.request.user
        if user and user.is_authenticated and hasattr(user, 'custom_user'):
            # Фильтруем по user (связь напрямую с вашей моделью User)
            return MealPlans.objects.filter(user=user.custom_user)
        return MealPlans.objects.none()

    def perform_create(self, serializer):
        """
        При создании нового плана питания (POST /api/mealplans/),
        автоматически устанавливаем поле 'user' равным текущему
        аутентифицированному пользователю.
        """
        try:
            custom_user_instance = self.request.user.custom_user
            serializer.save(user=custom_user_instance)
        except User.DoesNotExist:
            raise ValidationError("Associated custom user profile not found for the authenticated user.")
        except AttributeError:
            raise PermissionDenied("Cannot determine the associated user profile.")

    @action(detail=True, methods=['get'])
    def meals(self, request, pk=None):
        """
        Получить список блюд для конкретного плана питания.
        GET /api/mealplans/{id}/meals/
        """
        meal_plan = self.get_object()  # Это автоматически проверит права доступа
        meals = meal_plan.meals.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def calculate_calories(self, request, pk=None): 
        """Рассчитать стоимость плана питания""" 
        meal_plan_instance = self.get_object() 
        calories = MealPlanManager.calculate_plan_calories(meal_plan_instance.id)
        return Response({'calories': calories})

class MealViewSet(viewsets.ModelViewSet):
    """API endpoint для управления блюдами"""
    serializer_class = MealSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Переопределяем метод для динамического формирования queryset.
        Добавляем фильтрацию по user_id и meal_plan_id
        """
        queryset = Meals.objects.all()

        # Получаем параметры фильтрации
        meal_plan_id = self.request.query_params.get('meal_plan_id')
        user_id = self.request.query_params.get('user_id')

        # Фильтруем по плану питания
        if meal_plan_id:
            try:
                meal_plan = MealPlans.objects.get(id=meal_plan_id)
                # Проверяем, принадлежит ли план текущему пользователю
                if meal_plan.user == self.request.user.custom_user:
                    queryset = queryset.filter(meal_plans=meal_plan)
                else:
                    return Meals.objects.none()
            except MealPlans.DoesNotExist:
                return Meals.objects.none()

        # Фильтруем по пользователю (через избранное или планы питания)
        if user_id:
            try:
                user_id = int(user_id)
                if user_id == self.request.user.custom_user.id:
                    # Получаем блюда из избранного и планов питания пользователя
                    user_meals = queryset.filter(
                        models.Q(favorites__user_id=user_id) |
                        models.Q(meal_plans__user_id=user_id)
                    ).distinct()
                    return user_meals
                return Meals.objects.none()
            except (ValueError, AttributeError):
                return Meals.objects.none()

        # Фильтрация по типу диеты
        diet_type_id = self.request.query_params.get('diet_type_id')
        if diet_type_id:
            try:
                diet_type_id = int(diet_type_id)
                queryset = queryset.filter(diet_type_id=diet_type_id)
            except ValueError:
                return Meals.objects.none()
            
        # Фильтрация по типу приема пищи (1-завтрак,2-обед,3-ужин)
        type = self.request.query_params.get('type')
        if type:
            try:
                meal_type_val = int(type)
                queryset = queryset.filter(type=meal_type_val)
            except ValueError:
                return Meals.objects.none()

        return queryset

    @action(detail=True, methods=['get'])
    def ingredients(self, request, pk=None):
        """
        Получить список ингредиентов для конкретного блюда.
        Доступ разрешен только если блюдо находится в плане питания пользователя
        или в избранном.
        GET /api/meals/{id}/ingredients/
        """
        meal = self.get_object()
        user = request.user.custom_user

        # Проверяем доступ к блюду
        has_access = (
            meal.meal_plans.filter(user=user).exists() or  # Блюдо в плане питания пользователя
            meal.favorites.filter(user=user).exists()      # Блюдо в избранном пользователя
        )

        if not has_access:
            raise PermissionDenied("You don't have access to this meal's ingredients")

        # Получаем ингредиенты с количеством через MealIngredient
        meal_ingredients = meal.mealingredient_set.all()
        
        # Создаем расширенный список с количеством каждого ингредиента
        ingredients_data = []
        for mi in meal_ingredients:
            ingredient_data = IngredientSerializer(mi.ingredient).data
            ingredient_data['quantity'] = mi.quantity
            ingredients_data.append(ingredient_data)

        return Response(ingredients_data)

    @action(detail=True, methods=['get'])
    def calculate_calories(self, request, pk=None):
        """Рассчитать стоимость блюда"""
        meal_instance = self.get_object()
        calories = MealManager.calculate_meal_calories(meal_instance.id)
        return Response({'calories': calories})

class IngredientViewSet(viewsets.ModelViewSet):
    """API endpoint для управления ингредиентами"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class DietTypeViewSet(viewsets.ModelViewSet):
    """API endpoint для управления типами диет"""
    queryset = DietTypes.objects.all()
    serializer_class = DietTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class FavoriteViewSet(viewsets.ModelViewSet):
    """API endpoint для управления избранными блюдами"""
    # queryset = Favorites.objects.all() # Заменено на get_queryset для фильтрации по пользователю
    serializer_class = FavoriteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Этот viewset должен возвращать список всех избранных для текущего аутентифицированного пользователя."""
        user = self.request.user
        # Убедимся, что у request.user есть custom_user (связь с вашей моделью User)
        if user and user.is_authenticated and hasattr(user, 'custom_user'):
            return Favorites.objects.filter(user=user.custom_user)
        return Favorites.objects.none()

    def perform_create(self, serializer):
        """Связать создаваемое избранное с текущим пользователем."""
        try:
            custom_user_instance = self.request.user.custom_user
        except AttributeError:
            # Если у DjangoUser нет связанного custom_user
            raise PermissionDenied("Пользовательский профиль не определен для аутентифицированного пользователя.")
        
        # serializer.validated_data['meal'] будет содержать экземпляр Meals,
        # так как в FavoriteSerializer поле meal_id использует source='meal'.
        meal_instance = serializer.validated_data.get('meal') 

        if Favorites.objects.filter(user=custom_user_instance, meal=meal_instance).exists():
            # Используем serializers.ValidationError, чтобы DRF вернул корректный 400 ответ
            raise serializers.ValidationError({"detail": "Это блюдо уже в избранном."}) 
            
        serializer.save(user=custom_user_instance)

class LogoutView(APIView):
    """
    API endpoint для выхода из системы.
    Добавляет refresh token в черный список, делая его недействительным.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            # Получаем refresh token из тела запроса
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем объект токена и добавляем его в черный список
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'detail': 'Successfully logged out.'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
def index(request):
    dishes = [
        {'title': 'Овсянка на молоке с бананами'},
        {'title': 'Тушеная рыба с овощами'},
        {'title': 'ПП-бургер'},
        {'title': 'Салат из пасты и тунца'},
    ]
    return render(request, 'index.html', {'dishes': dishes})

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def favorites(request):
    return render(request, 'favorites.html')

def settings(request):
    return render(request, 'settings.html')


def Meals_list(request):
    plan_id = request.GET.get('plan_id')
    if not plan_id:
        return render(request, 'Meals_list.html', {'rows': []})

    plan = get_object_or_404(MealPlans, id=plan_id)

    # Получаем все блюда из плана
    meals = list(
        MealPlanMeal.objects
        .filter(plan=plan)
        .select_related('meal')
        .order_by('id')  # или по дате добавления, если есть
    )

    # Группируем по типам
    breakfasts = [m.meal for m in meals if m.meal.type == 1]
    lunches    = [m.meal for m in meals if m.meal.type == 2]
    dinners    = [m.meal for m in meals if m.meal.type == 3]

    # Формируем список строк по дням
    rows = [
        [(bf, "Завтрак"), (ln, "Обед"), (dn, "Ужин")]
        for bf, ln, dn in zip_longest(breakfasts, lunches, dinners, fillvalue=None)
    ]

    return render(request, 'Meals_list.html', {'rows': rows})

def MealPlan_list(request):
    meal_plans = MealPlans.objects.all().order_by('-created_at')
    # Строим список строк, каждая строка — это три ячейки: (план, метка)
    rows = [
        [(mp, "План питания")]
        for mp in meal_plans
    ]
    return render(request, 'MealPlan_list.html', {'rows': rows})


@csrf_exempt
def create_meal_plan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import random
        from decimal import Decimal
        import json

        data = json.loads(request.body)
        user_id = data.get('user_id')
        total_calories = data.get('total_calories')
        duration_weeks = int(data.get('duration'))

        if not all([user_id, total_calories, duration_weeks]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        user = User.objects.get(id=user_id)
        duration_days = duration_weeks * 7

        # Создаём план
        mealplan = MealPlans.objects.create(
            user=user,
            total_calories=Decimal(str(total_calories)),
            duration=duration_days
        )

        # Цели по калориям
        targets = {
            1: round(total_calories * 0.3),  # Завтрак
            2: round(total_calories * 0.5),  # Обед
            3: round(total_calories * 0.2),  # Ужин
        }

        log = []

        for meal_type in [1, 2, 3]:
            kcal_target = targets[meal_type]
            lower = kcal_target - 50
            upper = kcal_target + 50

            meals = list(Meals.objects.filter(type=meal_type, calories__gte=lower, calories__lte=upper))
            if not meals:
                log.append(f"Нет подходящих по калориям для типа {meal_type} — берём любые")
                meals = list(Meals.objects.filter(type=meal_type))

            if not meals:
                log.append(f"Нет вообще блюд типа {meal_type}, пропускаем всё")
                continue

            # Для каждого дня — добавляем случайное блюдо
            for day in range(1, duration_days + 1):
                selected = random.choice(meals)
                MealPlanMeal.objects.create(plan=mealplan, meal=selected)
                log.append(f"День {day}, тип {meal_type}: {selected.name}")

        # Выводим статистику
        print("📊 План питания сгенерирован:")
        print(f"  Всего дней: {duration_days}")
        print(f"  Ожидается записей: {duration_days * 3}")
        print(f"  Фактически создано: {MealPlanMeal.objects.filter(plan=mealplan).count()}")

        for l in log[-20:]:  # последние 20 строк — чтобы не захламлять
            print(l)

        return JsonResponse({'success': True, 'plan_id': mealplan.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


