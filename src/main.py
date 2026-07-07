import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics

def run_scenario(config: SimulationConfig, name: str):
    sim = WarehouseSimulation(config)
    sim.run()
    
    total_time = config.working_hours * 60 * config.simulation_days
    worker_util = sim.workers.get_utilization(total_time)
    
    analytics = Analytics(config)
    kpis = analytics.compute_kpis(sim.orders, sim.completed_orders, total_time, worker_util)
    analytics.print_report(kpis, name)
    
    df = analytics.create_dataframe(sim.completed_orders)
    analytics.plot_results(kpis, df, name)
    
    return kpis, df

def main():
    print("\n" + "="*60)
    print("  WAREHOUSE OPERATIONS SIMULATION")
    print("  Using SimPy Discrete-Event Simulation")
    print("="*60)
    
    scenarios = [
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=3), "Scenario 1 - Current Config"),
        (SimulationConfig(num_workers=7, num_forklifts=2, num_packing_stations=3), "Scenario 2 - More Workers"),
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=5), "Scenario 3 - More Packing Stations"),
        (SimulationConfig(num_workers=5, num_forklifts=2, num_packing_stations=3, orders_per_hour=30.0), "Scenario 4 - 50% More Demand"),
        (SimulationConfig(num_workers=5, num_forklifts=4, num_packing_stations=3), "Scenario 5 - More Forklifts"),
    ]
    
    all_results = []
    for config, name in scenarios:
        kpis, df = run_scenario(config, name)
        all_results.append((name, kpis))
    
    print("\n" + "="*60)
    print("  SCENARIO COMPARISON SUMMARY")
    print("="*60)
    print(f"{'Scenario':<30} {'Completed':<10} {'Avg Time':<10} {'Utilization':<12} {'Throughput':<10}")
    print("-"*72)
    for name, kpis in all_results:
        print(f"{name:<30} {kpis.get('orders_completed', 0):<10} {kpis.get('avg_completion_time', 0):<10.2f} {kpis.get('worker_utilization', 0):<10.1f}% {kpis.get('throughput_per_day', 0):<10}")
    print("="*60)

if __name__ == "__main__":
    main()
