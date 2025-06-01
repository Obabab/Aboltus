| Endpoint                                      | Method   | Description                                                  |
|----------------------------------------------|----------|--------------------------------------------------------------|
| /api/users/                                   | GET      | Получить список пользователей (staff)                        |
| /api/users/                                   | POST     | Регистрация нового пользователя                              |
| /api/users/{id}/                               | GET      | Получить информацию о пользователе                           |
| /api/users/{id}/                               | PATCH    | Обновить пользователя                                        |
| /api/users/{id}/                               | DELETE   | Удалить пользователя                                         |
| /api/users/{id}/verify_password/              | POST     | Проверка пароля                                              |
| /api/users/{id}/change_password/              | POST     | Изменение пароля                                             |
| /api/users/{id}/change_height/                | PATCH    | Изменение роста                                              |
| /api/users/{id}/change_weight/                | PATCH    | Изменение веса                                               |
| /api/users/{id}/change_age/                   | PATCH    | Изменение возраста                                           |
| /api/users/{id}/change_username/              | PATCH    | Изменение имени пользователя                                 |
| /api/users/me_id/                             | GET      | Получить ID текущего пользователя                            |
| /api/meal-plans/                              | GET      | Список планов текущего пользователя                          |
| /api/meal-plans/                              | POST     | Создание плана питания                                       |
| /api/meal-plans/{id}/                         | GET      | Получить план питания                                        |
| /api/meal-plans/{id}/                         | PATCH    | Обновить план питания                                        |
| /api/meal-plans/{id}/                         | DELETE   | Удалить план питания                                         |
| /api/meal-plans/{id}/meals/                   | GET      | Блюда из плана питания                                       |
| /api/meal-plans/{id}/calculate_calories/      | GET      | Рассчитать калорийность плана                                |
| /api/meals/                                   | GET      | Список блюд (фильтрация по meal_plan_id, user_id и др.)     |
| /api/meals/                                   | POST     | Создание блюда                                               |
| /api/meals/{id}/                               | GET      | Получить блюдо                                               |
| /api/meals/{id}/                               | PATCH    | Обновить блюдо                                               |
| /api/meals/{id}/                               | DELETE   | Удалить блюдо                                                |
| /api/meals/{id}/ingredients/                  | GET      | Получить ингредиенты блюда (если доступ разрешён)           |
| /api/meals/{id}/calculate_calories/           | GET      | Рассчитать калории блюда                                     |
| /api/ingredients/                             | GET      | Список ингредиентов                                          |
| /api/ingredients/                             | POST     | Создать ингредиент                                           |
| /api/ingredients/{id}/                         | GET      | Получить ингредиент                                          |
| /api/ingredients/{id}/                         | PATCH    | Обновить ингредиент                                          |
| /api/ingredients/{id}/                         | DELETE   | Удалить ингредиент                                           |
| /api/diet-types/                              | GET      | Список типов диет                                            |
| /api/diet-types/                              | POST     | Создать тип диеты                                            |
| /api/diet-types/{id}/                          | GET      | Получить тип диеты                                           |
| /api/diet-types/{id}/                          | PATCH    | Обновить тип диеты                                           |
| /api/diet-types/{id}/                          | DELETE   | Удалить тип диеты                                            |
| /api/favorites/                               | GET      | Список избранных блюд текущего пользователя                 |
| /api/favorites/                               | POST     | Добавить блюдо в избранное                                   |
| /api/favorites/{id}/                           | GET      | Получить избранное блюдо                                     |
| /api/favorites/{id}/                           | PATCH    | Обновить избранное блюдо                                     |
| /api/favorites/{id}/                           | DELETE   | Удалить из избранного                                        |
| /api/token/                                   | POST     | Получение JWT-токена (логин)                                 |
| /api/token/refresh/                           | POST     | Обновление JWT-токена                                        |
| /api/token/verify/                            | POST     | Проверка валидности токена                                   |
| /api/token/blacklist/                         | POST     | Занесение refresh токена в черный список                    |
| /api/logout/                                  | POST     | Выход из системы (logout)                                    |
| /api/create_meal_plan/                        | POST     | Генерация плана питания по калориям и длительности           |
