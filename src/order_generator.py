import simpy
import random
from typing import List, Callable, Optional
from src.config import Order, SimulationConfig, Product

class OrderGenerator:
    def __init__(self, env: simpy.Environment, config: SimulationConfig, products: List[Product], order_callback: Callable, forecast_rates: Optional[List[float]] = None):
        self.env = env
        self.config = config
        self.products = products
        self.order_callback = order_callback
        self.forecast_rates = forecast_rates
        self.order_count = 0
        self.rng = random.Random(config.random_seed)

    def start(self):
        self.env.process(self._generate_orders())

    def _get_current_rate(self) -> float:
        if self.forecast_rates is None:
            return self.config.orders_per_hour
        hour = int(self.env.now / 60)
        if hour < len(self.forecast_rates):
            return self.forecast_rates[hour]
        return self.config.orders_per_hour

    def _generate_orders(self):
        last_hour = max(s.end_hour for s in self.config.shifts) if self.config.shifts else self.config.working_hours
        total_minutes = last_hour * 60 * self.config.simulation_days
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
            current_rate = self._get_current_rate()
            current_iat = 60.0 / current_rate if current_rate > 0 else 60.0
            inter_arrival = self.rng.expovariate(1.0 / current_iat)
            yield self.env.timeout(inter_arrival)
