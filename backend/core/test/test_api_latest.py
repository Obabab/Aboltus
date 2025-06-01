import uuid # Для уникальности имен других ресурсов в тестах
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User as DjangoUser
from core.models import User, DietTypes, MealPlans, Meals, Ingredients, Favorites

class TestAPIEndpoints(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/'
        self.login_url = '/api/token/'
        self.meal_plan_url = '/api/meal-plans/'
        self.meal_url = '/api/meals/'
        self.ingredient_url = '/api/ingredients/'
        self.diet_type_url = '/api/diet-types/'
        self.favorite_url = '/api/favorites/'

        # Используем фиксированные, но уникальные для тестового запуска данные
        # чтобы избежать случайных пересечений, если tearDown не всегда срабатывает идеально
        # или если тесты запускаются параллельно в будущем.
        # Но для основной проверки удаления, можно использовать и полностью статичные.
        # Я оставлю генерацию, т.к. это более надежно в сложных сценариях.
        unique_suffix = uuid.uuid4().hex[:8]
        self.test_username = f"testuser_{unique_suffix}"
        self.test_email = f"test_{unique_suffix}@example.com"
        self.test_password = "testpass123"

        self.user_data_for_setup = {
            "username": self.test_username,
            "password": self.test_password,
            "email": self.test_email
            # 'weight', 'height', 'age' можно добавить, если нужно при регистрации
        }
        
        # Убедимся, что такого пользователя нет перед регистрацией в setUp
        DjangoUser.objects.filter(username=self.test_username).delete() # Каскадно удалит User и Profile

        register_response = self.client.post(self.register_url, self.user_data_for_setup, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED, 
                         f"Failed to register user in setUp: {register_response.data}")
        
        # registered_user_id это ID от core.models.User
        self.registered_user_id = register_response.data['id'] 
        # Проверим, что DjangoUser и CoreUser действительно созданы
        self.assertTrue(DjangoUser.objects.filter(username=self.test_username).exists())
        self.assertTrue(User.objects.filter(id=self.registered_user_id, django_user__username=self.test_username).exists())


        login_response = self.client.post(self.login_url, {
            'username': self.test_username,
            'password': self.test_password
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK,
                         f"Failed to login user in setUp: {login_response.data}")
        self.token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.base_diet_type = DietTypes.objects.create(
            name=f"Base Test Diet {unique_suffix}",
            description="Base Test Diet Description",
            is_restricted=False
        )

    def tearDown(self):
        self.client.credentials() # Сброс токена
        # Объекты, созданные в setUp (пользователь, base_diet_type),
        # должны удаляться либо в своих тестах (если они специфичны для теста),
        # либо в последнем тесте "очистки", либо здесь как "последняя линия обороны".
        # Так как test_99_delete_registered_user_via_api должен удалить пользователя,
        # здесь мы можем попытаться удалить base_diet_type.

        # Попытка удалить base_diet_type, если он еще существует
        if hasattr(self, 'base_diet_type') and DietTypes.objects.filter(pk=self.base_diet_type.pk).exists():
            self.base_diet_type.delete()

        # Дополнительная очистка пользователя из setUp на случай, если тест удаления не был запущен или упал
        # Это должно быть избыточным, если test_99 работает.
        if hasattr(self, 'test_username'):
            dj_user = DjangoUser.objects.filter(username=self.test_username).first()
            if dj_user:
                dj_user.delete() # Каскадно удалит User и Profile

    def test_01_register_user_again_with_different_data(self):
        """Тест регистрации нового, другого пользователя"""
        self.client.credentials() 

        unique_suffix_test = uuid.uuid4().hex[:8]
        new_user_data = {
            "username": f"anotheruser_{unique_suffix_test}",
            "password": "anotherpassword",
            "email": f"another_{unique_suffix_test}@example.com"
        }
        
        DjangoUser.objects.filter(username=new_user_data['username']).delete() # Предочистка

        response = self.client.post(self.register_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        
        created_django_user = DjangoUser.objects.filter(username=new_user_data['username'])
        self.assertTrue(created_django_user.exists())
        # Проверка, что core.User тоже создан (через UserManager и сериализатор)
        self.assertTrue(User.objects.filter(django_user=created_django_user.first()).exists())
        
        # Очистка созданного в этом тесте
        created_django_user.first().delete() # Каскадно удалит User и Profile

    def test_02_login_registered_user(self):
        """Тест входа пользователя, зарегистрированного в setUp"""
        self.client.credentials()
        
        response = self.client.post(
            self.login_url,
            {'username': self.test_username, 'password': self.test_password},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)

    def test_03_protected_endpoints_require_jwt(self):
        """Тест проверки защиты эндпоинтов"""
        self.client.credentials()
        
        common_endpoints = [
            (self.meal_plan_url, 'GET'), (f'{self.meal_plan_url}1/', 'GET'), # Предполагаем, что ID 1 может не существовать, но важен сам факт 401
            (self.meal_url, 'GET'), (f'{self.meal_url}1/', 'GET'),
            (self.ingredient_url, 'GET'), (f'{self.ingredient_url}1/', 'GET'),
            (self.diet_type_url, 'GET'), (f'{self.diet_type_url}1/', 'GET'),
            (self.favorite_url, 'GET'), (f'{self.favorite_url}1/', 'GET'),
        ]
        user_specific_endpoints = [
             (f'/api/users/{self.registered_user_id}/', 'GET'),
             (f'/api/users/{self.registered_user_id}/', 'PATCH', {'email': 'new@example.com'}), # Нужно тело для PATCH
             (f'/api/users/{self.registered_user_id}/verify_password/', 'POST', {'password': 'any'}),
             (f'/api/users/{self.registered_user_id}/', 'DELETE'),
        ]

        for url, method, *data_arg in common_endpoints + user_specific_endpoints:
            data = data_arg[0] if data_arg else {}
            if method == 'GET': response = self.client.get(url)
            elif method == 'POST': response = self.client.post(url, data, format='json')
            elif method == 'PATCH': response = self.client.patch(url, data, format='json')
            elif method == 'DELETE': response = self.client.delete(url)
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, 
                             f"Endpoint {url} ({method}) did not return 401. Got {response.status_code}: {response.data}")

    def test_04_diet_type_crud_with_jwt(self):
        """Тест CRUD операций для типов диет"""
        diet_type_data = {"name": f"CRUD Diet {uuid.uuid4().hex[:6]}", "description": "Test", "is_restricted": False}
        
        response_create = self.client.post(self.diet_type_url, diet_type_data, format='json')
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED, response_create.data)
        diet_type_id = response_create.data['id']

        response_read = self.client.get(f'{self.diet_type_url}{diet_type_id}/')
        self.assertEqual(response_read.status_code, status.HTTP_200_OK)
        self.assertEqual(response_read.data['name'], diet_type_data['name'])

        update_data = {"name": f"Updated CRUD Diet {uuid.uuid4().hex[:6]}"}
        response_update = self.client.patch(f'{self.diet_type_url}{diet_type_id}/', update_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_update.data['name'], update_data['name'])

        response_delete = self.client.delete(f'{self.diet_type_url}{diet_type_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DietTypes.objects.filter(id=diet_type_id).exists())

    def test_05_meal_plan_crud_with_jwt(self):
        """Тест CRUD операций для планов питания"""
        meal_plan_data = {"user_id": self.registered_user_id, "duration": 5, "total_price": "50.0"}
        
        response_create = self.client.post(self.meal_plan_url, meal_plan_data, format='json')
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED, response_create.data)
        meal_plan_id = response_create.data['id']

        response_read = self.client.get(f'{self.meal_plan_url}{meal_plan_id}/')
        self.assertEqual(response_read.status_code, status.HTTP_200_OK)
        self.assertEqual(response_read.data['user_id'], self.registered_user_id)

        update_data = {"total_price": "75.5"}
        response_update = self.client.patch(f'{self.meal_plan_url}{meal_plan_id}/', update_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response_update.data['total_price']), 75.5)

        response_delete = self.client.delete(f'{self.meal_plan_url}{meal_plan_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MealPlans.objects.filter(id=meal_plan_id).exists())

    def test_06_meal_crud_with_jwt(self):
        """Тест CRUD операций для блюд"""
        meal_data = {
            "name": f"CRUD Meal {uuid.uuid4().hex[:6]}", 
            "price": "12.99", 
            "diet_type_id": self.base_diet_type.id
        }
        response_create = self.client.post(self.meal_url, meal_data, format='json')
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED, response_create.data)
        meal_id = response_create.data['id']

        response_read = self.client.get(f'{self.meal_url}{meal_id}/')
        self.assertEqual(response_read.status_code, status.HTTP_200_OK)
        self.assertEqual(response_read.data['name'], meal_data['name'])

        update_data = {"price": "15.50"}
        response_update = self.client.patch(f'{self.meal_url}{meal_id}/', update_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response_update.data['price']), 15.50)

        response_delete = self.client.delete(f'{self.meal_url}{meal_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Meals.objects.filter(id=meal_id).exists())

    def test_07_ingredient_crud_with_jwt(self):
        """Тест CRUD операций для ингредиентов"""
        ing_data = {
            "name": f"CRUD Ing {uuid.uuid4().hex[:6]}", 
            "price_per_unit": "1.25", 
            "unit": "kg"
        }
        response_create = self.client.post(self.ingredient_url, ing_data, format='json')
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED, response_create.data)
        ing_id = response_create.data['id']

        response_read = self.client.get(f'{self.ingredient_url}{ing_id}/')
        self.assertEqual(response_read.status_code, status.HTTP_200_OK)
        self.assertEqual(response_read.data['name'], ing_data['name'])

        update_data = {"price_per_unit": "1.50"}
        response_update = self.client.patch(f'{self.ingredient_url}{ing_id}/', update_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response_update.data['price_per_unit']), 1.50)

        response_delete = self.client.delete(f'{self.ingredient_url}{ing_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredients.objects.filter(id=ing_id).exists())

    def test_08_favorite_crud_with_jwt(self):
        """Тест CRUD операций для избранных блюд"""
        meal_for_fav = Meals.objects.create(
            name=f"Fav Meal {uuid.uuid4().hex[:6]}", 
            price="9.99", 
            diet_type=self.base_diet_type
        )
        fav_data = {"user_id": self.registered_user_id, "meal_id": meal_for_fav.id}
        
        response_create = self.client.post(self.favorite_url, fav_data, format='json')
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED, response_create.data)
        fav_id = response_create.data['id']

        response_read = self.client.get(f'{self.favorite_url}{fav_id}/')
        self.assertEqual(response_read.status_code, status.HTTP_200_OK)
        self.assertEqual(response_read.data['user_id'], self.registered_user_id)
        self.assertEqual(response_read.data['meal_id'], meal_for_fav.id)

        response_delete = self.client.delete(f'{self.favorite_url}{fav_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorites.objects.filter(id=fav_id).exists())
        
        meal_for_fav.delete() # Очистка блюда, созданного для этого теста

    def test_09_user_verify_password(self):
        """Тест проверки пароля пользователя из setUp"""
        url = f'/api/users/{self.registered_user_id}/verify_password/'
        
        response_valid = self.client.post(url, {'password': self.test_password}, format='json')
        self.assertEqual(response_valid.status_code, status.HTTP_200_OK, response_valid.data)
        self.assertTrue(response_valid.data['is_valid'])

        response_invalid = self.client.post(url, {'password': 'wrongpassword'}, format='json')
        # API должен вернуть 200 OK, но is_valid: false
        self.assertEqual(response_invalid.status_code, status.HTTP_200_OK, response_invalid.data) 
        self.assertFalse(response_invalid.data['is_valid'])

        response_no_pass = self.client.post(url, {}, format='json')
        self.assertEqual(response_no_pass.status_code, status.HTTP_400_BAD_REQUEST, response_no_pass.data)

    def test_99_delete_registered_user_via_api(self):
        """Тест удаления пользователя, созданного в setUp, через API"""
        user_to_delete_id = self.registered_user_id 
        django_user_username_to_check = self.test_username

        # Проверяем, что пользователь существует перед удалением
        self.assertTrue(User.objects.filter(id=user_to_delete_id).exists(), "CoreUser не найден перед удалением")
        self.assertTrue(DjangoUser.objects.filter(username=django_user_username_to_check).exists(), "DjangoUser не найден перед удалением")

        # Выполняем DELETE запрос
        response = self.client.delete(f'/api/users/{user_to_delete_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 
                         f"API delete user failed: {response.data if response and response.content else 'No response content'}")

        # Проверяем, что пользователь действительно удален из обеих таблиц
        self.assertFalse(User.objects.filter(id=user_to_delete_id).exists(), 
                         "core.User запись не была удалена после API вызова.")
        self.assertFalse(DjangoUser.objects.filter(username=django_user_username_to_check).exists(),
                         "django.contrib.auth.models.User запись не была удалена после API вызова.")