import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig
from src.forecasting import DemandForecaster

def test_forecaster_creation():
    config = SimulationConfig(orders_per_hour=20.0, working_hours=8.0)
    fc = DemandForecaster(config)
    assert fc.model is None

def test_generate_historical_data():
    config = SimulationConfig(orders_per_hour=20.0, working_hours=2.0, simulation_days=1)
    fc = DemandForecaster(config)
    data = fc.generate_historical_data(num_runs=2)
    assert data is not None
    assert len(data) > 0

def test_forecast_fallback():
    config = SimulationConfig(orders_per_hour=20.0)
    fc = DemandForecaster(config)
    fc2 = fc.forecast(steps=8)
    assert len(fc2) == 8
    assert fc2.iloc[0] == 20.0

def test_get_rate_for_hour():
    config = SimulationConfig(orders_per_hour=20.0)
    fc = DemandForecaster(config)
    fc._forecast = None
    rate = fc.get_rate_for_hour(3)
    assert rate == 20.0
