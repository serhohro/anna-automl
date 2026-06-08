"""
Stream Simulator — эмулятор сенсорного потока для гиперактивного режима
"""

import random
import time
import numpy as np
from datetime import datetime


class SensorSimulator:
    """Эмулятор сенсора для тестирования гиперактивного режима"""
    
    def __init__(self, mode: str = 'trend'):
        self.mode = mode
        self.step = 0
        self.price = 50000
    
    def get_next(self) -> dict:
        """Следующий сенсорный сигнал"""
        self.step += 1
        
        if self.mode == 'random':
            x = random.gauss(0, 1)
            y = x * 2 + random.gauss(0, 0.5)
        elif self.mode == 'trend':
            x = 100 + self.step * 0.1 + random.gauss(0, 1)
            y = x * 1.5 + random.gauss(0, 2)
        elif self.mode == 'market':
            self.price += random.gauss(0, self.price * 0.002)
            self.price = max(1, self.price)
            x = self.price
            y = self.price + random.gauss(0, self.price * 0.01)
        else:
            x = random.random() * 100
            y = x * 0.5 + random.gauss(0, 5)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'features': {'sensor_1': x, 'step': self.step},
            'target': y
        }
    
    def run_realtime(self, callback, frequency_hz: int = 50):
        """Запуск реального потока"""
        interval = 1.0 / frequency_hz
        while True:
            data = self.get_next()
            callback(data)
            time.sleep(interval)