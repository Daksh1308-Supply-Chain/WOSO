import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig
from src.scheduler import WorkerScheduler

def test_scheduler_creation():
    config = SimulationConfig()
    sched = WorkerScheduler(config)
    assert sched.model is None

def test_generate_training_data():
    config = SimulationConfig(working_hours=1.0, random_seed=42)
    sched = WorkerScheduler(config)
    data = sched.generate_training_data(num_runs=5)
    assert data is not None
    assert len(data) == 5
    assert 'optimal_workers' in data.columns

def test_train_and_predict():
    config = SimulationConfig(working_hours=1.0, random_seed=42)
    sched = WorkerScheduler(config)
    data = sched.generate_training_data(num_runs=10)
    sched.train(data)
    pred = sched.predict_optimal_workers(config)
    assert pred >= 1

def test_predict_default():
    config = SimulationConfig()
    sched = WorkerScheduler(config)
    pred = sched.predict_optimal_workers(config)
    assert pred == config.num_workers
