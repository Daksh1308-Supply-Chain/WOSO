from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import random
from src.costing import CostConfig

ORDER_PENDING = "pending"
ORDER_PICKING = "picking"
ORDER_PACKING = "packing"
ORDER_QUALITY_CHECK = "quality_check"
ORDER_SHIPPING = "shipping"
ORDER_COMPLETED = "completed"

@dataclass
class Shift:
    name: str = "Default Shift"
    start_hour: float = 0.0
    end_hour: float = 8.0
    break_start: Optional[float] = None
    break_duration: float = 0.5

@dataclass
class WorkerProfile:
    worker_type: str = "experienced"
    walking_speed: float = 50.0

@dataclass
class Order:
    order_id: int
    items: List[int]
    arrival_time: float
    pick_start_time: float = 0.0
    pick_end_time: float = 0.0
    pack_start_time: float = 0.0
    pack_end_time: float = 0.0
    ship_start_time: float = 0.0
    ship_end_time: float = 0.0
    state: str = ORDER_PENDING

@dataclass
class Product:
    product_id: int
    name: str
    quantity: int
    location: Tuple[float, float]
    reorder_level: int

@dataclass
class SimulationConfig:
    num_workers: int = 5
    num_forklifts: int = 2
    warehouse_capacity: int = 10000
    num_packing_stations: int = 3
    num_receiving_docks: int = 2

    orders_per_hour: float = 20.0
    picking_speed: float = 0.5
    walking_speed: float = 50.0
    packing_time_mean: float = 3.0
    packing_time_std: float = 0.5
    shipping_time_mean: float = 2.0
    shipping_time_std: float = 0.3
    quality_check_time: float = 1.0

    items_per_order_mean: float = 3.0
    items_per_order_std: float = 1.0

    working_hours: float = 8.0
    shift_duration: float = 8.0
    random_seed: int = 42
    simulation_days: int = 1

    warehouse_length: float = 300.0
    warehouse_width: float = 200.0
    receiving_dock: Tuple[float, float] = (0.0, 0.0)
    shipping_dock: Tuple[float, float] = (300.0, 0.0)
    packing_station_location: Tuple[float, float] = (150.0, 0.0)

    num_agvs: int = 0
    agv_speed: float = 100.0
    agv_pick_speed: float = 0.3
    agv_battery_capacity: float = 100.0
    agv_charge_rate: float = 10.0
    num_charging_stations: int = 2
    agv_charge_interval: float = 45.0
    agv_charge_duration: float = 5.0
    agv_mode: str = "disabled"
    agv_distance_threshold: float = 200.0

    num_robot_pickers: int = 0
    robot_pick_speed: float = 0.2
    robot_maintenance_interval: float = 120.0
    robot_maintenance_duration: float = 10.0
    robot_mode: str = "disabled"
    robot_high_volume_count: int = 10

    enable_forecasting: bool = False
    forecast_training_runs: int = 5

    enable_ml_scheduling: bool = False
    ml_scheduling_training_runs: int = 30

    cost_config: CostConfig = field(default_factory=CostConfig)

    shifts: List[Shift] = field(default_factory=lambda: [
        Shift(name="Default Shift", start_hour=0.0, end_hour=8.0, break_start=None, break_duration=0.5)
    ])
    worker_profiles: List[WorkerProfile] = field(default_factory=lambda: [
        WorkerProfile(worker_type="experienced", walking_speed=50.0)
    ])

    @property
    def orders_per_day(self) -> int:
        return int(self.orders_per_hour * self.working_hours)

    @property
    def inter_arrival_time(self) -> float:
        return 60.0 / self.orders_per_hour

def create_default_products(num_products: int = 50, seed: int = 42) -> List[Product]:
    rng = random.Random(seed)
    products = []
    for i in range(1, num_products + 1):
        products.append(Product(
            product_id=i,
            name=f"Product-{i:03d}",
            quantity=50,
            reorder_level=10,
            location=(round(rng.uniform(10, 290), 1), round(rng.uniform(10, 190), 1))
        ))
    return products
