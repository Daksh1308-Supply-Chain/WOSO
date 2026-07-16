import simpy
import random
from typing import List
from src.config import SimulationConfig

class RobotPool:
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.num_robots = config.num_robot_pickers
        self.robot_pick_speed = config.robot_pick_speed
        self.maintenance_interval = config.robot_maintenance_interval
        self.maintenance_duration = config.robot_maintenance_duration

        self._util_samples = []
        self._maintenance_events = 0

        if self.num_robots > 0:
            self.resource = simpy.Resource(env, capacity=self.num_robots)
            self._monitor_process = env.process(self._monitor_utilization())
            if self.maintenance_interval > 0:
                self._maintenance_process = env.process(self._manage_maintenance())

    def _monitor_utilization(self):
        while True:
            self._util_samples.append((self.env.now, self.resource.count))
            yield self.env.timeout(1.0)

    def _manage_maintenance(self):
        while True:
            yield self.env.timeout(self.maintenance_interval * 60)
            count = min(self.num_robots, self.num_robots)
            if count == 0:
                continue
            requests = [self.resource.request() for _ in range(count)]
            for req in requests:
                yield req
            yield self.env.timeout(self.maintenance_duration * 60)
            self._maintenance_events += 1
            for req in requests:
                self.resource.release(req)

    def request(self):
        return self.resource.request() if self.num_robots > 0 else None

    def is_high_volume_product(self, product_id: int) -> bool:
        return product_id <= self.config.robot_high_volume_count

    def order_is_robot_eligible(self, item_ids: List[int]) -> bool:
        if self.num_robots == 0:
            return False
        if self.config.robot_mode == "disabled":
            return False
        if self.config.robot_mode == "all":
            return True
        high_vol = sum(1 for pid in item_ids if self.is_high_volume_product(pid))
        return high_vol > len(item_ids) / 2

    def get_utilization(self, current_time: float) -> float:
        if self.num_robots == 0 or current_time == 0 or not self._util_samples:
            return 0.0
        samples = [s for s in self._util_samples if s[0] <= current_time]
        if not samples:
            return 0.0
        total_busy = sum(count for _, count in samples)
        total_possible = len(samples) * self.num_robots
        return (total_busy / total_possible * 100) if total_possible > 0 else 0.0

    @property
    def available_robots(self) -> int:
        if self.num_robots == 0:
            return 0
        return self.num_robots - self.resource.count
