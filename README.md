# 🤖 ANNA HYPERACTIVE AutoML

**Версия 2.0** | Голосовой AutoML ассистент с локальным ИИ

## 📖 О программе

ANNA HYPERACTIVE AutoML — это интеллектуальный голосовой ассистент для автоматического машинного обучения. Программа умеет:

- 📊 **Анализировать данные** (CSV, Excel)
- 🤖 **Автоматически выбирать лучшие модели ML** (Random Forest, LightGBM, CatBoost, SVM, и др.)
- ⚡ **Работать в гиперактивном режиме** с латентностью < 100 мс
- 🎤 **Понимать голосовые команды** (более 50 команд)
- 🧠 **Отвечать на любые вопросы** через локальный LLM (Ollama)
- 📈 **Строить 3D графики и HTML дашборды**
- 🔮 **Объяснять предсказания** (SHAP, Feature Importance)

## 🚀 Быстрый старт

### Установка

```bash
# 1. Клонировать или скачать проект

# 2. Установить зависимости
pip install -r requirements.txt

# 3. (Опционально) Установить Ollama для умных ответов
# Windows: скачать с https://ollama.com
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 4. Скачать модель (если установлен Ollama)
ollama pull mistral

# 5. Запустить Ollama (в отдельном терминале)
ollama serve

# 6. Запустить Анну
streamlit run app.py