from dataclasses import dataclass, field
from typing import Dict

@dataclass
class CostConfig:
    labor_cost_per_hour: float = 25.0
    agv_cost_per_hour: float = 15.0
    robot_cost_per_hour: float = 20.0
    forklift_cost_per_hour: float = 10.0
    electricity_cost_per_kwh: float = 0.12
    agv_power_consumption_kw: float = 1.5
    robot_power_consumption_kw: float = 0.8
    warehouse_rent_per_day: float = 1000.0
    overhead_per_order: float = 2.5

class CostTracker:
    def __init__(self, config: CostConfig):
        self.config = config
        self.labor_cost = 0.0
        self.agv_cost = 0.0
        self.robot_cost = 0.0
        self.forklift_cost = 0.0
        self.energy_cost = 0.0
        self.overhead_cost = 0.0
        self.rent_cost = 0.0
        self.total_orders_completed = 0

    def record_labor_time(self, minutes: float):
        self.labor_cost += (minutes / 60.0) * self.config.labor_cost_per_hour

    def record_agv_time(self, minutes: float):
        self.agv_cost += (minutes / 60.0) * self.config.agv_cost_per_hour
        energy_kwh = (minutes / 60.0) * self.config.agv_power_consumption_kw
        self.energy_cost += energy_kwh * self.config.electricity_cost_per_kwh

    def record_robot_time(self, minutes: float):
        self.robot_cost += (minutes / 60.0) * self.config.robot_cost_per_hour
        energy_kwh = (minutes / 60.0) * self.config.robot_power_consumption_kw
        self.energy_cost += energy_kwh * self.config.electricity_cost_per_kwh

    def record_forklift_time(self, minutes: float):
        self.forklift_cost += (minutes / 60.0) * self.config.forklift_cost_per_hour

    def record_completed_order(self):
        self.total_orders_completed += 1
        self.overhead_cost += self.config.overhead_per_order

    def record_rent(self, days: float):
        self.rent_cost = self.config.warehouse_rent_per_day * days

    def get_total_cost(self) -> float:
        return (self.labor_cost + self.agv_cost + self.robot_cost
                + self.forklift_cost + self.energy_cost
                + self.overhead_cost + self.rent_cost)

    def get_cost_per_order(self) -> float:
        if self.total_orders_completed == 0:
            return 0.0
        return self.get_total_cost() / self.total_orders_completed

    def get_cost_per_order_breakdown(self) -> Dict[str, float]:
        if self.total_orders_completed == 0:
            return {}
        return {
            'labor_cost_per_order': self.labor_cost / self.total_orders_completed,
            'agv_cost_per_order': self.agv_cost / self.total_orders_completed,
            'robot_cost_per_order': self.robot_cost / self.total_orders_completed,
            'energy_cost_per_order': self.energy_cost / self.total_orders_completed,
            'overhead_per_order': self.overhead_cost / self.total_orders_completed,
        }

    def get_summary(self) -> dict:
        return {
            'labor_cost': round(self.labor_cost, 2),
            'agv_cost': round(self.agv_cost, 2),
            'robot_cost': round(self.robot_cost, 2),
            'forklift_cost': round(self.forklift_cost, 2),
            'energy_cost': round(self.energy_cost, 2),
            'overhead_cost': round(self.overhead_cost, 2),
            'rent_cost': round(self.rent_cost, 2),
            'total_cost': round(self.get_total_cost(), 2),
            'cost_per_order': round(self.get_cost_per_order(), 2),
            'total_orders_completed': self.total_orders_completed,
        }
