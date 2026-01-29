@echo off
chcp 65001 >nul
echo ===========================================
echo Установка зависимостей для переводчика модов
echo ===========================================
echo.

REM Проверяем наличие Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Найден Python, используем: python
    python --version
    echo.
    echo Устанавливаем зависимости...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    goto :end
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Найден Python, используем: py
    py --version
    echo.
    echo Устанавливаем зависимости...
    py -m pip install --upgrade pip
    py -m pip install -r requirements.txt
    goto :end
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Найден Python, используем: python3
    python3 --version
    echo.
    echo Устанавливаем зависимости...
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    goto :end
)

echo ОШИБКА: Python не найден!
echo.
echo Пожалуйста, установите Python 3.7 или выше:
echo 1. Скачайте с https://www.python.org/downloads/
echo 2. При установке отметьте "Add Python to PATH"
echo 3. Запустите этот скрипт снова
echo.
pause
exit /b 1

:end
echo.
echo ===========================================
echo Установка завершена!
echo ===========================================
echo.
pause
