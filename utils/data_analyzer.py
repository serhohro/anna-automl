"""
Data Analyzer — активные предложения на основе данных
"""

import pandas as pd
import numpy as np


class DataAnalyzer:
    """Анализирует данные и предлагает действия"""
    
    @staticmethod
    def analyze_and_suggest(df: pd.DataFrame) -> list:
        """Возвращает список предложений"""
        suggestions = []
        
        if df is None or df.empty:
            return suggestions
        
        # Пропуски
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            suggestions.append({
                'type': 'missing',
                'title': f"🔍 Найдены пропуски в {len(missing_cols)} колонках",
                'message': f"Колонка '{missing_cols[0]}' имеет {df[missing_cols[0]].isnull().sum()} пропусков",
                'actions': [{'name': 'Заполнить', 'action': 'fillna_mean'}]
            })
        
        # Выбросы
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outliers_found = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            if len(outliers) > 0:
                outliers_found.append({'col': col, 'count': len(outliers)})
        
        if outliers_found:
            top = max(outliers_found, key=lambda x: x['count'])
            suggestions.append({
                'type': 'outliers',
                'title': f"⚠️ Обнаружены выбросы",
                'message': f"В колонке '{top['col']}' найдено {top['count']} выбросов",
                'actions': [{'name': 'Показать', 'action': 'show_outliers'}]
            })
        
        # Предложение обучить модель
        if len(df) > 20 and len(numeric_cols) >= 1:
            suggestions.append({
                'type': 'suggest_train',
                'title': "🤖 Хотите обучить модель?",
                'message': f"У вас {len(df)} строк и {len(numeric_cols)} числовых признаков",
                'actions': [{'name': 'Обучить', 'action': 'train_model'}]
            })
        
        return suggestions