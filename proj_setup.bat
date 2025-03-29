@echo off
cd /d %~dp0

:: 0. Освобождаем порт 5432 для работы базы данных
call port_clearer.bat

:: 1. Запускаем Docker Desktop
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 20 /nobreak

:: 2. Создаём виртуальное окружение
python -m venv venv

:: 3. Активируем виртуальное окружение
call venv\Scripts\activate

:: 4. Запускаем Docker
docker-compose up -d

:: 5. Устанавливаем зависимости
pip install -r requirements.txt

:: 6. Генерируем миграцию
alembic revision --autogenerate -m "add new table"

:: 7. Применяем миграции
alembic upgrade head

:: 8. Завершаем скрипт
echo.
echo [INFO] Проект настроен и готов к работе!
cmd /k

