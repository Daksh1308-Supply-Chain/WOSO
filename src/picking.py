import simpy
import random
import math
from typing import List
from src.config import Order, Product, SimulationConfig
from src.inventory import InventoryManager

class PickingProcess:
    def __init__(self, env: simpy.Environment, config: SimulationConfig, inventory: InventoryManager):
        self.env = env
        self.config = config
        self.inventory = inventory
        self.picking_station_location = config.packing_station_location
        self.rng = random.Random(config.random_seed)

    def calculate_travel_distance(self, product_ids: List[int]) -> float:
        if not product_ids:
            return 0.0
        locations = [self.inventory.get_product_location(pid) for pid in product_ids]
        current = self.picking_station_location
        total_distance = 0.0
        for loc in locations:
            total_distance += math.sqrt((current[0] - loc[0])**2 + (current[1] - loc[1])**2)
            current = loc
        return_to_packing = math.sqrt((current[0] - self.picking_station_location[0])**2 + (current[1] - self.picking_station_location[1])**2)
        total_distance += return_to_packing
        return total_distance

    def calculate_picking_time(self, order: Order) -> float:
        distance = self.calculate_travel_distance(order.items)
        travel_time = distance / self.config.walking_speed
        pick_time = len(order.items) * self.config.picking_speed
        return travel_time + pick_time
