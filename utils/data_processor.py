"""
Data Processor — очистка и подготовка данных
"""

import pandas as pd
import numpy as np


class DataProcessor:
    """Обработка и очистка данных"""
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Базовая очистка"""
        df = df.copy()
        df = df.drop_duplicates()
        
        for col in df.columns:
            if df[col].nunique() == 1:
                df = df.drop(columns=[col])
        
        return df
    
    @staticmethod
    def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
        """Обработка пропусков"""
        df = df.copy()
        
        for col in df.columns:
            missing_pct = df[col].isnull().mean()
            if missing_pct > 0.5:
                df = df.drop(columns=[col])
            elif missing_pct > 0:
                if df[col].dtype in ['int64', 'float64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')
        
        return df
    
    @staticmethod
    def get_info(df: pd.DataFrame) -> dict:
        """Информация о данных"""
        return {
            'rows': len(df),
            'cols': len(df.columns),
            'numeric': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical': df.select_dtypes(include=['object']).columns.tolist(),
            'missing': df.isnull().sum().to_dict()
        }