import simpy
import random
from typing import List, Callable
from src.config import Order, SimulationConfig, Product

class OrderGenerator:
    def __init__(self, env: simpy.Environment, config: SimulationConfig, products: List[Product], order_callback: Callable):
        self.env = env
        self.config = config
        self.products = products
        self.order_callback = order_callback
        self.order_count = 0
        self.rng = random.Random(config.random_seed)

    def start(self):
        self.env.process(self._generate_orders())

    def _generate_orders(self):
        total_minutes = self.config.working_hours * 60 * self.config.simulation_days
        while self.env.now < total_minutes:
            self.order_count += 1
            num_items = max(1, int(self.rng.gauss(self.config.items_per_order_mean, self.config.items_per_order_std)))
            items = [self.rng.choice(self.products).product_id for _ in range(num_items)]
            order = Order(
                order_id=self.order_count,
                items=items,
                arrival_time=self.env.now
            )
            self.order_callback(order)
            inter_arrival = self.rng.expovariate(1.0 / self.config.inter_arrival_time)
            yield self.env.timeout(inter_arrival)
