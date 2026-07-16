import numpy as np
import pandas as pd
import matplotlib
try:
    from IPython import get_ipython
    if get_ipython() is None:
        matplotlib.use('Agg')
except ImportError:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from src.config import Order, SimulationConfig, ORDER_COMPLETED

class Analytics:
    def __init__(self, config: SimulationConfig):
        self.config = config
    
    def compute_kpis(self, orders: List[Order], completed_orders: List[Order], total_time: float, worker_utilization: float, cost_summary: dict = None, agv_utilization: float = None, robot_utilization: float = None) -> dict:
        kpis = {}
        kpis['total_orders'] = len(orders)
        kpis['orders_completed'] = len(completed_orders)
        kpis['orders_pending'] = len(orders) - len(completed_orders)
        kpis['completion_rate'] = (len(completed_orders) / len(orders) * 100) if orders else 0.0
        
        if completed_orders:
            completion_times = [
                (o.ship_end_time - o.arrival_time) for o in completed_orders
                if o.ship_end_time > 0
            ]
            kpis['avg_completion_time'] = float(np.mean(completion_times)) if completion_times else 0.0
            kpis['max_completion_time'] = float(np.max(completion_times)) if completion_times else 0.0
            kpis['min_completion_time'] = float(np.min(completion_times)) if completion_times else 0.0
            
            pick_times = [
                (o.pick_end_time - o.pick_start_time) for o in completed_orders
                if o.pick_end_time > 0
            ]
            kpis['avg_pick_time'] = float(np.mean(pick_times)) if pick_times else 0.0
            
            pack_times = [
                (o.pack_end_time - o.pack_start_time) for o in completed_orders
                if o.pack_end_time > 0
            ]
            kpis['avg_pack_time'] = float(np.mean(pack_times)) if pack_times else 0.0
            
            wait_times = [
                (o.pick_start_time - o.arrival_time) for o in completed_orders
                if o.pick_start_time > 0
            ]
            kpis['avg_waiting_time'] = float(np.mean(wait_times)) if wait_times else 0.0
        else:
            kpis['avg_completion_time'] = 0.0
            kpis['max_completion_time'] = 0.0
            kpis['min_completion_time'] = 0.0
            kpis['avg_pick_time'] = 0.0
            kpis['avg_pack_time'] = 0.0
            kpis['avg_waiting_time'] = 0.0
        
        kpis['worker_utilization'] = worker_utilization
        if agv_utilization is not None:
            kpis['agv_utilization'] = agv_utilization
        if robot_utilization is not None:
            kpis['robot_utilization'] = robot_utilization
        
        throughput_hour = len(completed_orders) / (total_time / 60) if total_time > 0 else 0
        kpis['throughput_per_hour'] = round(throughput_hour, 2)
        kpis['throughput_per_day'] = len(completed_orders)

        if cost_summary:
            for key, value in cost_summary.items():
                kpis[f'cost_{key}'] = value
        
        return kpis
    
    def create_dataframe(self, completed_orders: List[Order]) -> pd.DataFrame:
        data = []
        for o in completed_orders:
            data.append({
                'order_id': o.order_id,
                'arrival_time': o.arrival_time,
                'pick_start': o.pick_start_time,
                'pick_end': o.pick_end_time,
                'pack_start': o.pack_start_time,
                'pack_end': o.pack_end_time,
                'ship_start': o.ship_start_time,
                'ship_end': o.ship_end_time,
                'completion_time': o.ship_end_time - o.arrival_time if o.ship_end_time > 0 else 0,
                'pick_duration': o.pick_end_time - o.pick_start_time if o.pick_end_time > 0 else 0,
                'pack_duration': o.pack_end_time - o.pack_start_time if o.pack_end_time > 0 else 0,
                'num_items': len(o.items),
            })
        return pd.DataFrame(data)
    
    def plot_results(self, kpis: dict, df: pd.DataFrame, scenario_name: str = "scenario", show: bool = False):
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        if not df.empty and 'completion_time' in df.columns:
            axes[0, 0].hist(df['completion_time'], bins=20, color='steelblue', edgecolor='black')
            axes[0, 0].set_title('Order Completion Times')
            axes[0, 0].set_xlabel('Minutes')
            axes[0, 0].set_ylabel('Frequency')
        
        if not df.empty and 'pick_duration' in df.columns:
            axes[0, 1].hist(df['pick_duration'], bins=15, color='coral', edgecolor='black')
            axes[0, 1].set_title('Picking Duration')
            axes[0, 1].set_xlabel('Minutes')
        
        if not df.empty and 'pack_duration' in df.columns:
            axes[0, 2].hist(df['pack_duration'], bins=15, color='green', edgecolor='black', alpha=0.7)
            axes[0, 2].set_title('Packing Duration')
            axes[0, 2].set_xlabel('Minutes')
        
        metrics = ['avg_completion_time', 'avg_pick_time', 'avg_pack_time', 'avg_waiting_time']
        values = [kpis.get(m, 0) for m in metrics]
        labels = ['Completion', 'Picking', 'Packing', 'Waiting']
        colors = ['steelblue', 'coral', 'green', 'orange']
        axes[1, 0].bar(labels, values, color=colors)
        axes[1, 0].set_title('Average Times (minutes)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        throughput_kpis = ['orders_completed', 'orders_pending', 'throughput_per_day']
        t_values = [kpis.get(k, 0) for k in throughput_kpis]
        axes[1, 1].bar(['Completed', 'Pending', 'Throughput'], t_values, color=['green', 'red', 'blue'])
        axes[1, 1].set_title('Order Statistics')
        
        wu = kpis.get('worker_utilization', 0)
        au = kpis.get('agv_utilization', None)
        ru = kpis.get('robot_utilization', None)
        labels = ['Worker']
        values = [wu]
        colors = ['purple']
        if au is not None:
            labels.append('AGV')
            values.append(au)
            colors.append('orange')
        if ru is not None:
            labels.append('Robot')
            values.append(ru)
            colors.append('green')
        axes[1, 2].bar(labels, values, color=colors)
        axes[1, 2].set_ylabel('Utilization %')
        axes[1, 2].set_ylim(0, 100)
        axes[1, 2].axhline(y=85, color='r', linestyle='--', label='Target Max')
        axes[1, 2].axhline(y=70, color='g', linestyle='--', label='Target Min')
        axes[1, 2].legend()
        axes[1, 2].set_title('Resource Utilization')
        
        plt.suptitle(f'Warehouse Simulation Results - {scenario_name}', fontsize=14)
        plt.tight_layout()
        if show:
            plt.show()
        plt.savefig(f'output/{scenario_name}_report.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_heatmap(self, pick_frequencies: Dict[Tuple[float, float], int], scenario_name: str = "scenario", show: bool = False):
        if not pick_frequencies:
            return
        fig, ax = plt.subplots(figsize=(10, 7))
        locations = list(pick_frequencies.keys())
        freqs = list(pick_frequencies.values())
        xs, ys = zip(*locations)
        sc = ax.scatter(xs, ys, c=freqs, cmap='hot', s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        cbar = plt.colorbar(sc, ax=ax, label='Pick Frequency')
        ax.set_xlim(0, self.config.warehouse_length)
        ax.set_ylim(0, self.config.warehouse_width)
        ax.set_xlabel('Warehouse Length (ft)')
        ax.set_ylabel('Warehouse Width (ft)')
        ax.set_title(f'Warehouse Pick Frequency Heat Map - {scenario_name}')
        ax.invert_yaxis()
        plt.tight_layout()
        if show:
            plt.show()
        plt.savefig(f'output/{scenario_name}_heatmap.png', dpi=150, bbox_inches='tight')
        plt.close()

    def plot_costs(self, cost_summary: dict, scenario_name: str = "scenario", show: bool = False):
        if not cost_summary:
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        cost_categories = ['labor_cost', 'agv_cost', 'robot_cost', 'forklift_cost', 'energy_cost', 'overhead_cost', 'rent_cost']
        labels = ['Labor', 'AGV', 'Robot', 'Forklift', 'Energy', 'Overhead', 'Rent']
        values = [cost_summary.get(c, 0) for c in cost_categories]
        colors = ['steelblue', 'orange', 'green', 'purple', 'red', 'brown', 'gray']
        axes[0].bar(labels, values, color=colors)
        axes[0].set_title('Cost Breakdown ($)')
        axes[0].tick_params(axis='x', rotation=45)
        cost_per = cost_summary.get('cost_per_order', 0)
        axes[1].bar(['Cost/Order'], [cost_per], color='gold', width=0.3)
        axes[1].set_title(f'Cost per Order: ${cost_per:.2f}')
        axes[1].set_ylabel('$')
        plt.suptitle(f'Cost Analysis - {scenario_name}', fontsize=14)
        plt.tight_layout()
        if show:
            plt.show()
        plt.savefig(f'output/{scenario_name}_costs.png', dpi=150, bbox_inches='tight')
        plt.close()

    def print_report(self, kpis: dict, scenario_name: str = "Scenario"):
        print(f"\n{'='*60}")
        print(f"  {scenario_name}")
        print(f"{'='*60}")
        print(f"  Orders Completed:     {kpis.get('orders_completed', 0)}")
        print(f"  Orders Pending:       {kpis.get('orders_pending', 0)}")
        print(f"  Completion Rate:      {kpis.get('completion_rate', 0):.1f}%")
        print(f"  Avg Completion Time:  {kpis.get('avg_completion_time', 0):.2f} min")
        print(f"  Avg Pick Time:        {kpis.get('avg_pick_time', 0):.2f} min")
        print(f"  Avg Pack Time:        {kpis.get('avg_pack_time', 0):.2f} min")
        print(f"  Avg Waiting Time:     {kpis.get('avg_waiting_time', 0):.2f} min")
        print(f"  Worker Utilization:   {kpis.get('worker_utilization', 0):.1f}%")
        agv_util = kpis.get('agv_utilization', None)
        if agv_util is not None:
            print(f"  AGV Utilization:      {agv_util:.1f}%")
        robot_util = kpis.get('robot_utilization', None)
        if robot_util is not None:
            print(f"  Robot Utilization:    {robot_util:.1f}%")
        print(f"  Throughput/Hour:      {kpis.get('throughput_per_hour', 0):.2f}")
        print(f"  Throughput/Day:       {kpis.get('throughput_per_day', 0)}")
        total_cost = kpis.get('cost_total_cost', None)
        if total_cost is not None:
            print(f"  Total Cost:           ${total_cost:.2f}")
            print(f"  Cost per Order:       ${kpis.get('cost_cost_per_order', 0):.2f}")
        print(f"{'='*60}\n")
