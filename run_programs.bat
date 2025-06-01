::@echo off
::call python -m venv venv
call venv\Scripts\activate.bat
::call pip install -r backend\requirements.txt
:: Меню команд
:menu
cls
echo ==== Управление Django-проектом в Docker ====
echo 1. Django shell
::echo 2. Run tests
::echo 3. Run API tests
echo 4. Заполнить БД (filler.py)
echo 5. Очистить БД (bd_eraser.py)
echo 6. Make migrations
echo 7. Apply migrations
echo 8. Открыть терминал
echo 9. Положить проект
echo 0. Exit
echo =============================================

set /p choice="Выбор: "

cd /d %~dp0

if "%choice%"=="1" python backend/manage.py shell
::if "%choice%"=="2" python backend/manage.py test
::if "%choice%"=="3" pytest backend/core/test/test_api_new.py -v
if "%choice%"=="4" python backend/core/filler.py
if "%choice%"=="5" python backend/core/bd_eraser.py
if "%choice%"=="6" python backend/manage.py makemigrations
if "%choice%"=="7" python backend/manage.py migrate
if "%choice%"=="8" goto ssshhh
if "%choice%"=="9" docker-compose down
if "%choice%"=="0" exit

pause
goto menu
:ssshhh
cmd