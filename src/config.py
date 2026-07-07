from dataclasses import dataclass, field
from typing import List, Tuple
import random

ORDER_PENDING = "pending"
ORDER_PICKING = "picking"
ORDER_PACKING = "packing"
ORDER_QUALITY_CHECK = "quality_check"
ORDER_SHIPPING = "shipping"
ORDER_COMPLETED = "completed"

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
