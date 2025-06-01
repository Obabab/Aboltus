import uuid
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User as DjangoUser
from core.models import User, DietTypes, MealPlans, Meals, Ingredients, Favorites

class TestAPIEndpoints(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_username = "testuser_1"
        cls.test_email = "test@example.com"
        cls.test_password = "testpass123"
        client = APIClient()
        data = {
            "username": cls.test_username,
            "password": cls.test_password,
            "email": cls.test_email
        }
        response = client.post('/api/users/', data, format='json')
        assert response.status_code == 201, response.data
        cls.user_id = response.data['id']
        login_response = client.post('/api/token/', {
            "username": cls.test_username,
            "password": cls.test_password
        }, format='json')
        assert login_response.status_code == 200, login_response.data
        cls.token = login_response.data['access']

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.users_url = '/api/users/'
        self.user_me_url = '/api/users/me/'
        self.login_url = '/api/token/'
        self.meal_plan_url = '/api/meal-plans/'
        self.meal_url = '/api/meals/'
        self.ingredient_url = '/api/ingredients/'
        self.diet_type_url = '/api/diet-types/'
        self.favorite_url = '/api/favorites/'

    def tearDown(self):
        self.client.credentials()

    def test_user_me_endpoint(self):
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.test_username)
        self.assertEqual(response.data['email'], self.test_email)

    def test_01_register_user(self):
        self.client.credentials()
        unique_username = f"newuser_{uuid.uuid4().hex[:8]}"
        data = {
            "username": unique_username,
            "password": "newpass123",
            "email": f"{unique_username}@example.com"
        }
        response = self.client.post(self.users_url, data, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('id', response.data)

    def test_02_login_user(self):
        self.client.credentials()
        response = self.client.post(self.login_url, {
            "username": self.test_username,
            "password": self.test_password
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        me = self.client.get(self.user_me_url)
        self.assertEqual(me.status_code, 200)

    def test_03_protected_endpoints_require_jwt(self):
        self.client.credentials()
        public_endpoints = [
            # Здесь не должно быть self.meal_url, если он требует авторизации
        ]
        protected_endpoints = [
            (self.meal_url, 'GET'),
            (self.meal_plan_url, 'GET'),
            (f'{self.meal_plan_url}1/', 'GET'),
            (self.ingredient_url, 'GET'),
            (f'{self.ingredient_url}1/', 'GET'),
            (self.diet_type_url, 'GET'),
            (f'{self.diet_type_url}1/', 'GET'),
            (self.favorite_url, 'GET'),
            (f'{self.favorite_url}1/', 'GET'),
            (self.user_me_url, 'GET'),
            (self.user_me_url, 'PUT'),
            (f'{self.users_url}{self.user_id}/', 'GET'),
            (f'{self.users_url}{self.user_id}/', 'PATCH'),
            (f'{self.users_url}{self.user_id}/verify_password/', 'POST'),
            (f'{self.users_url}{self.user_id}/change_password/', 'POST'),
        ]
        for url, method in public_endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Endpoint {url} ({method}) returned {response.status_code} instead of 200")
        for url, method in protected_endpoints:
            if method == 'GET': response = self.client.get(url)
            elif method == 'POST': response = self.client.post(url, {}, format='json')
            elif method == 'PUT': response = self.client.put(url, {}, format='json')
            elif method == 'PATCH': response = self.client.patch(url, {}, format='json')
            elif method == 'DELETE': response = self.client.delete(url)
            self.assertIn(response.status_code, [401, 404], f"Endpoint {url} ({method}) returned {response.status_code} instead of 401/404")

    def test_04_user_me_endpoint(self):
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_id)
        self.assertEqual(response.data['username'], self.test_username)
        self.assertEqual(response.data['email'], self.test_email)
        put_data = {
            "username": self.test_username,
            "email": "updated.me@example.com",
            "weight": "70.5",
            "height": "175.0",
            "age": 30
        }
        response = self.client.put(self.user_me_url, put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], put_data['email'])
        patch_data = {"age": 31, "weight": "72.3"}
        response = self.client.patch(self.user_me_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['age'], patch_data['age'])
        self.assertEqual(response.data['weight'], patch_data['weight'])

    def test_05_change_password(self):
        new_password = "newtestpass123"
        change_response = self.client.post(
            f'{self.users_url}{self.user_id}/change_password/',
            {'old_password': self.test_password, 'new_password': new_password},
            format='json'
        )
        self.assertEqual(change_response.status_code, status.HTTP_200_OK)
        old_login = self.client.post(self.login_url, {'username': self.test_username, 'password': self.test_password}, format='json')
        self.assertEqual(old_login.status_code, status.HTTP_401_UNAUTHORIZED)
        new_login = self.client.post(self.login_url, {'username': self.test_username, 'password': new_password}, format='json')
        self.assertEqual(new_login.status_code, status.HTTP_200_OK)
        dj_user = DjangoUser.objects.get(username=self.test_username)
        dj_user.set_password(self.test_password)
        dj_user.save()
        self.token = self.client.post(self.login_url, {
            "username": self.test_username,
            "password": self.test_password
        }, format='json').data['access']

    def test_06_diet_type_crud(self):
        diet_type_data = {"name": f"CRUD Diet {uuid.uuid4().hex[:6]}", "description": "Test", "is_restricted": False}
        response = self.client.post(self.diet_type_url, diet_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        diet_type_id = response.data['id']
        response = self.client.get(f'{self.diet_type_url}{diet_type_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], diet_type_data['name'])
        update_data = {"name": f"Updated CRUD Diet {uuid.uuid4().hex[:6]}"}
        response = self.client.patch(f'{self.diet_type_url}{diet_type_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_data['name'])
        response = self.client.delete(f'{self.diet_type_url}{diet_type_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DietTypes.objects.filter(id=diet_type_id).exists())

    def test_07_meal_crud(self):
        diet_type = DietTypes.objects.create(name=f"MealTestDiet{uuid.uuid4().hex[:6]}")
        meal_data = {"name": f"CRUD Meal {uuid.uuid4().hex[:6]}", "price": "12.99", "diet_type_id": diet_type.id}
        response = self.client.post(self.meal_url, meal_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        meal_id = response.data['id']
        response = self.client.get(f'{self.meal_url}{meal_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], meal_data['name'])
        update_data = {"price": "15.50"}
        response = self.client.patch(f'{self.meal_url}{meal_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['price']), 15.50)
        response = self.client.delete(f'{self.meal_url}{meal_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Meals.objects.filter(id=meal_id).exists())
        diet_type.delete()

    def test_08_ingredient_crud(self):
        ing_data = {"name": f"CRUD Ing {uuid.uuid4().hex[:6]}", "price_per_unit": "1.25", "unit": "kg"}
        response = self.client.post(self.ingredient_url, ing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ing_id = response.data['id']
        response = self.client.get(f'{self.ingredient_url}{ing_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], ing_data['name'])
        update_data = {"price_per_unit": "1.50"}
        response = self.client.patch(f'{self.ingredient_url}{ing_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['price_per_unit']), 1.50)
        response = self.client.delete(f'{self.ingredient_url}{ing_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredients.objects.filter(id=ing_id).exists())

    def test_09_meal_plan_crud(self):
        diet_type = DietTypes.objects.create(name=f"PlanTestDiet{uuid.uuid4().hex[:6]}")
        meal = Meals.objects.create(name=f"PlanTestMeal{uuid.uuid4().hex[:6]}", price=10.0, diet_type=diet_type)
        meal_plan_data = {"duration": 7, "total_price": 99.99, "meal_ids": [meal.id]}
        response = self.client.post(self.meal_plan_url, meal_plan_data, format='json')
        print('DEBUG meal_plan_crud response:', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        meal_plan_id = response.data['id']
        response = self.client.get(f"{self.meal_plan_url}{meal_plan_id}/meals/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], meal.id)
        response = self.client.delete(f'{self.meal_plan_url}{meal_plan_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MealPlans.objects.filter(id=meal_plan_id).exists())
        meal.delete()
        diet_type.delete()

    def test_10_favorite_crud(self):
        diet_type = DietTypes.objects.create(name=f"FavTestDiet{uuid.uuid4().hex[:6]}")
        meal = Meals.objects.create(name=f"FavTestMeal{uuid.uuid4().hex[:6]}", price=9.99, diet_type=diet_type)
        fav_data = {"meal_id": meal.id}
        response = self.client.post(self.favorite_url, fav_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        fav_id = response.data['id']
        response_dup = self.client.post(self.favorite_url, fav_data, format='json')
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response_dup.data)
        response = self.client.get(f'{self.favorite_url}{fav_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['meal']['id'], meal.id)
        response = self.client.delete(f'{self.favorite_url}{fav_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorites.objects.filter(id=fav_id).exists())
        meal.delete()
        diet_type.delete()

    def test_11_verify_password(self):
        url = f'{self.users_url}{self.user_id}/verify_password/'
        response = self.client.post(url, {'password': self.test_password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])
        response = self.client.post(url, {'password': 'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_99_delete_user(self):
        delete_url = f'{self.users_url}{self.user_id}/'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DjangoUser.objects.filter(username=self.test_username).exists())
        self.assertFalse(User.objects.filter(id=self.user_id).exists()) 