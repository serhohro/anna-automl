"""
NLP Parser — распознавание голосовых команд
"""

import re


class NLPParser:
    """Парсер естественного языка для команд"""
    
    COMMANDS = {
        'show_data': ['покажи данные', 'head', 'первые строки', 'что внутри', 'покажи таблицу'],
        'shape': ['сколько строк', 'размер данных', 'shape', 'размерность'],
        'stats': ['статистика', 'describe', 'среднее', 'описание'],
        'missing': ['пропуски', 'null', 'nan', 'пустые значения'],
        'feature_importance': ['важность признаков', 'feature importance', 'какие колонки важны', 'что влияет'],
        'confusion_matrix': ['матрица ошибок', 'confusion matrix', 'качество классификации'],
        'shap_explain': ['объясни предсказание', 'shap', 'почему модель так решила'],
        'plot_3d': ['3d график', 'трёхмерный', '3d plot'],
        'generate_dashboard': ['создать дашборд', 'html отчёт', 'dashboard'],
        'train_all': ['сравни все модели', 'выбери лучшую модель', 'анна выбери лучшую'],
        'help': ['помощь', 'help', 'что ты умеешь', 'команды', 'список команд'],
        'new_features': ['что нового', 'новые возможности', 'обновления'],
        'sound_off': ['выключи звук', 'sound off', 'тишина', 'mute'],
        'sound_on': ['включи звук', 'sound on', 'звук включи', 'unmute'],
        'greeting': ['привет анна', 'здравствуй анна', 'hi anna', 'привет'],
        'thank': ['спасибо', 'thanks', 'thank you', 'молодец'],
        'unknown': []
    }
    
    @classmethod
    def parse(cls, text: str) -> str:
        """Распознать команду из текста"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower().strip()
        
        for command, keywords in cls.COMMANDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return command
        
        return 'unknown'
    
    @classmethod
    def extract_column(cls, text: str, columns: list) -> str:
        """Извлечь название колонки"""
        if not columns:
            return None
        
        text_lower = text.lower()
        for col in columns:
            if col.lower() in text_lower:
                return col
        return None
    
    @classmethod
    def get_command_description(cls, command: str) -> str:
        """Описание команды"""
        descriptions = {
            'show_data': '📊 Показываю первые строки',
            'shape': '📏 Размер датасета',
            'stats': '📈 Статистика данных',
            'missing': '🔍 Поиск пропусков',
            'feature_importance': '⭐ Важность признаков',
            'confusion_matrix': '🎯 Матрица ошибок',
            'shap_explain': '🔮 SHAP объяснение',
            'plot_3d': '🎮 3D график',
            'generate_dashboard': '📄 HTML дашборд',
            'train_all': '🏆 Поиск лучшей модели',
            'help': '🤖 Список команд',
        }
        return descriptions.get(command, '🤔 Неизвестная команда')