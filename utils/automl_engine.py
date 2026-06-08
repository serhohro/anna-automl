"""
SuperAutoML Engine — автоматическое машинное обучение
Поддерживает: Random Forest, Gradient Boosting, LightGBM, CatBoost, Linear, SVM, KNN
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, f1_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
import warnings
import joblib
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# LightGBM
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

# CatBoost
try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

warnings.filterwarnings('ignore')


class SuperAutoML:
    """
    Главный класс AutoML
    Автоматически определяет тип задачи, обрабатывает данные, обучает модели
    """
    
    def __init__(self):
        self.model = None
        self.best_params = None
        self.is_trained = False
        self.task_type = None
        self.scaler = StandardScaler()
        self.imputer_num = SimpleImputer(strategy='mean')
        self.feature_names = []
        self.last_metric = None
        self.dummy_columns = None
        self.target_encoder = None
        self.all_models_results = {}
        self.best_model_name = None
        self.feature_importance_df = None
        self.shap_explainer = None
        self.X_train_scaled = None
        
    def _get_model(self, model_name, task_type):
        """Возвращает модель по имени"""
        model_name = model_name.lower()
        
        models = {
            'random_forest': {
                'classification': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
                'regression': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            },
            'gradient_boosting': {
                'classification': GradientBoostingClassifier(random_state=42),
                'regression': GradientBoostingRegressor(random_state=42)
            },
            'linear': {
                'classification': LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
                'regression': LinearRegression()
            },
            'ridge': {
                'classification': LogisticRegression(max_iter=1000, random_state=42, penalty='l2', n_jobs=-1),
                'regression': Ridge(random_state=42)
            },
            'lasso': {
                'classification': LogisticRegression(max_iter=1000, random_state=42, penalty='l1', solver='saga', n_jobs=-1),
                'regression': Lasso(random_state=42)
            },
            'svm': {
                'classification': SVC(kernel='rbf', probability=True, random_state=42),
                'regression': SVR(kernel='rbf')
            },
            'knn': {
                'classification': KNeighborsClassifier(n_neighbors=5),
                'regression': KNeighborsRegressor(n_neighbors=5)
            }
        }
        
        if LIGHTGBM_AVAILABLE:
            models['lightgbm'] = {
                'classification': lgb.LGBMClassifier(random_state=42, verbose=-1),
                'regression': lgb.LGBMRegressor(random_state=42, verbose=-1)
            }
        
        if CATBOOST_AVAILABLE:
            models['catboost'] = {
                'classification': cb.CatBoostClassifier(random_state=42, verbose=False),
                'regression': cb.CatBoostRegressor(random_state=42, verbose=False)
            }
        
        if model_name not in models:
            model_name = 'random_forest'
        
        return models[model_name][task_type]
    
    def _detect_task_type(self, y):
        """Автоопределение типа задачи"""
        if y.dtype == 'object':
            return 'classification'
        if y.nunique() <= 20:
            return 'classification'
        return 'regression'
    
    def fit(self, data, target_column, model_name='random_forest'):
        """Обучение модели"""
        print(f"🚀 AutoML: {model_name}")
        
        # Загрузка
        if isinstance(data, str):
            df = pd.read_csv(data) if data.endswith('.csv') else pd.read_excel(data)
        else:
            df = data.copy()
        
        self.task_type = self._detect_task_type(df[target_column])
        print(f"📊 Тип задачи: {self.task_type}")
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Кодирование цели
        if y.dtype == 'object':
            self.target_encoder = LabelEncoder()
            y = self.target_encoder.fit_transform(y)
        
        # Категориальные признаки
        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=False)
            self.dummy_columns = X.columns.tolist()
        else:
            self.dummy_columns = X.columns.tolist()
        
        # Пропуски
        num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            X[num_cols] = self.imputer_num.fit_transform(X[num_cols])
        
        self.feature_names = X.columns.tolist()
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        # Сохраняем для SHAP
        self.X_train_scaled = X_train
        
        # Обучение
        self.model = self._get_model(model_name, self.task_type)
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Оценка
        y_pred = self.model.predict(X_test)
        
        if self.task_type == 'classification':
            self.last_metric = accuracy_score(y_test, y_pred)
            print(f"✅ Accuracy: {self.last_metric:.4f}")
        else:
            self.last_metric = np.sqrt(mean_squared_error(y_test, y_pred))
            print(f"✅ RMSE: {self.last_metric:.4f}")
        
        # Feature Importance
        self._compute_feature_importance()
        
        return self
    
    def _compute_feature_importance(self):
        """Вычисление важности признаков"""
        if not self.is_trained:
            return
        
        importance = None
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            coef = self.model.coef_
            if len(coef.shape) > 1:
                importance = np.mean(np.abs(coef), axis=0)
            else:
                importance = np.abs(coef)
        
        if importance is not None and len(self.feature_names) == len(importance):
            self.feature_importance_df = pd.DataFrame({
                'Признак': self.feature_names,
                'Важность': importance
            }).sort_values('Важность', ascending=False)
            
            if self.feature_importance_df['Важность'].max() > 0:
                self.feature_importance_df['Важность_норм'] = self.feature_importance_df['Важность'] / self.feature_importance_df['Важность'].max()
    
    def get_feature_importance(self, top_n=15):
        """Возвращает важность признаков"""
        if self.feature_importance_df is None:
            self._compute_feature_importance()
        return self.feature_importance_df.head(top_n) if self.feature_importance_df is not None else None
    
    def plot_feature_importance(self, top_n=15):
        """Визуализация важности признаков"""
        fi = self.get_feature_importance(top_n)
        if fi is None:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0, 1, len(fi)))
        
        val_col = 'Важность_норм' if 'Важность_норм' in fi.columns else 'Важность'
        bars = ax.barh(range(len(fi)), fi[val_col], color=colors, edgecolor='black')
        ax.set_yticks(range(len(fi)))
        ax.set_yticklabels(fi['Признак'])
        ax.invert_yaxis()
        ax.set_xlabel('Важность')
        ax.set_title(f'Топ-{top_n} важных признаков')
        ax.grid(True, alpha=0.3)
        
        for i, (_, row) in enumerate(fi.iterrows()):
            ax.text(row[val_col] + 0.01, i, f'{row[val_col]:.3f}', va='center')
        
        plt.tight_layout()
        return fig
    
    def plot_confusion_matrix(self, X_test, y_test):
        """Матрица ошибок"""
        if self.task_type != 'classification':
            return None
        
        y_pred = self.predict(X_test)
        
        if self.target_encoder:
            y_true = self.target_encoder.inverse_transform(y_test)
            y_pred = self.target_encoder.inverse_transform(y_pred.astype(int))
            labels = self.target_encoder.classes_
        else:
            y_true = y_test
            labels = np.unique(np.concatenate([y_test, y_pred]))
        
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels, ax=ax)
        ax.set_xlabel('Предсказано')
        ax.set_ylabel('Истинное')
        ax.set_title('Матрица ошибок')
        
        return fig
    
    def predict(self, new_data):
        """Предсказание"""
        if not self.is_trained:
            raise Exception("Сначала обучите модель")
        
        if isinstance(new_data, pd.DataFrame):
            df = new_data.copy()
        elif isinstance(new_data, dict):
            df = pd.DataFrame([new_data])
        else:
            df = pd.DataFrame([new_data])
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
        
        if self.dummy_columns:
            for col in self.dummy_columns:
                if col not in df.columns:
                    df[col] = 0
            df = df[self.dummy_columns]
        
        df = df.fillna(0)
        df_scaled = self.scaler.transform(df)
        predictions = self.model.predict(df_scaled)
        
        if self.task_type == 'classification' and self.target_encoder:
            predictions = self.target_encoder.inverse_transform(predictions.astype(int))
        
        return predictions
    
    def explain_prediction(self, X_sample):
        """SHAP объяснение (упрощённое)"""
        if not self.is_trained:
            return None
        
        try:
            import shap
        except ImportError:
            return "Установите shap: pip install shap"
        
        # Подготовка
        if isinstance(X_sample, dict):
            X_sample = pd.DataFrame([X_sample])
        
        cat_cols = X_sample.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            X_sample = pd.get_dummies(X_sample, columns=cat_cols, drop_first=False)
        
        if self.dummy_columns:
            for col in self.dummy_columns:
                if col not in X_sample.columns:
                    X_sample[col] = 0
            X_sample = X_sample[self.dummy_columns]
        
        X_sample = X_sample.fillna(0)
        X_scaled = self.scaler.transform(X_sample)
        
        # SHAP
        if hasattr(self.model, 'feature_importances_'):
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_scaled)
            
            pred = self.predict(X_sample)[0]
            
            explanation = {
                'prediction': pred,
                'base_value': float(explainer.expected_value),
                'features': []
            }
            
            if len(shap_values.shape) == 3:
                pred_encoded = self.target_encoder.transform([pred])[0] if self.target_encoder else pred
                shap_vals = shap_values[:, :, pred_encoded] if pred_encoded < shap_values.shape[2] else shap_values[:, :, 0]
            else:
                shap_vals = shap_values
            
            if len(shap_vals.shape) == 1:
                indices = np.argsort(np.abs(shap_vals))[-5:][::-1]
                for idx in indices:
                    if idx < len(self.feature_names):
                        explanation['features'].append({
                            'feature': self.feature_names[idx],
                            'value': float(X_scaled[0, idx]) if idx < X_scaled.shape[1] else 0,
                            'shap_value': float(shap_vals[idx])
                        })
            
            return explanation
        else:
            return "SHAP объяснение доступно только для tree-based моделей"
    
    def save(self, path):
        """Сохранение модели"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"💾 Сохранено: {path}")
    
    @staticmethod
    def load(path):
        """Загрузка модели"""
        return joblib.load(path)
    
    def auto_select_best_model(self, data, target_column, models_to_try=None, use_gridsearch=False):
        """Автоматический выбор лучшей модели"""
        if models_to_try is None:
            models_to_try = ['random_forest', 'gradient_boosting', 'lightgbm', 'catboost', 
                           'linear', 'ridge', 'lasso', 'svm', 'knn']
        
        # Загрузка
        if isinstance(data, str):
            df = pd.read_csv(data) if data.endswith('.csv') else pd.read_excel(data)
        else:
            df = data.copy()
        
        self.task_type = self._detect_task_type(df[target_column])
        print(f"\n{'='*50}")
        print(f"🤖 Поиск лучшей модели ({self.task_type})")
        print(f"Тестируется: {len(models_to_try)} моделей")
        print(f"{'='*50}\n")
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        if y.dtype == 'object':
            self.target_encoder = LabelEncoder()
            y = self.target_encoder.fit_transform(y)
        
        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=False)
            self.dummy_columns = X.columns.tolist()
        
        X = X.fillna(X.mean())
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        results = {}
        
        for model_name in models_to_try:
            try:
                model = self._get_model(model_name, self.task_type)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                if self.task_type == 'classification':
                    score = accuracy_score(y_test, y_pred)
                else:
                    score = np.sqrt(mean_squared_error(y_test, y_pred))
                
                results[model_name] = score
                print(f"  {model_name}: {score:.4f}")
            except Exception as e:
                print(f"  {model_name}: ОШИБКА - {str(e)[:50]}")
                results[model_name] = -np.inf if self.task_type == 'classification' else np.inf
        
        # Выбор лучшей
        if self.task_type == 'classification':
            best_model = max(results.items(), key=lambda x: x[1])[0]
        else:
            best_model = min(results.items(), key=lambda x: x[1])[0]
        
        print(f"\n🏆 Лучшая модель: {best_model.upper()}")
        
        # Обучаем лучшую
        self.fit(df, target_column, best_model)
        self.best_model_name = best_model
        self.all_models_results = results
        
        return best_model, results
    
    def get_results_dataframe(self):
        """Результаты сравнения моделей в DataFrame"""
        if not self.all_models_results:
            return None
        
        results = []
        for name, score in self.all_models_results.items():
            results.append({
                'Модель': name.upper(),
                'Метрика': f"{score:.4f}" if isinstance(score, float) else str(score)
            })
        return pd.DataFrame(results)