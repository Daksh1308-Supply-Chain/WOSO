import os
import numpy as np
import pandas as pd
from typing import List, Optional
from src.config import SimulationConfig

class DemandForecaster:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.model = None
        self.historical_data: Optional[pd.Series] = None
        self._forecast: Optional[pd.Series] = None

    def generate_historical_data(self, num_runs: int = 10) -> pd.Series:
        all_hourly = []
        for seed_offset in range(num_runs):
            cfg = SimulationConfig(
                orders_per_hour=self.config.orders_per_hour,
                working_hours=24.0,
                simulation_days=self.config.simulation_days,
                random_seed=self.config.random_seed + seed_offset,
            )
            from src.warehouse import WarehouseSimulation
            sim = WarehouseSimulation(cfg)
            sim.run()
            arr = np.array([o.arrival_time for o in sim.orders])
            if len(arr) == 0:
                continue
            hours = np.floor(arr / 60).astype(int)
            total_hours = int(24 * cfg.simulation_days)
            counts = np.bincount(hours, minlength=total_hours + 1)[:total_hours]
            all_hourly.append(counts)
        if not all_hourly:
            return pd.Series(dtype=float)
        avg = np.mean(all_hourly, axis=0)
        self.historical_data = pd.Series(avg, name="orders_per_hour")
        return self.historical_data

    def train(self, order_counts: Optional[pd.Series] = None):
        try:
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            return
        data = order_counts if order_counts is not None else self.historical_data
        if data is None or len(data) < 10:
            return
        self.model = ARIMA(data, order=(5, 1, 0))
        self.model = self.model.fit()

    def forecast(self, steps: int = 8) -> pd.Series:
        if self.model is None:
            fallback = pd.Series([self.config.orders_per_hour] * steps)
            self._forecast = fallback
            return fallback
        fc = self.model.forecast(steps=steps)
        fc = np.maximum(fc, 1)
        self._forecast = pd.Series(fc, name="forecast")
        return self._forecast

    def get_rate_for_hour(self, hour_index: int) -> float:
        if self._forecast is not None and hour_index < len(self._forecast):
            return float(self._forecast.iloc[hour_index])
        return self.config.orders_per_hour

    def save_model(self, path: str):
        if self.model is None:
            return
        try:
            import joblib
            joblib.dump(self.model, path)
        except ImportError:
            pass

    def load_model(self, path: str):
        try:
            import joblib
            self.model = joblib.load(path)
        except (ImportError, FileNotFoundError):
            self.model = None

    def evaluate(self) -> dict:
        if self.model is None or self.historical_data is None:
            return {}
        n = len(self.historical_data)
        split = int(n * 0.8)
        train = self.historical_data[:split]
        test = self.historical_data[split:]
        if len(test) < 2:
            return {}
        try:
            from statsmodels.tsa.arima.model import ARIMA
            m = ARIMA(train, order=(5, 1, 0)).fit()
            pred = m.forecast(steps=len(test))
            rmse = float(np.sqrt(np.mean((test.values - pred.values) ** 2)))
            mae = float(np.mean(np.abs(test.values - pred.values)))
            return {"rmse": round(rmse, 2), "mae": round(mae, 2)}
        except ImportError:
            return {}
