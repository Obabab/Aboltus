@echo off
setlocal enabledelayedexpansion

set PORT=5432
set PID=

echo Поиск процесса, занятого портом %PORT%...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    set PID=%%a
    goto kill
)

echo Порт %PORT% не занят.
goto end

:kill
echo Найден PID: %PID%. Завершаем процесс...
taskkill /F /PID !PID!
if !ERRORLEVEL! equ 0 (
    echo Порт %PORT% успешно освобожден.
) else (
    echo Не удалось завершить процесс с PID !PID!.
)

:end
endlocal
