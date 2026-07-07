import simpy
from src.config import SimulationConfig

class WorkerPool:
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.resource = simpy.Resource(env, capacity=config.num_workers)
        self.total_workers = config.num_workers
        self._util_samples = []
        self._monitor_process = env.process(self._monitor_utilization())

    def _monitor_utilization(self):
        while True:
            self._util_samples.append((self.env.now, self.resource.count))
            yield self.env.timeout(1.0)

    def request(self):
        return self.resource.request()

    def get_utilization(self, current_time: float) -> float:
        if current_time == 0 or not self._util_samples:
            return 0.0
        samples = [s for s in self._util_samples if s[0] <= current_time]
        if not samples:
            return 0.0
        total_busy = sum(count for _, count in samples)
        total_possible = len(samples) * self.total_workers
        return (total_busy / total_possible) * 100 if total_possible > 0 else 0.0

    @property
    def available_workers(self) -> int:
        return self.total_workers - self.resource.count

    @property
    def busy_workers(self) -> int:
        return self.resource.count
