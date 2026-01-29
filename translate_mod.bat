@echo off
chcp 65001 >nul
echo Переводчик модов Minecraft на русский язык
echo ===========================================
echo.

if "%~1"=="" (
    echo Использование: translate_mod.bat "путь\к\моду" [опции]
    echo.
    echo Примеры:
    echo   translate_mod.bat "C:\mods\MyMod"
    echo   translate_mod.bat "C:\mods\MyMod.jar"
    echo   translate_mod.bat "C:\mods\MyMod" -o "C:\mods\MyMod_RU"
    echo.
    pause
    exit /b 1
)

python translator.py %*

pause
