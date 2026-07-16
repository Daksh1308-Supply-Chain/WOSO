import simpy
import random
from typing import List, Tuple, Optional
from src.config import SimulationConfig

class AGVManager:
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.num_agvs = config.num_agvs
        self.agv_speed = config.agv_speed
        self.charge_interval = config.agv_charge_interval
        self.charge_duration = config.agv_charge_duration
        self.rng = random.Random(config.random_seed)

        self._util_samples: List[Tuple[float, int]] = []
        self._charges_completed = 0
        self._total_charge_time = 0.0

        if self.num_agvs > 0:
            self.resource = simpy.Resource(env, capacity=self.num_agvs)
            self.charging_stations = simpy.Resource(env, capacity=config.num_charging_stations)
            self._monitor_process = env.process(self._monitor_utilization())
            if config.agv_mode != "disabled":
                self._charge_process = env.process(self._manage_charging())

    def _monitor_utilization(self):
        while True:
            self._util_samples.append((self.env.now, self.resource.count))
            yield self.env.timeout(1.0)

    def _manage_charging(self):
        while True:
            yield self.env.timeout(self.charge_interval * 60)
            available_stations = self.charging_stations.capacity
            count = min(self.num_agvs, available_stations)
            if count == 0:
                continue
            requests = [self.charging_stations.request() for _ in range(count)]
            for req in requests:
                yield req
            yield self.env.timeout(self.charge_duration * 60)
            self._charges_completed += count
            self._total_charge_time += self.charge_duration * 60 * count
            for req in requests:
                self.charging_stations.release(req)

    def request(self):
        return self.resource.request() if self.num_agvs > 0 else None

    def calculate_travel_time(self, distance: float) -> float:
        return distance / self.agv_speed

    def get_utilization(self, current_time: float) -> float:
        if self.num_agvs == 0 or current_time == 0 or not self._util_samples:
            return 0.0
        samples = [s for s in self._util_samples if s[0] <= current_time]
        if not samples:
            return 0.0
        total_busy = sum(count for _, count in samples)
        total_possible = len(samples) * self.num_agvs
        return (total_busy / total_possible * 100) if total_possible > 0 else 0.0

    @property
    def available_agvs(self) -> int:
        if self.num_agvs == 0:
            return 0
        return self.num_agvs - self.resource.count
