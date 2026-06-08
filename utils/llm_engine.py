"""
LLM Engine — локальный ИИ через Ollama
Понимает любые вопросы на естественном языке
"""

import requests
import re
import pandas as pd
from typing import Dict, Optional


class LLMEngine:
    """Локальный языковой модели для ответов на любые вопросы"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.is_available = False
        self._check_availability()
    
    def _check_availability(self):
        """Проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                
                if self.model in model_names:
                    self.is_available = True
                    print(f"✅ LLM доступен: {self.model}")
                else:
                    print(f"⚠️ Модель {self.model} не найдена. Установите: ollama pull {self.model}")
            else:
                print("⚠️ Ollama не запущен. Запустите: ollama serve")
        except:
            print("⚠️ Не удалось подключиться к Ollama")
    
    def ask(self, question: str, context: Dict = None) -> str:
        """Задать любой вопрос"""
        if not self.is_available:
            return self._fallback_response(question)
        
        system_prompt = self._get_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nПользователь: {question}\n\nАнна:"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 512}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                answer = response.json().get('response', '')
                answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
                return answer.strip()
            else:
                return f"❌ Ошибка: {response.status_code}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)[:100]}"
    
    def ask_about_data(self, question: str, df: pd.DataFrame, model_info: Dict = None) -> str:
        """Вопрос о загруженных данных"""
        context = {
            'rows': len(df) if df is not None else 0,
            'cols': len(df.columns) if df is not None else 0,
            'columns': df.columns.tolist()[:10] if df is not None else [],
            'numeric_cols': len(df.select_dtypes(include=['number']).columns) if df is not None else 0,
            'missing_total': df.isnull().sum().sum() if df is not None else 0,
            'task_type': model_info.get('task_type', 'не определена') if model_info else 'не определена',
            'model_trained': model_info.get('is_trained', False) if model_info else False,
        }
        return self.ask(question, context)
    
    def _get_system_prompt(self, context: Dict = None) -> str:
        """Системный промпт"""
        prompt = """Ты — Анна, дружелюбный AI-ассистент по анализу данных и машинному обучению.
Отвечай кратко, понятно, на русском языке. Используй эмодзи.
Будь вежливой и полезной."""
        
        if context:
            prompt += f"""

КОНТЕКСТ О ДАННЫХ:
- Строк: {context.get('rows', 'нет')}
- Колонок: {context.get('cols', 'нет')}
- Колонки: {', '.join(context.get('columns', [])[:5])}
- Пропусков: {context.get('missing_total', 0)}
- Тип задачи: {context.get('task_type', 'не определена')}
- Модель обучена: {'да' if context.get('model_trained') else 'нет'}

Учитывай этот контекст при ответе."""
        
        return prompt
    
    def _fallback_response(self, question: str) -> str:
        """Ответ при недоступности LLM"""
        return f"""🤔 Вы спросили: "{question[:100]}..."

⚠️ **LLM не доступен!**

Для ответов на любые вопросы:
1. Установите Ollama: https://ollama.com
2. Скачайте модель: `ollama pull mistral`
3. Запустите: `ollama serve`
4. Перезапустите приложение

Пока я знаю только команды. Скажите "помощь"."""
    
    def is_ready(self) -> bool:
        return self.is_available