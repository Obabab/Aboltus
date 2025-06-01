@echo off


:: Проверка на права администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запуск от имени администратора...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:start
echo === Запуск проекта ===
echo.
echo 1. Сначала выполнить build (пересобрать образы)
echo 2. Только запустить проект (без сборки)
set /p choice="Выберите действие (1-2): "

cd /d %~dp0

:: Очистка порта 5432
call port_clearer.bat

:: Запуск Docker, если он не работает
docker info > nul 2>&1
if errorlevel 1 (
    echo Запускаем Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30
)

if "%choice%"=="1" (
    echo Выполняется build...
    docker-compose build
)

echo Запуск контейнеров...
docker-compose up -d

echo.
echo Проект запущен:
echo Django(сайт проекта):   http://localhost
echo PgAdmin:                http://localhost:5050
echo Press any key to stop the containers...
pause > nul

:: Stop containers
cmd /c docker-compose down
