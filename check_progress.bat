@echo off
chcp 65001 >nul
echo Проверка прогресса перевода...
echo.

REM Проверяем наличие переведенного .jar файла
if exist "hexcasting-forge-1.20.1-0.11.3_ru.jar" (
    echo ✓ Переведенный файл найден: hexcasting-forge-1.20.1-0.11.3_ru.jar
    echo.
    dir "hexcasting-forge-1.20.1-0.11.3_ru.jar"
) else (
    echo ⏳ Переведенный файл еще не создан. Процесс перевода продолжается...
    echo.
    echo Проверяем запущенные процессы Python...
    tasklist | findstr /i "py.exe python"
)

echo.
pause
