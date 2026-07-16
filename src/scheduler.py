import os
import numpy as np
import pandas as pd
from typing import Optional, Tuple
from src.config import SimulationConfig

class WorkerScheduler:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.model = None
        self._feature_cols = [
            "orders_per_hour", "num_packing_stations", "num_forklifts",
            "has_agv", "has_robots", "items_per_order"
        ]

    def generate_training_data(self, num_runs: int = 50) -> pd.DataFrame:
        from src.warehouse import WarehouseSimulation
        from src.analytics import Analytics
        rows = []
        base_config = self.config
        rng = np.random.default_rng(seed=base_config.random_seed)
        for _ in range(num_runs):
            workers = int(rng.integers(2, 15))
            demand = float(rng.uniform(5, 40))
            packing = int(rng.integers(1, 6))
            forklifts = int(rng.integers(1, 5))
            has_agv = bool(rng.integers(0, 2))
            has_robots = bool(rng.integers(0, 2))
            items_mean = float(rng.uniform(2, 5))
            cfg = SimulationConfig(
                num_workers=workers,
                orders_per_hour=demand,
                num_packing_stations=packing,
                num_forklifts=forklifts,
                num_agvs=3 if has_agv else 0,
                num_robot_pickers=2 if has_robots else 0,
                items_per_order_mean=items_mean,
                working_hours=4.0,
                random_seed=int(rng.integers(0, 10000)),
            )
            sim = WarehouseSimulation(cfg)
            sim.run()
            total_time = cfg.working_hours * 60
            worker_util = sim.workers.get_utilization(total_time)
            kpis = Analytics(cfg).compute_kpis(
                sim.orders, sim.completed_orders, total_time, worker_util
            )
            avg_time = kpis.get("avg_completion_time", 999)
            completed = kpis.get("orders_completed", 0)
            opt = self._evaluate_optimal(workers, avg_time, completed, worker_util)
            rows.append({
                "orders_per_hour": demand,
                "num_packing_stations": packing,
                "num_forklifts": forklifts,
                "has_agv": int(has_agv),
                "has_robots": int(has_robots),
                "items_per_order": items_mean,
                "actual_workers": workers,
                "avg_completion_time": avg_time,
                "completed": completed,
                "worker_utilization": worker_util,
                "optimal_workers": opt,
            })
        return pd.DataFrame(rows)

    def _evaluate_optimal(self, workers: int, avg_time: float, completed: int, util: float) -> int:
        if avg_time < 15 and util < 60 and completed > 0:
            return max(1, workers - 1)
        if avg_time > 25 and completed > 0:
            return workers + 1
        return workers

    def train(self, data: pd.DataFrame):
        try:
            from sklearn.ensemble import RandomForestRegressor
        except ImportError:
            return
        if len(data) < 10:
            return
        X = data[self._feature_cols]
        y = data["optimal_workers"]
        self.model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        self.model.fit(X, y)

    def predict_optimal_workers(self, config: SimulationConfig) -> int:
        if self.model is None:
            return config.num_workers
        features = pd.DataFrame([{
            "orders_per_hour": config.orders_per_hour,
            "num_packing_stations": config.num_packing_stations,
            "num_forklifts": config.num_forklifts,
            "has_agv": int(config.num_agvs > 0),
            "has_robots": int(config.num_robot_pickers > 0),
            "items_per_order": config.items_per_order_mean,
        }])
        pred = self.model.predict(features)[0]
        return max(1, int(round(pred)))

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
