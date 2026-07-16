import sys
import os
import simpy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics
from src.agv import AGVManager

def test_agv_manager_creation():
    config = SimulationConfig(
        num_agvs=3,
        agv_mode="mixed",
        num_charging_stations=2
    )
    env = simpy.Environment()
    mgr = AGVManager(env, config)
    assert mgr.num_agvs == 3
    assert mgr.available_agvs == 3

def test_agv_travel_time():
    config = SimulationConfig(num_agvs=2, agv_speed=100.0)
    env = simpy.Environment()
    mgr = AGVManager(env, config)
    tt = mgr.calculate_travel_time(500.0)
    assert abs(tt - 5.0) < 0.01

def test_agv_utilization_tracking():
    config = SimulationConfig(num_agvs=2, agv_mode="mixed", working_hours=0.5)
    sim = WarehouseSimulation(config)
    sim.run()
    total_time = config.working_hours * 60
    util = sim.agv_manager.get_utilization(total_time)
    assert 0.0 <= util <= 100.0

def test_agv_kpis_in_report():
    config = SimulationConfig(
        num_agvs=2, agv_mode="mixed",
        num_workers=3, working_hours=0.5,
        orders_per_hour=15.0
    )
    sim = WarehouseSimulation(config)
    sim.run()
    total_time = config.working_hours * 60
    worker_util = sim.workers.get_utilization(total_time)
    cost_summary = sim.cost_tracker.get_summary()
    agv_util = sim.agv_manager.get_utilization(total_time)
    analytics = Analytics(config)
    kpis = analytics.compute_kpis(
        sim.orders, sim.completed_orders, total_time,
        worker_util, cost_summary, agv_util
    )
    assert 'agv_utilization' in kpis
    assert 0.0 <= kpis['agv_utilization'] <= 100.0

def test_agv_cost_tracking():
    config = SimulationConfig(
        num_agvs=2, agv_mode="agv_only",
        num_workers=1, working_hours=0.5,
        orders_per_hour=10.0
    )
    sim = WarehouseSimulation(config)
    sim.run()
    summary = sim.cost_tracker.get_summary()
    assert summary['agv_cost'] >= 0
    assert summary['energy_cost'] >= 0
