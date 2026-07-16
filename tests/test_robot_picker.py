import sys
import os
import simpy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics
from src.robot_picker import RobotPool

def test_robot_pool_creation():
    config = SimulationConfig(num_robot_pickers=3, robot_mode="default")
    env = simpy.Environment()
    pool = RobotPool(env, config)
    assert pool.num_robots == 3
    assert pool.available_robots == 3

def test_high_volume_classification():
    config = SimulationConfig(num_robot_pickers=2, robot_high_volume_count=5)
    env = simpy.Environment()
    pool = RobotPool(env, config)
    assert pool.is_high_volume_product(1) == True
    assert pool.is_high_volume_product(5) == True
    assert pool.is_high_volume_product(6) == False

def test_robot_eligibility():
    config = SimulationConfig(num_robot_pickers=2, robot_mode="default", robot_high_volume_count=5)
    env = simpy.Environment()
    pool = RobotPool(env, config)
    assert pool.order_is_robot_eligible([1, 2, 3]) == True
    assert pool.order_is_robot_eligible([6, 7, 8]) == False
    assert pool.order_is_robot_eligible([1, 7, 8]) == False

def test_robot_disabled():
    config = SimulationConfig(num_robot_pickers=0)
    env = simpy.Environment()
    pool = RobotPool(env, config)
    assert pool.order_is_robot_eligible([1, 2, 3]) == False

def test_robot_utilization_tracking():
    config = SimulationConfig(num_robot_pickers=2, robot_mode="default", working_hours=0.5, orders_per_hour=15.0)
    sim = WarehouseSimulation(config)
    sim.run()
    total_time = config.working_hours * 60
    util = sim.robot_pool.get_utilization(total_time)
    assert 0.0 <= util <= 100.0

def test_robot_kpis_in_report():
    config = SimulationConfig(num_robot_pickers=2, robot_mode="default", working_hours=0.5, orders_per_hour=15.0)
    sim = WarehouseSimulation(config)
    sim.run()
    total_time = config.working_hours * 60
    kpis = Analytics(config).compute_kpis(
        sim.orders, sim.completed_orders, total_time, 0.0, None, None,
        sim.robot_pool.get_utilization(total_time)
    )
    assert 'robot_utilization' in kpis

def test_robot_cost_tracking():
    config = SimulationConfig(num_robot_pickers=2, robot_mode="default", working_hours=0.5, orders_per_hour=10.0)
    sim = WarehouseSimulation(config)
    sim.run()
    summary = sim.cost_tracker.get_summary()
    assert summary['robot_cost'] >= 0
