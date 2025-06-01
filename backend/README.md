# Обзор проекта

#######manage.py#########

## Файл manage.py

Файл `manage.py` является важной частью Django-проекта. Он служит точкой входа для выполнения административных задач, таких как запуск сервера разработки, миграции базы данных и другие команды Django.

### Структура файла

```python
#!/usr/bin/env python
```
Эта строка указывает на то, что скрипт должен быть выполнен с использованием интерпретатора Python, который находится в пути окружения.

```python
"""Django's command-line utility for administrative tasks."""
```
Это строка документации, которая описывает назначение файла.

```python
import os
import sys
```
Эти модули необходимы для работы с системными функциями и переменными окружения.

### Функция main()

```python
def main():
    """Run administrative tasks."""
```
Функция `main()` служит для выполнения административных задач. Она устанавливает переменную окружения `DJANGO_SETTINGS_MODULE`, которая указывает на файл настроек Django.

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```
Эта строка устанавливает значение по умолчанию для переменной окружения `DJANGO_SETTINGS_MODULE`, указывая на модуль настроек проекта.

```python
try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc
```
Этот блок кода пытается импортировать функцию `execute_from_command_line` из модуля `django.core.management`. Если импорт не удается, выбрасывается исключение с сообщением об ошибке, указывающим на возможные причины.

```python
execute_from_command_line(sys.argv)
```
Эта строка выполняет команду, переданную в командной строке, используя аргументы, переданные скрипту.

### Запуск скрипта

```python
if __name__ == '__main__':
    main()
```
Этот блок кода проверяет, что скрипт выполняется как основная программа, и вызывает функцию `main()`. Это стандартный способ запуска скриптов в Python.

#######Dockerfile#########

## Файл Dockerfile

`Dockerfile` используется для создания образа Docker, который содержит все необходимые зависимости и настройки для запуска приложения.

### Структура файла

```dockerfile
# Use Python 3.11 slim image as the base image
FROM python:3.11-slim-bullseye as builder
```
Эта строка указывает на использование базового образа Python 3.11 slim, который является легковесной версией операционной системы с установленным Python.

```dockerfile
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive
```
Эти переменные окружения:
- `PYTHONDONTWRITEBYTECODE=1` предотвращает создание файлов .pyc.
- `PYTHONUNBUFFERED=1` обеспечивает немедленный вывод в терминал.
- `DEBIAN_FRONTEND=noninteractive` отключает интерактивный режим для apt-get.

```dockerfile
# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
```
Этот блок устанавливает системные зависимости, необходимые для работы приложения, и очищает кеши для уменьшения размера образа.

```dockerfile
# Set working directory
WORKDIR /app
```
Устанавливает рабочую директорию `/app` внутри контейнера.

```dockerfile
# Copy only requirements to cache them in docker layer
COPY requirements.txt .
```
Копирует файл `requirements.txt` для установки зависимостей Python.

```dockerfile
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
```
Устанавливает Python-зависимости, указанные в `requirements.txt`.

```dockerfile
# Create and switch to a non-root user
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django
```
Создает пользователя `django` и переключается на него для повышения безопасности.

```dockerfile
# Copy project files
COPY --chown=django:django . .
```
Копирует все файлы проекта в контейнер.

```dockerfile
# Expose port 8000
EXPOSE 8000
```
Открывает порт 8000 для доступа к приложению.

```dockerfile
# Create volume for static and media files
VOLUME ["/app/staticfiles", "/app/media"]
```
Создает тома для хранения статических и медиафайлов.

```dockerfile
# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```
Указывает команду для запуска приложения на сервере разработки.

#######docker-compose.yml#########

## Файл docker-compose.yml

`docker-compose.yml` используется для определения и запуска многоконтейнерных Docker приложений. Он описывает сервисы, сети и тома, необходимые для работы приложения.

### Структура файла

```yaml
version: '3.8'
```
Указывает версию синтаксиса Docker Compose.

#### Сервисы

```yaml
services:
```
Определяет список сервисов, которые будут запущены в контейнерах.

##### Сервис db

```yaml
db:
  image: postgres:15-alpine
  container_name: postgres_db
  restart: unless-stopped
```
Этот сервис использует образ PostgreSQL и будет перезапущен, если остановится.

```yaml
environment:
  POSTGRES_DB: mydatabase
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: laygon
```
Устанавливает переменные окружения для настройки базы данных PostgreSQL.

```yaml
ports:
  - "5432:5432"
```
Пробрасывает порт 5432 для доступа к базе данных.

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```
Использует том для хранения данных базы данных.

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d mydatabase"]
```
Определяет проверку состояния для базы данных.

##### Сервис pgadmin

```yaml
pgadmin:
  image: dpage/pgadmin4:latest
  container_name: pgadmin
```
Этот сервис предоставляет веб-интерфейс для управления PostgreSQL.

```yaml
environment:
  PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@example.com}
  PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-changeme}
```
Устанавливает учетные данные по умолчанию для доступа к pgAdmin.

##### Сервис web

```yaml
web:
  build:
    context: .
    dockerfile: Dockerfile
```
Собирает образ для веб-приложения на основе `Dockerfile`.

```yaml
command: >
  sh -c "
    echo 'Waiting for database...' &&
    sleep 15 &&
    python manage.py migrate &&
    python manage.py collectstatic --noinput &&
    python manage.py runserver 0.0.0.0:8000
  "
```
Выполняет команды для подготовки и запуска Django-приложения.

##### Сервис nginx

```yaml
nginx:
  image: nginx:alpine
  container_name: nginx
```
Этот сервис использует Nginx для проксирования запросов к веб-приложению.

#### Сети и тома

```yaml
networks:
  app_network:
    driver: bridge
```
Определяет сеть для взаимодействия сервисов.

```yaml
volumes:
  postgres_data:
  pgadmin_data:
  static_volume:
  media_volume:
```
Определяет тома для хранения данных и статических файлов.

#######requirements.txt#########

## Файл requirements.txt

`requirements.txt` содержит список зависимостей Python, необходимых для работы проекта. Каждая строка указывает на пакет и его версию, которые должны быть установлены.

### Зависимости

```plaintext
Django==5.0.2
```
Django — это высокоуровневый веб-фреймворк на Python, который способствует быстрому развитию и чистому, прагматичному дизайну.

```plaintext
psycopg2-binary==2.9.10
```
Psycopg2 — это адаптер базы данных PostgreSQL для языка программирования Python.

```plaintext
python-dotenv==1.0.1
```
Python-dotenv позволяет загружать переменные окружения из файла `.env`.

```plaintext
faker==37.0.2
```
Faker — это библиотека Python, которая генерирует фальшивые данные для вас.

```plaintext
werkzeug==3.1.3
```
Werkzeug — это библиотека WSGI для Python, которая используется для создания веб-приложений.

```plaintext
pytest==8.3.5
```
Pytest — это фреймворк для тестирования, который позволяет писать простые и масштабируемые тесты.

```plaintext
python-decouple==3.8
```
Python-decouple помогает отделить настройки от кода.

```plaintext
dj_database_url==2.3.0
```
Dj-database-url позволяет легко настроить базу данных Django с помощью URL-адреса.

```plaintext
dotenv==0.9.9
```
Dotenv — это еще одна библиотека для работы с переменными окружения из файла `.env`.

```plaintext
djangorestframework==3.14.0
```
Django REST Framework — это мощный и гибкий инструмент для создания веб-API.

```plaintext
django-cors-headers==4.3.1
```
Django CORS Headers — это приложение для обработки заголовков CORS в Django.

```plaintext
gunicorn==21.2.0
```
Gunicorn — это WSGI HTTP сервер для UNIX, который запускает Python веб-приложения.

```plaintext
whitenoise==6.6.0
```
WhiteNoise позволяет вашему веб-приложению Django обслуживать свои собственные статические файлы.

```plaintext
djangorestframework_simplejwt==5.5.0
```
Django REST Framework SimpleJWT предоставляет простой способ работы с JWT токенами в Django REST Framework.

#######.env#########

## Файл .env

Файл `.env` используется для хранения конфиденциальных данных и настроек, которые не должны быть включены в кодовую базу. Он позволяет легко изменять параметры конфигурации без изменения кода.

### Переменные окружения

```plaintext
DEBUG=True
```
Переменная `DEBUG` включает режим отладки в Django, что полезно для разработки, но не рекомендуется для продакшн-среды.

```plaintext
SECRET_KEY=django-insecure-%7gbz_4ky_syv#l*s2z^c&1r927&au@ml#kb5z!sibav#v82nk
```
`SECRET_KEY` используется Django для криптографических операций. В продакшн-среде этот ключ должен быть уникальным и защищенным.

```plaintext
DATABASE_URL=postgresql://postgres:laygon@db:5432/mydatabase
```
`DATABASE_URL` определяет строку подключения к базе данных PostgreSQL, включая пользователя, пароль, хост и имя базы данных.

```plaintext
ALLOWED_HOSTS=127.0.0.1,localhost
```
`ALLOWED_HOSTS` задает список хостов, которые могут обращаться к приложению. Это важно для безопасности.

Дополнительные переменные могут быть добавлены по мере необходимости для настройки других аспектов приложения.

#######start_project.bat#########

## Файл start_project.bat

`start_project.bat` — это сценарий командной оболочки Windows, который автоматизирует процесс запуска проекта Django с использованием Docker и виртуального окружения.

### Структура файла

```batch
@echo off
echo Starting Django Project...
```
Отключает вывод команд и выводит сообщение о начале запуска проекта.

```batch
:: Change to the project directory
cd /d %~dp0
```
Переключается в директорию проекта.

```batch
:: Clear port 5432 for PostgreSQL
call port_clearer.bat
```
Вызывает скрипт для очистки порта 5432, который использует PostgreSQL.

```batch
:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
```
Создает виртуальное окружение, если оно еще не существует.

```batch
:: Activate virtual environment
call venv\Scripts\activate
```
Активирует виртуальное окружение.

```batch
:: Install dependencies
pip install -r requirements.txt
```
Устанавливает зависимости из файла `requirements.txt`.

```batch
:: Check if Docker Desktop is running
docker info > nul 2>&1
```
Проверяет, запущен ли Docker Desktop.

```batch
:: Stop any running containers
cmd /c docker-compose down
```
Останавливает все запущенные контейнеры.

```batch
:: Remove old containers and volumes
cmd /c docker-compose down -v
cmd /c docker system prune -f
```
Удаляет старые контейнеры и тома, очищает систему Docker.

```batch
:: Build and start containers
cmd /c docker-compose build --no-cache
cmd /c docker-compose up -d
```
Собирает и запускает контейнеры в фоновом режиме.

```batch
:: Wait for services to be ready
timeout /t 10 /nobreak
```
Ждет, пока сервисы будут готовы к использованию.

```batch
:: Check container status
cmd /c docker-compose ps
```
Проверяет статус контейнеров.

```batch
:: Show logs if there are issues
cmd /c docker-compose logs web
```
Показывает логи контейнера веб-приложения, если есть проблемы.

```batch
echo Project is running!
echo Django app: http://localhost:8000
echo PgAdmin: http://localhost:5050
```
Выводит сообщение о том, что проект запущен, и URL-адреса для доступа к приложениям.

```batch
:: Stop containers
cmd /c docker-compose down
```
Останавливает контейнеры при завершении работы.

```batch
:: Deactivate virtual environment
deactivate
```
Деактивирует виртуальное окружение.

#######port_clearer.bat#########

## Файл port_clearer.bat

`port_clearer.bat` — это сценарий командной оболочки Windows, который освобождает указанный порт, завершая процесс, который его занимает.

### Структура файла

```batch
@echo off
setlocal
```
Отключает вывод команд и устанавливает локальный контекст для переменных.

```batch
:: Указываем порт, который нужно освободить
set PORT=5432
```
Устанавливает переменную `PORT` на значение 5432, что соответствует порту PostgreSQL.

```batch
:: Поиск процесса, занимающего порт
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
    set PID=%%a
)
```
Использует команду `netstat` для поиска процесса, который занимает указанный порт, и сохраняет его PID.

```batch
:: Проверка, найден ли PID
if defined PID (
    echo Найден процесс с PID=%PID%, занимающий порт %PORT%.
    echo Завершение процесса...
    taskkill /PID %PID% /F
    if %ERRORLEVEL% equ 0 (
        echo Порт %PORT% успешно освобожден.
    ) else (
        echo Не удалось завершить процесс. Ошибка: %ERRORLEVEL%
    )
) else (
    echo Порт %PORT% не занят.
)
```
Проверяет, найден ли процесс, и если да, завершает его с помощью команды `taskkill`. Выводит сообщение об успешном освобождении порта или об ошибке, если процесс не удалось завершить.

#######API_DOCUMENTATION.md#########

## Документация API

`API_DOCUMENTATION.md` содержит информацию о доступных API-эндпоинтах, их использовании и требованиях к аутентификации.

### Базовый URL

```plaintext
http://localhost:8000/api/
```
Это базовый URL для всех API-запросов.

### Аутентификация

API использует аутентификацию JWT (JSON Web Token). Все эндпоинты, кроме регистрации и входа, требуют аутентификации.

#### Получение JWT токена

1. Зарегистрируйте пользователя (если он еще не зарегистрирован).
2. Получите JWT токен, войдя в систему.
3. Включите токен в заголовок Authorization для всех защищенных эндпоинтов.

##### Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
  }'
```
Этот запрос создает нового пользователя.

##### Вход и получение токена

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```
Этот запрос возвращает JWT токены для доступа к защищенным ресурсам.

##### Обновление токена

Когда токен доступа истекает (через 60 минут), вы можете получить новый, используя refresh токен.

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

### Использование токена

Для всех защищенных эндпоинтов включите токен доступа в заголовок Authorization:

```bash
curl -X GET http://localhost:8000/api/diet-types/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Эндпоинты пользователей

#### Создание пользователя (Регистрация - Аутентификация не требуется)

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
  }'
```

#### Получение пользователя (Требуется аутентификация)

```bash
curl -X GET http://localhost:8000/api/users/{user_id}/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### Обновление пользователя (Требуется аутентификация)

```bash
curl -X PATCH http://localhost:8000/api/users/{user_id}/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "weight": 75.0,
    "height": 180
  }'
```

#### Удаление пользователя (Требуется аутентификация)

```bash
curl -X DELETE http://localhost:8000/api/users/{user_id}/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#######models.py#########

## Модели данных (models.py)

Файл `models.py` содержит определения моделей данных, которые представляют структуру базы данных для приложения.

### Модель DietTypes

```python
class DietTypes(models.Model):
    name = models.TextField(null=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    is_restricted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель описывает типы диет, включая их название, описание и флаг ограничения.

### Модель User

```python
class User(models.Model):
    django_user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='custom_user')
    weight = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    height = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    diet_type = models.ForeignKey(DietTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель расширяет стандартную модель пользователя Django, добавляя поля для веса, роста, возраста и типа диеты.

### Модель Profile

```python
class Profile(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='profile')
    site_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile')
    created_at = models.DateTimeField(default=timezone.now)
```
Модель профиля связывает пользователя Django с дополнительной информацией о сайте.

### Модель MealPlans

```python
class MealPlans(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    duration = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель описывает планы питания, включая пользователя, продолжительность и общую стоимость.

### Модель Meals

```python
class Meals(models.Model):
    name = models.TextField(null=False)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    diet_type = models.ForeignKey(DietTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name="meals")
    created_at = models.DateTimeField(default=timezone.now)
```
Модель описывает блюда, включая их название, описание, цену и тип диеты.

### Модель Ingredients

```python
class Ingredients(models.Model):
    name = models.TextField(null=False)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    unit = models.CharField(max_length=20, null=False)
    store_name = models.TextField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель описывает ингредиенты, включая их название, цену за единицу и магазин.

### Модель Favorites

```python
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(default=timezone.now)
```
Модель описывает избранные блюда пользователя.

### Промежуточные модели

#### MealPlanMeal

```python
class MealPlanMeal(models.Model):
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    plan = models.ForeignKey(MealPlans, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель связывает блюда с планами питания.

#### MealIngredient

```python
class MealIngredient(models.Model):
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    created_at = models.DateTimeField(default=timezone.now)
```
Эта модель связывает ингредиенты с блюдами, указывая количество.

#######views.py#########

## Представления (views.py)

Файл `views.py` содержит определения представлений, которые обрабатывают HTTP-запросы и возвращают HTTP-ответы. Он использует Django REST Framework для создания API.

### UserViewSet

```python
class UserViewSet(viewsets.ModelViewSet):
    """API endpoint для управления пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
```
Этот класс предоставляет CRUD операции для модели `User`. Он использует JWT для аутентификации.

#### verify_password

```python
@action(detail=True, methods=['post'])
def verify_password(self, request, pk=None):
    """Проверить пароль пользователя"""
```
Эта функция проверяет пароль пользователя, используя `UserManager`.

### MealPlanViewSet

```python
class MealPlanViewSet(viewsets.ModelViewSet):
    """API endpoint для управления планами питания"""
    queryset = MealPlans.objects.all()
    serializer_class = MealPlanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```
Этот класс предоставляет CRUD операции для модели `MealPlans`.

#### calculate_price

```python
@action(detail=True, methods=['get'])
def calculate_price(self, request, pk=None):
    """Рассчитать стоимость плана питания"""
```
Эта функция рассчитывает стоимость плана питания, используя `MealPlanManager`.

### MealViewSet

```python
class MealViewSet(viewsets.ModelViewSet):
    """API endpoint для управления блюдами"""
    queryset = Meals.objects.all()
    serializer_class = MealSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```
Этот класс предоставляет CRUD операции для модели `Meals`.

#### calculate_price

```python
@action(detail=True, methods=['get'])
def calculate_price(self, request, pk=None):
    """Рассчитать стоимость блюда"""
```
Эта функция рассчитывает стоимость блюда, используя `MealManager`.

### IngredientViewSet

```python
class IngredientViewSet(viewsets.ModelViewSet):
    """API endpoint для управления ингредиентами"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```
Этот класс предоставляет CRUD операции для модели `Ingredients`.

### DietTypeViewSet

```python
class DietTypeViewSet(viewsets.ModelViewSet):
    """API endpoint для управления типами диет"""
    queryset = DietTypes.objects.all()
    serializer_class = DietTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```
Этот класс предоставляет CRUD операции для модели `DietTypes`.

### FavoriteViewSet

```python
class FavoriteViewSet(viewsets.ModelViewSet):
    """API endpoint для управления избранными блюдами"""
    queryset = Favorites.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```
Этот класс предоставляет CRUD операции для модели `Favorites`.

#######serializers.py#########

## Сериализаторы (serializers.py)

Файл `serializers.py` содержит определения сериализаторов, которые преобразуют сложные типы данных, такие как модели Django, в нативные типы данных Python, которые затем могут быть легко преобразованы в JSON или XML.

### UserSerializer

```python
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
```
Этот сериализатор управляет данными пользователя, включая создание и обновление пользователей через `UserManager`.

### MealPlanSerializer

```python
class MealPlanSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
```
Этот сериализатор управляет данными планов питания, включая идентификатор пользователя, продолжительность и общую стоимость.

### MealSerializer

```python
class MealSerializer(serializers.ModelSerializer):
```
Этот сериализатор управляет данными блюд, включая название, описание, цену и тип диеты.

### IngredientSerializer

```python
class IngredientSerializer(serializers.ModelSerializer):
```
Этот сериализатор управляет данными ингредиентов, включая название, цену за единицу, единицу измерения и магазин.

### DietTypeSerializer

```python
class DietTypeSerializer(serializers.ModelSerializer):
```
Этот сериализатор управляет данными типов диет, включая название, описание и флаг ограничения.

### FavoriteSerializer

```python
class FavoriteSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    meal_id = serializers.IntegerField(required=True)
```
Этот сериализатор управляет данными избранных блюд, связывая пользователя с блюдом.

#######config/urls.py#########

## Конфигурация URL маршрутизации (config/urls.py)

Файл `urls.py` в директории `config` определяет маршрутизацию URL для всего проекта Django, связывая URL-адреса с соответствующими представлениями и обработчиками.

### Основные разделы

#### Импорт модулей

- **admin**: Включает административный интерфейс Django.
- **include**: Позволяет включать другие конфигурации URL.
- **TokenObtainPairView и TokenRefreshView**: Обеспечивают обработку JWT токенов для аутентификации.

#### Настройка маршрутизатора

```python
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('meal-plans', MealPlanViewSet, basename='meal-plan')
router.register('meals', MealViewSet, basename='meal')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('diet-types', DietTypeViewSet, basename='diet-type')
router.register('favorites', FavoriteViewSet, basename='favorite')
```
Этот код создает маршрутизатор и регистрирует наборы представлений, связывая их с соответствующими URL-путями.

#### Определение URL-путей

```python
urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```
Этот код включает URL-адреса для API, административного интерфейса и JWT аутентификации.

#######functions.py#########

## Управляющие классы (functions.py)

Файл `functions.py` содержит классы-менеджеры, которые инкапсулируют бизнес-логику для управления различными аспектами приложения, такими как пользователи, планы питания, блюда и ингредиенты.

### UserManager

```python
class UserManager:
    """Класс для управления пользователями"""
```
Этот класс предоставляет методы для создания, обновления и удаления пользователей, а также для проверки паролей.

#### create_user

```python
@staticmethod
def create_user(username: str, password: str, email: str, ...):
    """Создает нового пользователя"""
```
Создает нового пользователя в системе, включая Django пользователя и связанный профиль.

### MealPlanManager

```python
class MealPlanManager:
    """Класс для управления планами питания"""
```
Этот класс предоставляет методы для создания, получения и удаления планов питания, а также для расчета их стоимости.

#### calculate_plan_price

```python
@staticmethod
def calculate_plan_price(plan_id: int) -> float:
    """Рассчитывает стоимость плана питания"""
```
Рассчитывает общую стоимость плана питания на основе связанных блюд.

### MealManager

```python
class MealManager:
    """Класс для управления блюдами"""
```
Этот класс предоставляет методы для создания, получения и удаления блюд, а также для расчета их стоимости.

#### calculate_meal_price

```python
@staticmethod
def calculate_meal_price(meal_id: int) -> float:
    """Рассчитывает стоимость блюда на основе ингредиентов"""
```
Рассчитывает стоимость блюда на основе связанных ингредиентов и их количества.

### IngredientManager

```python
class IngredientManager:
    """Класс для управления ингредиентами"""
```
Этот класс предоставляет методы для создания, получения и удаления ингредиентов.

### DietTypeManager

```python
class DietTypeManager:
    """Класс для управления типами диет"""
```
Этот класс предоставляет методы для создания, получения и удаления типов диет.

### FavoriteManager

```python
class FavoriteManager:
    """Класс для управления избранными блюдами"""
```
Этот класс предоставляет методы для создания, получения и удаления избранных блюд.

### PriceManager

```python
class PriceManager:
    """Класс для управления ценами"""
```
Этот класс предоставляет методы для обновления цен на блюда и планы питания.

#######filler.py#########

## Скрипт заполнения базы данных (filler.py)

Файл `filler.py` используется для автоматического заполнения базы данных случайными данными с использованием библиотеки Faker. Это полезно для тестирования и разработки.

### Основные функции

#### generate_random_date

```python
def generate_random_date():
    # Generate timezone-aware date
```
Эта функция генерирует случайную дату в пределах последнего года.

#### generate_unique_username

```python
def generate_unique_username():
```
Генерирует уникальное имя пользователя, проверяя его наличие в базе данных.

#### create_diet_types

```python
def create_diet_types():
```
Создает случайные типы диет и сохраняет их в базе данных.

#### create_users

```python
def create_users(diet_types):
```
Создает случайных пользователей, связывая их с типами диет.

#### create_meals

```python
def create_meals(diet_types):
```
Создает случайные блюда, связывая их с типами диет.

#### create_meal_plans

```python
def create_meal_plans(users, meals):
```
Создает случайные планы питания, добавляя в них блюда.

#### create_favorites

```python
def create_favorites(users, meals):
```
Создает избранные блюда для пользователей.

#### create_ingredients

```python
def create_ingredients():
```
Создает случайные ингредиенты и сохраняет их в базе данных.

#### create_meal_ingredients

```python
def create_meal_ingredients(meals, ingredients):
```
Добавляет ингредиенты к блюдам, создавая связи между ними.

### populate_database

```python
def populate_database():
    try:
        with transaction.atomic():
```
Эта функция оборачивает все операции в транзакцию, чтобы обеспечить целостность данных при заполнении базы.

#######bd_eraser.py#########

## Скрипт очистки базы данных (bd_eraser.py)

Файл `bd_eraser.py` используется для удаления всех данных из базы данных, что полезно для сброса состояния базы данных во время разработки или тестирования.

### Основные функции

#### clear_database

```python
def clear_database():
    try:
        with transaction.atomic():
```
Эта функция удаляет все данные из базы данных в правильном порядке, начиная с зависимых таблиц, чтобы избежать ошибок целостности.

- Удаляет связи между блюдами и ингредиентами.
- Удаляет связи между планами и блюдами.
- Удаляет избранные блюда.
- Удаляет планы питания.
- Удаляет блюда.
- Удаляет ингредиенты.
- Удаляет пользователей сайта и их профили.
- Удаляет пользователей Django.
- Удаляет типы диет.

Функция оборачивает все операции в транзакцию, чтобы обеспечить целостность данных при очистке базы.

#######tests.py#########

## Тестирование (tests.py)

Файл `tests.py` предназначен для написания тестов, которые проверяют корректность работы приложения. Он использует модуль `TestCase` из Django для создания тестовых случаев.

### Основные функции

- **TestCase**: Базовый класс для написания тестов в Django, который предоставляет методы для проверки ожидаемых результатов и управления тестовой базой данных.

#######apps.py#########

## Конфигурация приложения (apps.py)

Файл `apps.py` используется для конфигурации приложения в Django. Он определяет класс конфигурации приложения, который наследуется от `AppConfig`.

### Основные функции

- **CoreConfig**: Класс конфигурации для приложения `core`, который задает настройки по умолчанию, такие как `default_auto_field` и имя приложения.

#######settings.py#########

## Конфигурация настроек Django (settings.py)

Файл `settings.py` содержит конфигурацию для Django-приложения, включая настройки базы данных, приложений, промежуточного ПО и других параметров.

### Основные разделы

#### Базовые настройки

- **BASE_DIR**: Определяет базовую директорию проекта.
- **SECRET_KEY**: Секретный ключ для криптографических операций.
- **DEBUG**: Включает или отключает режим отладки.
- **ALLOWED_HOSTS**: Список хостов, которым разрешено обращаться к приложению.

#### Приложения

- **INSTALLED_APPS**: Список приложений, установленных в проекте, включая стандартные приложения Django и сторонние библиотеки.

#### Промежуточное ПО

- **MIDDLEWARE**: Список промежуточного ПО, которое обрабатывает запросы и ответы.

#### База данных

- **DATABASES**: Настройки подключения к базе данных PostgreSQL, включая имя базы данных, пользователя, пароль и хост.

#### Статические и медиа файлы

- **STATIC_URL** и **MEDIA_URL**: URL-адреса для доступа к статическим и медиафайлам.
- **STATICFILES_DIRS** и **MEDIA_ROOT**: Директории для хранения статических и медиафайлов.

#### REST Framework

- **REST_FRAMEWORK**: Настройки для Django REST Framework, включая классы аутентификации.

#### CORS

- **CORS_ALLOW_ALL_ORIGINS**: Разрешает все источники при включенном режиме отладки.
- **CORS_ALLOWED_ORIGINS**: Список разрешенных источников для CORS.

#### Безопасность

- **SECURE_SSL_REDIRECT** и другие параметры безопасности: Включаются в продакшн-среде для обеспечения безопасности приложения.

#### JWT

- **SIMPLE_JWT**: Настройки для JSON Web Token, включая время жизни токенов и типы токенов.

#######config/config.py#########

## Конфигурация приложения (config/config.py)

Файл `config.py` используется для управления конфигурационными настройками приложения, такими как URL-адрес базы данных.

### Основные функции

- **DATABASE_URL**: Получает URL-адрес базы данных из переменных окружения с использованием библиотеки `decouple`, что позволяет легко изменять настройки без изменения кода.

#######config/wsgi.py#########

## Конфигурация WSGI (config/wsgi.py)

Файл `wsgi.py` используется для развертывания Django-приложения. Он определяет точку входа для WSGI-сервера, который обрабатывает запросы к приложению.

### Основные функции

- **application**: Объект WSGI-приложения, который используется сервером для обработки запросов. Он создается с помощью функции `get_wsgi_application()` из Django.

#######config/asgi.py#########

## Конфигурация ASGI (config/asgi.py)

Файл `asgi.py` используется для развертывания Django-приложения с поддержкой ASGI. Он определяет точку входа для ASGI-сервера, который обрабатывает асинхронные запросы к приложению.

### Основные функции

- **application**: Объект ASGI-приложения, который используется сервером для обработки асинхронных запросов. Он создается с помощью функции `get_asgi_application()` из Django. 