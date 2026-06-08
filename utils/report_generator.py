"""
Report Generator — HTML дашборды и отчёты
"""

import pandas as pd
import numpy as np
import os
import base64
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


class ReportGenerator:
    """Генерация HTML отчётов"""
    
    @staticmethod
    def generate_html_dashboard(df: pd.DataFrame, model=None, metrics=None, feature_importance=None) -> str:
        """Создаёт HTML дашборд"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Генерация графиков
        plots_html = ""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:4]
        
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
            ax.set_title(f'Распределение: {col}')
            
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = base64.b64encode(buf.read()).decode()
            plt.close()
            
            plots_html += f'<img src="data:image/png;base64,{img}" style="width:45%; margin:1%; border-radius:10px;">\n'
        
        # HTML шаблон
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📊 Отчёт Анны AutoML</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg,#667eea,#764ba2); color: white; padding: 30px; border-radius: 20px; text-align: center; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric {{ font-size: 2em; color: #667eea; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 ANNA HYPERACTIVE AutoML</h1>
            <p>Отчёт сгенерирован: {timestamp}</p>
        </div>
        
        <div class="card">
            <h2>📈 Информация о данных</h2>
            <p><b>Строк:</b> {len(df)}</p>
            <p><b>Колонок:</b> {len(df.columns)}</p>
            <p><b>Числовых колонок:</b> {len(df.select_dtypes(include=[np.number]).columns)}</p>
        </div>
"""
        
        if metrics:
            html += f"""
        <div class="card">
            <h2>🤖 Модель ML</h2>
            <p><b>Метрика:</b> <span class="metric">{metrics:.4f}</span></p>
            <p><b>Тип задачи:</b> {model.task_type if model else 'неизвестно'}</p>
        </div>
"""
        
        if plots_html:
            html += f"""
        <div class="card">
            <h2>📊 Визуализации</h2>
            {plots_html}
        </div>
"""
        
        html += f"""
        <div class="card">
            <h2>📋 Предпросмотр данных</h2>
            {df.head(10).to_html()}
        </div>
    </div>
</body>
</html>
"""
        # Сохранение
        os.makedirs('outputs/reports', exist_ok=True)
        path = f'outputs/reports/dashboard_{datetime.now():%Y%m%d_%H%M%S}.html'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return path