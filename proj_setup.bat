@echo off
cd /d %~dp0

:: 0. Освобождаем порт 5432 для работы базы данных
call port_clearer.bat

:: 1. Создаём виртуальное окружение
python -m venv venv

:: 2. Активируем виртуальное окружение
call venv\Scripts\activate

:: 3. Запускаем Docker Compose
docker-compose up -d

:: 4. Устанавливаем зависимости
pip install -r requirements.txt

:: 5. Генерируем миграцию
alembic revision --autogenerate -m "add new table"

:: 6. Применяем миграции
alembic upgrade head

:: 7. Завершаем скрипт
echo.
echo [INFO] Проект настроен и готов к работе!
cmd /k

