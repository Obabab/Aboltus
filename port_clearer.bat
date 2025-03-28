@echo off
setlocal

:: Указываем порт, который нужно освободить
set PORT=5432

:: Поиск процесса, занимающего порт
echo Поиск процесса, занимающего порт %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
    set PID=%%a
)

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

endlocal
pause