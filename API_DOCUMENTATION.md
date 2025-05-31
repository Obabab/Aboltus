# 🍽️ Полная документация API (Django REST Framework)

## 🔐 Аутентификация

| Метод | URL                   | Auth | Описание                          |
| ----- | --------------------- | ---- | --------------------------------- |
| POST  | `/api/token/`         | ❌    | Получить JWT токен (логин)        |
| POST  | `/api/token/refresh/` | ❌    | Обновить access токен             |
| POST  | `/api/logout/`        | ✅    | Выйти (требуется `refresh_token`) |

**Пример запроса (POST /api/token/):**

```json
{
  "username": "danii",
  "password": "secret123"
}
```

**Ответ:**

```json
{
  "refresh": "...",
  "access": "..."
}
```

**POST /api/logout/**

```json
{
  "refresh_token": "..."
}
```

---

## 👤 Пользователь (`UserViewSet`)

Базовый маршрут: `/api/users/`

### 🔸 POST `/api/users/` — Регистрация пользователя

**Auth:** ❌

```json
{
  "username": "danii",
  "password": "secret123",
  "email": "danii@example.com",
  "first_name": "Даниил",
  "weight": 100.0,
  "height": 195.0,
  "age": 20,
  "diet_type_id": 1
}
```

Ответ:

```json
{
  "id": 7,
  "username": "danii",
  "email": "danii@example.com",
  "first_name": "Даниил",
  "weight": 100.0,
  "height": 195.0,
  "age": 20,
  "diet_type_id": 1
}
```

### 🔸 GET `/api/users/me_id/`

```json
{
  "id": 7
}
```

### 🔸 POST `/api/users/{id}/verify_password/`

```json
{ "password": "secret123" }
```

Ответ:

```json
{ "is_valid": true }
```

### 🔸 POST `/api/users/{id}/change_password/`

```json
{
  "old_password": "secret123",
  "new_password": "newpass456"
}
```

Ответ:

```json
{ "detail": "Password successfully changed" }
```

### 🔸 PATCH `/api/users/{id}/change_height/`

```json
{ "height": 192.5 }
```

### 🔸 PATCH `/api/users/{id}/change_weight/`

```json
{ "weight": 95.0 }
```

### 🔸 PATCH `/api/users/{id}/change_age/`

```json
{ "age": 21 }
```

### 🔸 PATCH `/api/users/{id}/change_username/`

```json
{ "username": "new_username" }
```

---

## 🧮 План питания (`MealPlanViewSet`)

Базовый маршрут: `/api/mealplans/`

### 🔸 POST `/api/mealplans/`

**Auth:** ✅

```json
{
  "duration": 14,
  "total_calories": 2500,
  "meal_ids": [1, 2, 3]
}
```

### 🔸 GET `/api/mealplans/`

Ответ:

```json
[
  {
    "id": 5,
    "user": {...},
    "duration": 14,
    "total_calories": 2500,
    "meals": [ ... ]
  }
]
```

### 🔸 GET `/api/mealplans/{id}/meals/`

Ответ:

```json
[
  { "id": 1, "name": "Овсянка", ... },
  { "id": 2, "name": "Курица с рисом", ... }
]
```

### 🔸 GET `/api/mealplans/{id}/calculate_calories/`

```json
{ "calories": 2435 }
```

---

## 🍽️ Блюда (`MealViewSet`)

Базовый маршрут: `/api/meals/`

### 🔸 POST `/api/meals/`

```json
{
  "name": "ПП-бургер",
  "description": "Полезный бургер",
  "calories": 600,
  "type": 2,
  "ingredient_ids": [1, 3],
  "diet_type_id": 1
}
```

### 🔸 GET `/api/meals/?user_id=7&type=1`

Ответ:

```json
[
  {
    "id": 3,
    "name": "Овсянка",
    "description": "Овсянка с молоком",
    "calories": 300,
    "type": 1,
    "ingredients": [ ... ],
    "diet_type": {...}
  }
]
```

### 🔸 GET `/api/meals/{id}/ingredients/`

Ответ:

```json
[
  {
    "id": 1,
    "name": "Овсяные хлопья",
    "calories_per_unit": 350,
    "unit": "г"
  },
  ...
]
```

### 🔸 GET `/api/meals/{id}/calculate_calories/`

```json
{ "calories": 598.2 }
```

---

## 🧂 Ингредиенты (`IngredientViewSet`)

Базовый маршрут: `/api/ingredients/`

Пример POST:

```json
{
  "name": "Куриное филе",
  "calories_per_unit": 165,
  "unit": "г",
  "store_name": "Пятёрочка",
  "valid_from": "2025-01-01"
}
```

---

## 🥗 Типы диет (`DietTypeViewSet`)

Базовый маршрут: `/api/diettypes/`

Пример POST:

```json
{
  "name": "Кето",
  "description": "Много жиров, мало углеводов",
  "is_restricted": true
}
```

---

## ❤️ Избранное (`FavoriteViewSet`)

Базовый маршрут: `/api/favorites/`

### 🔸 POST `/api/favorites/`

```json
{ "meal_id": 5 }
```

### 🔸 GET `/api/favorites/`

```json
[
  {
    "id": 1,
    "user": { ... },
    "meal": { "id": 5, "name": "Овсянка" }
  }
]
```

---

## ⚙️ Дополнительный маршрут: `/create_meal_plan/`

### 🔸 POST

```json
{
  "user_id": 7,
  "total_calories": 2500,
  "duration": 2
}
```

Ответ:

```json
{
  "success": true,
  "plan_id": 12
}
```

Создаёт план питания с подбором блюд по калорийности и типу приёма пищи.
