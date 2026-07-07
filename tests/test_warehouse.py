import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics

def test_simulation_runs():
    config = SimulationConfig(
        num_workers=5,
        num_packing_stations=3,
        orders_per_hour=10.0,
        working_hours=1.0,
        random_seed=42
    )
    sim = WarehouseSimulation(config)
    sim.run()
    assert len(sim.orders) > 0
    assert sim.env.now > 0

def test_orders_generated():
    config = SimulationConfig(
        orders_per_hour=60.0,
        working_hours=1.0,
        random_seed=42
    )
    sim = WarehouseSimulation(config)
    sim.run()
    expected_min = 50
    assert len(sim.orders) >= expected_min, f"Expected >= {expected_min}, got {len(sim.orders)}"

def test_kpis_computed():
    config = SimulationConfig(
        num_workers=10,
        num_packing_stations=5,
        orders_per_hour=10.0,
        working_hours=1.0,
        random_seed=42
    )
    sim = WarehouseSimulation(config)
    sim.run()
    total_time = config.working_hours * 60
    analytics = Analytics(config)
    kpis = analytics.compute_kpis(sim.orders, sim.completed_orders, total_time, 0.0)
    assert 'orders_completed' in kpis
    assert 'avg_completion_time' in kpis
    assert 'worker_utilization' in kpis
    assert kpis['orders_completed'] <= len(sim.orders)

def test_reproducibility():
    config1 = SimulationConfig(random_seed=123)
    config2 = SimulationConfig(random_seed=123)
    sim1 = WarehouseSimulation(config1)
    sim2 = WarehouseSimulation(config2)
    sim1.run()
    sim2.run()
    assert len(sim1.orders) == len(sim2.orders)

if __name__ == "__main__":
    test_simulation_runs()
    test_orders_generated()
    test_kpis_computed()
    test_reproducibility()
    print("All warehouse tests passed!")
