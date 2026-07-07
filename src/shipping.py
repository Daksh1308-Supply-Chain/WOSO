import simpy
import random
from src.config import SimulationConfig

class ShippingProcess:
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.resource = simpy.Resource(env, capacity=config.num_receiving_docks)
        self.rng = random.Random(config.random_seed)
        self.queue_lengths = []
        self.shipped_orders = []

    def request(self):
        return self.resource.request()

    def get_shipping_time(self) -> float:
        return max(0.3, self.rng.gauss(self.config.shipping_time_mean, self.config.shipping_time_std))

    def record_queue(self):
        self.queue_lengths.append((self.env.now, len(self.resource.queue)))

    def ship_order(self, order):
        self.shipped_orders.append(order)
