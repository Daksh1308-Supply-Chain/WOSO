import simpy
import random
from src.config import SimulationConfig

class PackingProcess:
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.resource = simpy.Resource(env, capacity=config.num_packing_stations)
        self.rng = random.Random(config.random_seed)
        self.queue_lengths = []

    def request(self):
        return self.resource.request()

    def get_packing_time(self) -> float:
        return max(0.5, self.rng.gauss(self.config.packing_time_mean, self.config.packing_time_std))

    def record_queue(self):
        self.queue_lengths.append((self.env.now, len(self.resource.queue)))
