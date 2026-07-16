import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics
from src.forecasting import DemandForecaster
from src.scheduler import WorkerScheduler

def run_scenario(config: SimulationConfig, name: str):
    sim = WarehouseSimulation(config)
    sim.run()
    
    total_time = config.working_hours * 60 * config.simulation_days
    worker_util = sim.workers.get_utilization(total_time)
    cost_summary = sim.cost_tracker.get_summary()
    agv_util = sim.agv_manager.get_utilization(total_time) if config.num_agvs > 0 else None
    robot_util = sim.robot_pool.get_utilization(total_time) if config.num_robot_pickers > 0 else None
    
    analytics = Analytics(config)
    kpis = analytics.compute_kpis(sim.orders, sim.completed_orders, total_time, worker_util, cost_summary, agv_util, robot_util)
    analytics.print_report(kpis, name)
    
    df = analytics.create_dataframe(sim.completed_orders)
    analytics.plot_results(kpis, df, name)
    analytics.plot_costs(cost_summary, name)
    
    return kpis, df

def main():
    print("\n" + "="*60)
    print("  WAREHOUSE OPERATIONS SIMULATION")
    print("  Using SimPy Discrete-Event Simulation")
    print("="*60)
    
    all_results = []

    scenarios = [
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=3), "Scenario 1 - Current Config"),
        (SimulationConfig(num_workers=7, num_forklifts=2, num_packing_stations=3), "Scenario 2 - More Workers"),
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=5), "Scenario 3 - More Packing Stations"),
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=3, orders_per_hour=30.0), "Scenario 4 - 50% More Demand"),
        (SimulationConfig(num_workers=5, num_forklifts=4, num_packing_stations=3), "Scenario 5 - More Forklifts"),
        (SimulationConfig(num_workers=3, num_agvs=2, agv_mode="mixed"), "Scenario 6 - Human + AGV Mixed"),
        (SimulationConfig(num_workers=2, num_agvs=3, agv_mode="agv_only"), "Scenario 7 - AGV Only"),
        (SimulationConfig(num_workers=3, num_robot_pickers=2, robot_mode="default"), "Scenario 8 - Human + Robot Mixed"),
        (SimulationConfig(num_workers=1, num_robot_pickers=4, robot_mode="default", num_agvs=2, agv_mode="agv_only"), "Scenario 9 - Full Automation"),
    ]

    for config, name in scenarios:
        kpis, df = run_scenario(config, name)
        all_results.append((name, kpis))

    fc_rates = [15, 18, 22, 25, 28, 25, 20, 16]
    fc_config = SimulationConfig(
        enable_forecasting=True,
        working_hours=8.0, random_seed=99, num_workers=5
    )
    fc_sim = WarehouseSimulation(fc_config, forecast_rates=fc_rates)
    fc_sim.run()
    total_time = fc_config.working_hours * 60
    worker_util = fc_sim.workers.get_utilization(total_time)
    cost_summary = fc_sim.cost_tracker.get_summary()
    analytics = Analytics(fc_config)
    fc_kpis = analytics.compute_kpis(fc_sim.orders, fc_sim.completed_orders, total_time, worker_util, cost_summary)
    analytics.print_report(fc_kpis, "Scenario 10 - Forecast-Driven Demand")
    df_fc = analytics.create_dataframe(fc_sim.completed_orders)
    analytics.plot_results(fc_kpis, df_fc, "Scenario 10 - Forecast-Driven Demand")
    analytics.plot_costs(cost_summary, "Scenario 10 - Forecast-Driven Demand")
    all_results.append(("Scenario 10 - Forecast-Driven Demand", fc_kpis))

    ml_config = SimulationConfig(
        orders_per_hour=25.0, working_hours=4.0,
        num_workers=8, enable_ml_scheduling=True,
        ml_scheduling_training_runs=10, random_seed=77
    )
    scheduler = WorkerScheduler(ml_config)
    train_data = scheduler.generate_training_data(num_runs=10)
    scheduler.train(train_data)
    recommended = scheduler.predict_optimal_workers(ml_config)
    ml_config.num_workers = recommended
    ml_sim = WarehouseSimulation(ml_config)
    ml_sim.run()
    total_time = ml_config.working_hours * 60
    worker_util = ml_sim.workers.get_utilization(total_time)
    cost_summary = ml_sim.cost_tracker.get_summary()
    analytics = Analytics(ml_config)
    ml_kpis = analytics.compute_kpis(ml_sim.orders, ml_sim.completed_orders, total_time, worker_util, cost_summary)
    analytics.print_report(ml_kpis, f"Scenario 11 - ML Scheduler (Recommended: {recommended} workers)")
    df_ml = analytics.create_dataframe(ml_sim.completed_orders)
    analytics.plot_results(ml_kpis, df_ml, "Scenario 11 - ML Scheduler")
    analytics.plot_costs(cost_summary, "Scenario 11 - ML Scheduler")
    all_results.append((f"Scenario 11 - ML Scheduler ({recommended} workers)", ml_kpis))

    print("\n" + "="*118)
    print("  SCENARIO COMPARISON SUMMARY")
    print("="*118)
    print(f"{'Scenario':<30} {'Completed':<10} {'Avg Time':<10} {'Worker%':<8} {'AGV%':<7} {'Robot%':<8} {'Throughput':<10} {'Total Cost':<12} {'Cost/Order':<10}")
    print("-"*118)
    for name, kpis in all_results:
        cost = kpis.get('cost_total_cost', 0)
        cpo = kpis.get('cost_cost_per_order', 0)
        wu = kpis.get('worker_utilization', 0)
        au = kpis.get('agv_utilization', None)
        ru = kpis.get('robot_utilization', None)
        au_str = f"{au:<6.1f}%" if au is not None else "N/A    "
        ru_str = f"{ru:<6.1f}%" if ru is not None else "N/A    "
        print(f"{name:<30} {kpis.get('orders_completed', 0):<10} {kpis.get('avg_completion_time', 0):<10.2f} {wu:<7.1f}% {au_str} {ru_str} {kpis.get('throughput_per_day', 0):<10} ${cost:<8.2f} ${cpo:<6.2f}")
    print("="*118)

if __name__ == "__main__":
    main()
