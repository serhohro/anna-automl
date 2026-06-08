#!/bin/bash

echo "==============================================="
echo "   ЗАПУСК ANNA HYPERACTIVE AutoML"
echo "   Версия 2.0"
echo "==============================================="

if [ ! -f "app.py" ]; then
    echo "ОШИБКА: Файл app.py не найден!"
    exit 1
fi

echo "Запуск Streamlit приложения..."
streamlit run app.py