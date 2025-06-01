@echo off
echo Building project...

:: Переход в директорию проекта
cd /d %~dp0

:: Очистка порта (на всякий случай)
call backend\port_clearer.bat

:: Проверка запуска Docker
docker info > nul 2>&1
if errorlevel 1 (
    echo Запускаем Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30
)

:: Сборка всех образов
docker-compose build

echo Build завершён.
pause
