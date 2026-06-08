@echo off
chcp 65001 > nul
title 🤖 ANNA AI v5.2 - DEUTSCHE VERSION
echo ===============================================
echo    ЗАПУСК ANNA AI v5.2 - DEUTSCHE VERSION
echo    Версия 2.0
echo    Голосовой AutoLM с локальным ИИ
echo ===============================================
echo.

REM Проверка наличия файла
if not exist "app.py" (
    echo ОШИБКА: Файл app.py не найден!
    pause
    exit
)

echo Запуск Streamlit приложения...
streamlit run app.py

pause