"""
Hyperactive Engine — гиперактивный режим реального времени
"""

import time
import numpy as np
from collections import deque
from .automl_engine import SuperAutoML


class HyperactiveAutoML(SuperAutoML):
    """Гиперактивная версия — обработка с латентностью < 100 мс"""
    
    def __init__(self, latency_ms: int = 100, retrain_every_n: int = 50):
        super().__init__()
        self.latency_ms = latency_ms
        self.retrain_every_n = retrain_every_n
        self.buffer_X = deque(maxlen=retrain_every_n)
        self.buffer_y = deque(maxlen=retrain_every_n)
        self.example_counter = 0
        self.total_latencies = []
        self.is_running = False
        self.action_callback = None
        self.sensor_callback = None
    
    def set_action_callback(self, callback):
        """Функция действия на основе предсказания"""
        self.action_callback = callback
    
    def set_sensor_callback(self, callback):
        """Функция получения данных с сенсора"""
        self.sensor_callback = callback
    
    def process_one(self, X_new, y_true=None):
        """Один цикл гиперактивной обработки"""
        start_ms = time.time() * 1000
        
        # Предсказание
        prediction = self.predict(X_new)
        pred_value = float(prediction[0]) if isinstance(prediction, np.ndarray) else float(prediction)
        
        # Действие
        action_result = None
        if self.action_callback:
            action_result = self.action_callback(pred_value)
        
        # Дообучение
        if y_true is not None:
            self.buffer_X.append(X_new)
            self.buffer_y.append(y_true)
            self.example_counter += 1
            
            if self.example_counter % self.retrain_every_n == 0:
                self._online_retrain()
        
        # Контроль латентности
        elapsed_ms = (time.time() * 1000) - start_ms
        self.total_latencies.append(elapsed_ms)
        
        if elapsed_ms > self.latency_ms:
            print(f"⚠️ Превышение: {elapsed_ms:.2f} > {self.latency_ms} мс")
        
        return pred_value, action_result, elapsed_ms
    
    def _online_retrain(self):
        """Онлайн-дообучение"""
        if len(self.buffer_X) < 2:
            return
        
        print(f"🔄 Дообучение на {len(self.buffer_X)} примерах...")
        
        X_list = list(self.buffer_X)
        y_list = list(self.buffer_y)
        
        for i in range(len(X_list)):
            self.partial_fit(X_list[i], y_list[i])
        
        self.buffer_X.clear()
        self.buffer_y.clear()
    
    def run_stream(self, num_iterations: int = None, duration_seconds: float = None):
        """Запуск гиперактивного потока"""
        if not self.sensor_callback:
            raise Exception("Установите sensor_callback")
        
        self.is_running = True
        start_time = time.time()
        iteration = 0
        
        print(f"⚡ Гиперактивный режим запущен (латентность < {self.latency_ms} мс)")
        
        while self.is_running:
            if num_iterations and iteration >= num_iterations:
                break
            if duration_seconds and (time.time() - start_time) > duration_seconds:
                break
            
            sensor_data = self.sensor_callback()
            if sensor_data is None:
                time.sleep(0.001)
                continue
            
            X_new = sensor_data.get('features', {})
            y_true = sensor_data.get('target', None)
            
            pred, action, latency = self.process_one(X_new, y_true)
            iteration += 1
            
            if iteration % 100 == 0:
                avg_lat = np.mean(self.total_latencies[-100:])
                print(f"📊 Итерация {iteration} | Латентность: {avg_lat:.2f} мс")
            
            time.sleep(max(0, (self.latency_ms / 1000) - (latency / 1000)))
        
        self.stop()
    
    def stop(self):
        """Остановка"""
        self.is_running = False
        if self.total_latencies:
            print(f"\n📊 Средняя латентность: {np.mean(self.total_latencies):.2f} мс")
            print(f"   Всего циклов: {len(self.total_latencies)}")